from __future__ import annotations

import tkinter as tk
from tkinter import ttk
import pymupdf


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

        try:
            if hasattr(master, "tk") and "tkdnd::drop_target_register" in master.tk.call("info", "commands"):
                master.tk.call("tkdnd::drop_target_register", master._w, "DND_Files")
                master.bind("<<Drop:DND_Files>>", self._drop_files)
        except tk.TclError:
            pass
        master.bind("<Drop>", self._drop_files)

    def open(self, path: str) -> None:
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
        self.zoom = max(0.25, min(4.0, zoom))
        self.render()

    def previous(self) -> None:
        if self.doc and self.page_index > 0:
            self.page_index -= 1
            self.render()

    def next(self) -> None:
        if self.doc and self.page_index + 1 < self.doc.page_count:
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
            self.page_index = page_number - 1
            self.render()

    def go_to_index(self, page_index: int) -> None:
        if self.doc and 0 <= page_index < self.doc.page_count:
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
        pix = self.doc.load_page(self.page_index).get_pixmap(matrix=pymupdf.Matrix(self.zoom, self.zoom), alpha=False)
        ppm = pix.tobytes("ppm")
        self.photo = tk.PhotoImage(data=ppm)
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor="nw", image=self.photo)
        self.canvas.configure(scrollregion=(0, 0, pix.width, pix.height))
        self.status.configure(text=f"Page {self.page_index + 1} / {self.doc.page_count}")
