from __future__ import annotations

import tkinter as tk
from tkinter import ttk
import pymupdf


def canvas_point_to_pdf(
    canvas_x: float,
    canvas_y: float,
    zoom: float,
) -> tuple[float, float]:
    """Map a Tk canvas point to PDF page points at the current zoom."""
    if zoom <= 0:
        raise ValueError("zoom must be greater than zero")
    return canvas_x / zoom, canvas_y / zoom


def canvas_rect_to_pdf(
    start_x: float,
    start_y: float,
    end_x: float,
    end_y: float,
    zoom: float,
) -> tuple[float, float, float, float]:
    x0, y0 = canvas_point_to_pdf(min(start_x, end_x), min(start_y, end_y), zoom)
    x1, y1 = canvas_point_to_pdf(max(start_x, end_x), max(start_y, end_y), zoom)
    return x0, y0, x1, y1


def rendered_point_to_pdf(
    canvas_x: float,
    canvas_y: float,
    page_rect: pymupdf.Rect,
    rendered_width: float,
    rendered_height: float,
) -> tuple[float, float]:
    if rendered_width <= 0 or rendered_height <= 0:
        raise ValueError("rendered page dimensions must be greater than zero")
    x = min(max(canvas_x, 0), rendered_width)
    y = min(max(canvas_y, 0), rendered_height)
    pdf_x = page_rect.x0 + (x / rendered_width) * page_rect.width
    pdf_y = page_rect.y0 + (y / rendered_height) * page_rect.height
    return pdf_x, pdf_y


def rendered_rect_to_pdf(
    start_x: float,
    start_y: float,
    end_x: float,
    end_y: float,
    page_rect: pymupdf.Rect,
    rendered_width: float,
    rendered_height: float,
) -> tuple[float, float, float, float]:
    x0, y0 = rendered_point_to_pdf(start_x, start_y, page_rect, rendered_width, rendered_height)
    x1, y1 = rendered_point_to_pdf(end_x, end_y, page_rect, rendered_width, rendered_height)
    return (
        min(x0, x1),
        min(y0, y1),
        max(x0, x1),
        max(y0, y1),
    )


def bind_drop_target(master: tk.Misc, callback) -> None:
    try:
        if hasattr(master, "tk") and "tkdnd::drop_target_register" in master.tk.call("info", "commands"):
            master.tk.call("tkdnd::drop_target_register", master._w, "DND_Files")
            master.bind("<<Drop:DND_Files>>", callback)
    except tk.TclError:
        pass

    try:
        master.bind("<Drop>", callback)
    except tk.TclError:
        pass


class PdfViewer(ttk.Frame):
    def __init__(self, master: tk.Misc) -> None:
        super().__init__(master)
        self.doc: pymupdf.Document | None = None
        self.page_index = 0
        self.zoom = 1.0
        sidebar = ttk.Frame(self, width=150)
        sidebar.pack(side="left", fill="y")
        ttk.Label(sidebar, text="Pages").pack()
        self.thumbnail_canvas = tk.Canvas(sidebar, width=150, background="#ddd")
        scrollbar = ttk.Scrollbar(sidebar, orient="vertical", command=self.thumbnail_canvas.yview)
        self.thumbnail_canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.thumbnail_canvas.pack(side="left", fill="y", expand=True)

        self.canvas = tk.Canvas(self, background="#444")
        self.canvas.pack(fill="both", expand=True)
        controls = ttk.Frame(self)
        controls.pack(fill="x")
        ttk.Button(controls, text="Previous", command=self.previous).pack(side="left")
        ttk.Button(controls, text="Next", command=self.next).pack(side="left")
        ttk.Label(controls, text="Page").pack(side="left")
        self.page_entry = ttk.Entry(controls, width=6)
        self.page_entry.pack(side="left")
        ttk.Button(controls, text="Go", command=self.go_to_page).pack(side="left")
        ttk.Button(controls, text="Zoom -", command=lambda: self.set_zoom(self.zoom / 1.2)).pack(side="left")
        ttk.Button(controls, text="+", command=lambda: self.set_zoom(self.zoom * 1.2)).pack(side="left")
        self.status = ttk.Label(controls, text="")
        self.status.pack(side="right")
        self.thumbnail_items: list[int] = []
        self._selection_item: int | None = None
        self._selection_start: tuple[float, float] | None = None
        self._selection_points: list[tuple[float, float]] = []
        self._selection_callback = None
        self._selection_kind: str | None = None
        self._selection_page_index: int | None = None
        self._rendered_width = 0
        self._rendered_height = 0

        bind_drop_target(master, self._drop_files)

    def cancel_selection(self, _event: tk.Event | None = None) -> str:
        self.canvas.unbind("<Button-1>")
        self.canvas.unbind("<B1-Motion>")
        self.canvas.unbind("<ButtonRelease-1>")
        self.canvas.unbind("<Escape>")
        self.canvas.unbind("<Button-3>")
        if self._selection_item is not None:
            self.canvas.delete(self._selection_item)
        self._selection_item = None
        self._selection_start = None
        self._selection_points = []
        self._selection_callback = None
        self._selection_kind = None
        self._selection_page_index = None
        self.status.configure(text=f"Page {self.page_index + 1} / {self.doc.page_count}" if self.doc else "")
        return "break"

    def start_rect_selection(self, callback) -> None:
        if not self.doc:
            return
        self.cancel_selection()
        self._selection_kind = "rect"
        self._selection_callback = callback
        self._selection_page_index = self.page_index
        self.status.configure(text="Drag a rectangle; right-click or Escape cancels")
        self.canvas.bind("<Button-1>", self._rect_selection_start)
        self.canvas.bind("<B1-Motion>", self._rect_selection_move)
        self.canvas.bind("<ButtonRelease-1>", self._rect_selection_finish)
        self.canvas.bind("<Escape>", self.cancel_selection)
        self.canvas.bind("<Button-3>", self.cancel_selection)
        self.canvas.focus_set()

    def _canvas_event_point(self, event: tk.Event) -> tuple[float, float]:
        x = float(self.canvas.canvasx(event.x))
        y = float(self.canvas.canvasy(event.y))
        return x, y

    def _rect_selection_start(self, event: tk.Event) -> str:
        self._selection_start = self._canvas_event_point(event)
        if self._selection_item is not None:
            self.canvas.delete(self._selection_item)
        x, y = self._selection_start
        self._selection_item = self.canvas.create_rectangle(
            x, y, x, y, outline="#ff3333", width=2,
        )
        return "break"

    def _rect_selection_move(self, event: tk.Event) -> str:
        if self._selection_start is None or self._selection_item is None:
            return "break"
        x, y = self._canvas_event_point(event)
        start_x, start_y = self._selection_start
        self.canvas.coords(self._selection_item, start_x, start_y, x, y)
        return "break"

    def _rect_selection_finish(self, event: tk.Event) -> str:
        if self._selection_start is None or self._selection_callback is None:
            return "break"
        if self._selection_page_index != self.page_index:
            return self.cancel_selection()
        end_x, end_y = self._canvas_event_point(event)
        start_x, start_y = self._selection_start
        rect = rendered_rect_to_pdf(
            start_x,
            start_y,
            end_x,
            end_y,
            self.doc.load_page(self.page_index).rect,
            self._rendered_width,
            self._rendered_height,
        )
        if rect[2] - rect[0] < 1 or rect[3] - rect[1] < 1:
            return self.cancel_selection()
        callback = self._selection_callback
        self.cancel_selection()
        callback(rect)
        return "break"

    def start_freehand_selection(self, callback) -> None:
        if not self.doc:
            return
        self.cancel_selection()
        self._selection_kind = "freehand"
        self._selection_callback = callback
        self._selection_page_index = self.page_index
        self.status.configure(text="Draw a path; right-click or Escape cancels")
        self.canvas.bind("<Button-1>", self._freehand_selection_start)
        self.canvas.bind("<B1-Motion>", self._freehand_selection_move)
        self.canvas.bind("<ButtonRelease-1>", self._freehand_selection_finish)
        self.canvas.bind("<Escape>", self.cancel_selection)
        self.canvas.bind("<Button-3>", self.cancel_selection)
        self.canvas.focus_set()

    def _freehand_selection_start(self, event: tk.Event) -> str:
        x, y = self._canvas_event_point(event)
        point = rendered_point_to_pdf(
            x,
            y,
            self.doc.load_page(self.page_index).rect,
            self._rendered_width,
            self._rendered_height,
        )
        self._selection_points = [point]
        if self._selection_item is not None:
            self.canvas.delete(self._selection_item)
        self._selection_item = self.canvas.create_line(
            x, y, x, y, fill="#ff3333", width=2,
        )
        return "break"

    def _freehand_selection_move(self, event: tk.Event) -> str:
        if self._selection_item is None:
            return "break"
        if self._selection_page_index != self.page_index:
            return self.cancel_selection()
        x, y = self._canvas_event_point(event)
        pdf_point = rendered_point_to_pdf(
            x,
            y,
            self.doc.load_page(self.page_index).rect,
            self._rendered_width,
            self._rendered_height,
        )
        if pdf_point != self._selection_points[-1]:
            self._selection_points.append(pdf_point)
        coords = self.canvas.coords(self._selection_item)
        coords.extend((x, y))
        self.canvas.coords(self._selection_item, *coords)
        return "break"

    def _freehand_selection_finish(self, _event: tk.Event) -> str:
        if len(self._selection_points) < 2 or self._selection_callback is None:
            return self.cancel_selection()
        if self._selection_page_index != self.page_index:
            return self.cancel_selection()
        callback = self._selection_callback
        points = list(self._selection_points)
        self.cancel_selection()
        callback(points)
        return "break"

    def open(self, path: str) -> None:
        self.cancel_selection()
        if self.doc is not None:
            self.doc.close()
        self.doc = pymupdf.open(path)
        self.page_index = 0
        self.render()
        self.render_thumbnails()

    def close(self) -> None:
        if self.doc is not None:
            self.doc.close()
            self.doc = None

    def set_zoom(self, zoom: float) -> None:
        self.cancel_selection()
        self.zoom = max(0.25, min(4.0, zoom))
        self.render()

    def previous(self) -> None:
        if self.doc and self.page_index > 0:
            self.cancel_selection()
            self.page_index -= 1
            self.render()

    def next(self) -> None:
        if self.doc and self.page_index + 1 < self.doc.page_count:
            self.cancel_selection()
            self.page_index += 1
            self.render()

    def go_to_page(self) -> None:
        if not self.doc:
            return
        try:
            page_number = int(self.page_entry.get())
        except ValueError:
            return
        if 1 <= page_number <= self.doc.page_count:
            self.cancel_selection()
            self.page_index = page_number - 1
            self.render()

    def go_to_index(self, page_index: int) -> None:
        if self.doc and 0 <= page_index < self.doc.page_count:
            self.cancel_selection()
            self.page_index = page_index
            self.render()

    def _drop_files(self, event: tk.Event) -> str:
        data = getattr(event, "data", "")
        if not data:
            return "break"
        path = data.strip().strip("{}")
        callback = getattr(self.master, "open_document_path", None)
        if callback and path.lower().endswith(".pdf"):
            callback(path)
        return "break"

    def render_thumbnails(self) -> None:
        if not self.doc:
            return
        self.thumbnail_canvas.delete("all")
        self.thumbnail_items = []
        y = 10
        for index in range(self.doc.page_count):
            pix = self.doc.load_page(index).get_pixmap(matrix=pymupdf.Matrix(0.15, 0.15), alpha=False)
            photo = tk.PhotoImage(data=pix.tobytes("ppm"))
            self.thumbnail_items.append(photo)
            item = self.thumbnail_canvas.create_image(75, y, anchor="n", image=photo)
            self.thumbnail_canvas.create_text(75, y + 110, text=str(index + 1), anchor="n")
            self.thumbnail_canvas.tag_bind(item, "<Button-1>", lambda _event, i=index: self.go_to_index(i))
            y += 130
        self.thumbnail_canvas.configure(scrollregion=(0, 0, 150, y))

    def render(self) -> None:
        if not self.doc:
            return
        if self._selection_callback is not None:
            self.cancel_selection()
        pix = self.doc.load_page(self.page_index).get_pixmap(matrix=pymupdf.Matrix(self.zoom, self.zoom), alpha=False)
        self._rendered_width = pix.width
        self._rendered_height = pix.height
        ppm = pix.tobytes("ppm")
        self.photo = tk.PhotoImage(data=ppm)
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor="nw", image=self.photo)
        self.canvas.configure(scrollregion=(0, 0, pix.width, pix.height))
        self.status.configure(text=f"Page {self.page_index + 1} / {self.doc.page_count}")
