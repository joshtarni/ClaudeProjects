from __future__ import annotations

import tkinter as tk
import sys
import os
import tempfile
from pathlib import Path
from tkinter import filedialog, simpledialog, ttk

from core.document import (
    merge_pdfs,
    open_pdf,
    reorder_and_delete,
    save_pdf,
    split_pdf,
)
from core.annotations import (
    add_freehand_annotation,
    add_highlight_annotation,
    add_shape_annotation,
    add_text_annotation,
    add_underline_annotation,
    add_image_watermark,
    add_watermark,
    insert_text,
)
from core.document import rotate_pages
from core.images import insert_image, remove_image_rect, replace_image
from ui.dialogs import open_pdf_dialog, save_pdf_dialog, confirm_overwrite, show_error
from ui.viewer import PdfViewer
from core.security import encrypt_pdf, decrypt_pdf
from core.forms import list_fields, fill_fields
from core.extraction import extract_text, extract_images, export_text


def parse_float(value: str, label: str, minimum: float = 0.0) -> float:
    try:
        result = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{label} must be a number") from exc
    if result < minimum:
        raise ValueError(f"{label} must be at least {minimum}")
    return result


def parse_rect(value: str) -> tuple[float, float, float, float]:
    parts = [part.strip() for part in value.split(",")]
    if len(parts) != 4:
        raise ValueError("Rectangle must use x0,y0,x1,y1")
    x0 = parse_float(parts[0], "x0")
    y0 = parse_float(parts[1], "y0")
    x1 = parse_float(parts[2], "x1")
    y1 = parse_float(parts[3], "y1")
    if x1 <= x0 or y1 <= y0:
        raise ValueError("Rectangle width and height must be greater than zero")
    return x0, y0, x1, y1


def parse_color(value: str) -> tuple[float, float, float]:
    parts = [part.strip() for part in value.split(",")]
    if len(parts) != 3:
        raise ValueError("Color must use red,green,blue values from 0 to 1")
    color = tuple(parse_float(part, "Color component") for part in parts)
    if any(component > 1 for component in color):
        raise ValueError("Color components must be from 0 to 1")
    return color


def parse_quads(value: str) -> list[tuple[float, float, float, float]]:
    if not value.strip():
        raise ValueError("At least one annotation rectangle is required")
    return [parse_rect(rect.strip()) for rect in value.split(";")]


def parse_points(value: str) -> list[tuple[float, float]]:
    points: list[tuple[float, float]] = []
    if not value.strip():
        raise ValueError("At least one freehand point is required")
    for point in value.split(";"):
        parts = [part.strip() for part in point.split(",")]
        if len(parts) != 2:
            raise ValueError("Freehand points must use x,y")
        points.append((parse_float(parts[0], "x"), parse_float(parts[1], "y")))
    return points


class MainWindow(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("PDF Editor")
        self.geometry("1100x760")
        self.source: str | None = None
        self.working: str | None = None
        self._working_temp: str | None = None
        self.protocol("WM_DELETE_WINDOW", self.on_close)

        toolbar = ttk.Frame(self)
        toolbar.pack(fill="x")
        ttk.Button(toolbar, text="Open", command=self.open_document).pack(side="left")
        ttk.Button(toolbar, text="Save As", command=self.save_as).pack(side="left")
        ttk.Button(toolbar, text="Merge", command=self.merge_documents).pack(side="left")
        ttk.Button(toolbar, text="Split", command=self.split_document).pack(side="left")
        ttk.Button(toolbar, text="Reorder/Delete", command=self.reorder_delete_pages).pack(side="left")
        ttk.Button(toolbar, text="Text", command=self.insert_text).pack(side="left")
        ttk.Button(toolbar, text="Comment", command=self.add_comment).pack(side="left")
        ttk.Button(toolbar, text="Highlight", command=self.add_highlight).pack(side="left")
        ttk.Button(toolbar, text="Underline", command=self.add_underline).pack(side="left")
        ttk.Button(toolbar, text="Shape", command=self.add_shape).pack(side="left")
        ttk.Button(toolbar, text="Freehand", command=self.add_freehand).pack(side="left")
        ttk.Button(toolbar, text="Insert Image", command=self.insert_image).pack(side="left")
        ttk.Button(toolbar, text="Replace Image", command=self.replace_image).pack(side="left")
        ttk.Button(toolbar, text="Remove Image", command=self.remove_image).pack(side="left")
        ttk.Button(toolbar, text="Rotate", command=self.rotate_page).pack(side="left")
        ttk.Button(toolbar, text="Help/About", command=self.show_about).pack(side="right")

        second_toolbar = ttk.Frame(self)
        second_toolbar.pack(fill="x")
        ttk.Button(second_toolbar, text="Encrypt", command=self.encrypt_document).pack(side="left")
        ttk.Button(second_toolbar, text="Decrypt", command=self.decrypt_document).pack(side="left")
        ttk.Button(second_toolbar, text="Fill Forms", command=self.fill_forms).pack(side="left")
        ttk.Button(second_toolbar, text="Extract Text", command=self.extract_text).pack(side="left")
        ttk.Button(second_toolbar, text="Extract Images", command=self.extract_images).pack(side="left")
        ttk.Button(second_toolbar, text="Watermark", command=self.add_watermark).pack(side="left")

        self.viewer = PdfViewer(self)
        self.viewer.pack(fill="both", expand=True)

    def _clear_working_temp(self) -> None:
        if self._working_temp:
            try:
                os.unlink(self._working_temp)
            except FileNotFoundError:
                pass
            self._working_temp = None

    def open_document_path(self, path: str) -> None:
        try:
            doc = open_pdf(path)
            doc.close()
            self._clear_working_temp()
            self.source = path
            self.working = path
            self.viewer.open(path)
        except Exception as exc:
            if "Password required" not in str(exc):
                show_error(self, "Cannot open PDF", str(exc))
                return
            password = simpledialog.askstring(
                "Password required",
                "Enter the PDF user or owner password:",
                show="*",
                parent=self,
            )
            if password is None:
                return
            try:
                doc = open_pdf(path, password)
                fd, temp_path = tempfile.mkstemp(prefix="pdf-editor-open-", suffix=".pdf")
                os.close(fd)
                try:
                    doc.save(temp_path, garbage=4, deflate=True)
                    doc.close()
                except Exception:
                    if not doc.is_closed:
                        doc.close()
                    try:
                        os.unlink(temp_path)
                    except FileNotFoundError:
                        pass
                    raise
                self._clear_working_temp()
                self.source = path
                self.working = temp_path
                self._working_temp = temp_path
                self.viewer.open(temp_path)
            except Exception as password_exc:
                show_error(self, "Cannot open PDF", str(password_exc))

    def open_document(self) -> None:
        path = open_pdf_dialog(self)
        if not path:
            return
        self.open_document_path(path)

    def save_as(self) -> None:
        if not self.source or not self.working:
            show_error(self, "No document", "Open a PDF before saving.")
            return
        destination = save_pdf_dialog(self, self.source)
        if not destination:
            return
        destination_path = Path(destination)
        source_path = Path(self.source)
        overwrite = destination_path.resolve() == source_path.resolve()
        if destination_path.exists() and not overwrite:
            overwrite = confirm_overwrite(self)
            if not overwrite:
                return
        elif overwrite:
            overwrite = confirm_overwrite(self)
            if not overwrite:
                return
        try:
            saved = save_pdf(self.working, destination_path, overwrite=overwrite)
            tk.messagebox.showinfo(
                "Saved",
                f"Saved PDF as:\n{saved}",
                parent=self,
            )
        except Exception as exc:
            show_error(self, "Cannot save PDF", str(exc))

    def _operation_output(self, label: str) -> str:
        if not self.working:
            raise ValueError("Open a PDF before editing")
        source = Path(self.working)
        return str(source.with_name(f"{source.stem}-{label}-edited.pdf"))

    def _confirm_destination(self, destination: str) -> bool:
        path = Path(destination)
        if path.exists():
            return confirm_overwrite(self)
        if self.source:
            try:
                if path.resolve() == Path(self.source).resolve():
                    return confirm_overwrite(self)
            except OSError:
                pass
        return True

    def _run_operation(self, operation, label: str) -> None:
        if not self.working:
            show_error(self, "No document", "Open a PDF before editing.")
            return
        try:
            output_path = Path(self._operation_output(label))
            overwrite = False
            if output_path.exists():
                overwrite = confirm_overwrite(self)
                if not overwrite:
                    return
            output = operation(str(output_path), overwrite)
            if output:
                self.working = str(output)
                self.viewer.open(self.working)
        except Exception as exc:
            show_error(self, "Operation failed", str(exc))

    def _select_rect_for_operation(self, title: str, operation) -> None:
        if not self.working:
            show_error(self, "No document", "Open a PDF before editing.")
            return
        self.viewer.start_rect_selection(operation)

    def insert_text(self) -> None:
        text = simpledialog.askstring("Insert text", "Text:", parent=self)
        if not text:
            return
        try:
            font_size = parse_float(simpledialog.askstring(
                "Text size",
                "Font size:",
                initialvalue="12",
                parent=self,
            ) or "12", "Font size", minimum=1)
            color = parse_color(simpledialog.askstring(
                "Text color",
                "RGB components 0-1:",
                initialvalue="0,0,0",
                parent=self,
            ) or "")
            font_name = (simpledialog.askstring(
                "Text font",
                "Font name: helv or cour",
                initialvalue="helv",
                parent=self,
            ) or "helv").strip().lower()
            if font_name not in {"helv", "cour"}:
                raise ValueError("Font must be helv or cour")
        except ValueError as exc:
            show_error(self, "Invalid text parameters", str(exc))
            return

        def after_selection(rect: tuple[float, float, float, float]) -> None:
            def selected_operation(output: str, overwrite: bool = False) -> str:
                return insert_text(
                    self.working, self.viewer.page_index, text, rect,
                    font_size=font_size,
                    color=color,
                    font_name=font_name,
                    output=output,
                    overwrite=overwrite,
                )
            self._run_operation(selected_operation, "text")

        self._select_rect_for_operation("Select text bounds", after_selection)

    def add_comment(self) -> None:
        text = simpledialog.askstring("Add comment", "Comment:", parent=self)
        author = simpledialog.askstring("Add comment", "Author:", parent=self) or ""
        if not text:
            return
        def after_selection(rect: tuple[float, float, float, float]) -> None:
            def operation(output: str, overwrite: bool = False) -> str:
                return add_text_annotation(
                    self.working, self.viewer.page_index, rect, text, author,
                    output=output, overwrite=overwrite,
                )
            self._run_operation(operation, "comment")
        self._select_rect_for_operation("Select comment bounds", after_selection)

    def add_highlight(self) -> None:
        try:
            author = simpledialog.askstring("Highlight", "Author:", parent=self) or ""
            color = parse_color(simpledialog.askstring(
                "Highlight color", "RGB components 0-1:", initialvalue="1,1,0", parent=self,
            ) or "")
            opacity = parse_float(simpledialog.askstring(
                "Highlight opacity", "Opacity 0-1:", initialvalue="0.5", parent=self,
            ) or "", "Opacity")
            if opacity > 1:
                raise ValueError("Opacity must be from 0 to 1")
        except ValueError as exc:
            show_error(self, "Invalid highlight parameters", str(exc))
            return

        def after_selection(rect: tuple[float, float, float, float]) -> None:
            def operation(output: str, overwrite: bool = False) -> str:
                return add_highlight_annotation(
                    self.working, self.viewer.page_index, [rect], author,
                    color=color, opacity=opacity, output=output, overwrite=overwrite,
                )
            self._run_operation(operation, "highlight")
        self._select_rect_for_operation("Select highlight region", after_selection)

    def add_underline(self) -> None:
        try:
            author = simpledialog.askstring("Underline", "Author:", parent=self) or ""
            color = parse_color(simpledialog.askstring(
                "Underline color", "RGB components 0-1:", initialvalue="0,0,1", parent=self,
            ) or "")
            opacity = parse_float(simpledialog.askstring(
                "Underline opacity", "Opacity 0-1:", initialvalue="1", parent=self,
            ) or "", "Opacity")
            if opacity > 1:
                raise ValueError("Opacity must be from 0 to 1")
        except ValueError as exc:
            show_error(self, "Invalid underline parameters", str(exc))
            return

        def after_selection(rect: tuple[float, float, float, float]) -> None:
            def operation(output: str, overwrite: bool = False) -> str:
                return add_underline_annotation(
                    self.working, self.viewer.page_index, [rect], author,
                    color=color, opacity=opacity, output=output, overwrite=overwrite,
                )
            self._run_operation(operation, "underline")
        self._select_rect_for_operation("Select underline region", after_selection)

    def add_shape(self) -> None:
        try:
            author = simpledialog.askstring("Shape", "Author:", parent=self) or ""
            color = parse_color(simpledialog.askstring(
                "Shape color", "RGB components 0-1:", initialvalue="1,0,0", parent=self,
            ) or "")
            width = parse_float(simpledialog.askstring(
                "Shape stroke", "Stroke width:", initialvalue="1", parent=self,
            ) or "", "Stroke width", minimum=0.1)
        except ValueError as exc:
            show_error(self, "Invalid shape parameters", str(exc))
            return

        def after_selection(rect: tuple[float, float, float, float]) -> None:
            def operation(output: str, overwrite: bool = False) -> str:
                return add_shape_annotation(
                    self.working, self.viewer.page_index, rect, author,
                    color=color, width=width, output=output, overwrite=overwrite,
                )
            self._run_operation(operation, "shape")
        self._select_rect_for_operation("Select shape bounds", after_selection)

    def add_freehand(self) -> None:
        try:
            author = simpledialog.askstring("Freehand", "Author:", parent=self) or ""
            color = parse_color(simpledialog.askstring(
                "Freehand color", "RGB components 0-1:", initialvalue="1,0,0", parent=self,
            ) or "")
            width = parse_float(simpledialog.askstring(
                "Freehand stroke", "Stroke width:", initialvalue="1", parent=self,
            ) or "", "Stroke width", minimum=0.1)
        except ValueError as exc:
            show_error(self, "Invalid freehand parameters", str(exc))
            return

        def after_selection(points: list[tuple[float, float]]) -> None:
            def operation(output: str, overwrite: bool = False) -> str:
                return add_freehand_annotation(
                    self.working, self.viewer.page_index, points, author,
                    color=color, width=width, output=output, overwrite=overwrite,
                )
            self._run_operation(operation, "freehand")
        if not self.working:
            show_error(self, "No document", "Open a PDF before editing.")
            return
        self.viewer.start_freehand_selection(after_selection)

    def insert_image(self) -> None:
        image_path = filedialog.askopenfilename(
            parent=self,
            filetypes=[("Image files", "*.png *.jpg *.jpeg")],
        )
        if not image_path:
            return
        def after_selection(rect: tuple[float, float, float, float]) -> None:
            def operation(output: str, overwrite: bool = False) -> str:
                insert_image(
                    self.working,
                    output,
                    self.viewer.page_index,
                    image_path,
                    rect,
                    overwrite=overwrite,
                )
                return output
            self._run_operation(operation, "image")
        self._select_rect_for_operation("Select image bounds", after_selection)

    def replace_image(self) -> None:
        image_path = filedialog.askopenfilename(
            parent=self,
            filetypes=[("Image files", "*.png *.jpg *.jpeg")],
        )
        if not image_path:
            return
        def after_selection(rect: tuple[float, float, float, float]) -> None:
            def operation(output: str, overwrite: bool = False) -> str:
                replace_image(
                    self.working,
                    output,
                    self.viewer.page_index,
                    rect,
                    image_path,
                    overwrite=overwrite,
                )
                return output
            self._run_operation(operation, "replace")
        self._select_rect_for_operation("Select replacement bounds", after_selection)

    def remove_image(self) -> None:
        def after_selection(rect: tuple[float, float, float, float]) -> None:
            def operation(output: str, overwrite: bool = False) -> str:
                remove_image_rect(
                    self.working,
                    output,
                    self.viewer.page_index,
                    rect,
                    overwrite=overwrite,
                )
                return output
            self._run_operation(operation, "remove-image")
        self._select_rect_for_operation("Select image removal bounds", after_selection)

    def rotate_page(self) -> None:
        def operation(output: str, overwrite: bool = False) -> str:
            rotate_pages(
                self.working,
                output,
                [self.viewer.page_index],
                90,
                overwrite=overwrite,
            )
            return output

        self._run_operation(operation, "rotate")

    def merge_documents(self) -> None:
        paths = filedialog.askopenfilenames(
            parent=self,
            filetypes=[("PDF files", "*.pdf")],
            title="Select PDFs to merge",
        )
        if len(paths) < 2:
            show_error(self, "Merge failed", "Select at least two PDF files.")
            return
        destination = save_pdf_dialog(self)
        if not destination:
            return
        overwrite = False
        if Path(destination).exists():
            overwrite = confirm_overwrite(self)
            if not overwrite:
                return
        try:
            merge_pdfs(paths, destination, overwrite=overwrite)
            tk.messagebox.showinfo("Merged", f"Merged PDF saved as:\n{destination}", parent=self)
        except Exception as exc:
            show_error(self, "Merge failed", str(exc))

    def split_document(self) -> None:
        if not self.working:
            show_error(self, "No document", "Open a PDF before splitting.")
            return
        expression = simpledialog.askstring(
            "Split PDF",
            "Page ranges (for example 1-3,5,9-12):",
            parent=self,
        )
        if not expression:
            return
        output_dir = filedialog.askdirectory(parent=self, title="Select split output directory")
        if not output_dir:
            return
        separate = tk.messagebox.askyesno(
            "Separate outputs",
            "Create one file per page expression?",
            parent=self,
        )
        try:
            outputs = split_pdf(self.working, expression, output_dir, separate=separate)
            names = "\n".join(str(path) for path in outputs)
            tk.messagebox.showinfo("Split complete", f"Created:\n{names}", parent=self)
        except Exception as exc:
            show_error(self, "Split failed", str(exc))

    def reorder_delete_pages(self) -> None:
        if not self.working:
            show_error(self, "No document", "Open a PDF before changing pages.")
            return
        sequence = simpledialog.askstring(
            "Reorder or delete pages",
            "Enter final page order using one-based numbers (for example 4,2,1):",
            parent=self,
        )
        if not sequence:
            return
        try:
            page_order = [int(item.strip()) - 1 for item in sequence.split(",")]
        except ValueError:
            show_error(self, "Invalid page order", "Use comma-separated one-based page numbers.")
            return
        destination = save_pdf_dialog(self)
        if not destination:
            return
        overwrite = False
        if Path(destination).exists():
            overwrite = confirm_overwrite(self)
            if not overwrite:
                return
        try:
            reorder_and_delete(self.working, destination, page_order, overwrite=overwrite)
            tk.messagebox.showinfo("Pages updated", f"Saved updated PDF as:\n{destination}", parent=self)
        except Exception as exc:
            show_error(self, "Page update failed", str(exc))

    def encrypt_document(self) -> None:
        if not self.working:
            show_error(self, "No document", "Open a PDF before encryption.")
            return
        owner = simpledialog.askstring("Encrypt PDF", "Owner password (at least 12 characters):", show="*", parent=self)
        user = simpledialog.askstring("Encrypt PDF", "User password (at least 12 characters):", show="*", parent=self)
        if owner is None or user is None:
            return
        destination = save_pdf_dialog(self)
        if not destination:
            return
        overwrite = False
        if Path(destination).exists():
            overwrite = confirm_overwrite(self)
            if not overwrite:
                return
        try:
            encrypt_pdf(self.working, destination, owner, user, overwrite=overwrite)
            tk.messagebox.showinfo("Encrypted", f"Encrypted PDF saved as:\n{destination}", parent=self)
        except Exception as exc:
            show_error(self, "Encryption failed", str(exc))
        finally:
            owner = ""
            user = ""

    def decrypt_document(self) -> None:
        if not self.working:
            show_error(self, "No document", "Open a PDF before decryption.")
            return
        owner = simpledialog.askstring("Decrypt PDF", "Owner password:", show="*", parent=self)
        if owner is None:
            return
        destination = save_pdf_dialog(self)
        if not destination:
            return
        overwrite = False
        if Path(destination).exists():
            overwrite = confirm_overwrite(self)
            if not overwrite:
                return
        try:
            decrypt_pdf(self.working, destination, owner, overwrite=overwrite)
            tk.messagebox.showinfo("Decrypted", f"Decrypted PDF saved as:\n{destination}", parent=self)
        except Exception as exc:
            show_error(self, "Decryption failed", str(exc))
        finally:
            owner = ""

    def fill_forms(self) -> None:
        if not self.working:
            show_error(self, "No document", "Open a PDF before filling forms.")
            return
        try:
            fields = list_fields(self.working)
        except Exception as exc:
            show_error(self, "Form read failed", str(exc))
            return
        if not fields:
            show_error(self, "No form fields", "This PDF contains no supported form fields.")
            return
        assignments = simpledialog.askstring(
            "Fill form fields",
            "Enter name=value pairs separated by commas:\n" + ", ".join(name or "<unnamed>" for name, _ in fields),
            parent=self,
        )
        if not assignments:
            return
        values: dict[str, str] = {}
        for assignment in assignments.split(","):
            if "=" not in assignment:
                show_error(self, "Invalid form values", "Use name=value assignments.")
                return
            name, value = assignment.split("=", 1)
            values[name.strip()] = value.strip()
        destination = save_pdf_dialog(self)
        if not destination:
            return
        overwrite = False
        if Path(destination).exists():
            overwrite = confirm_overwrite(self)
            if not overwrite:
                return
        try:
            unsupported = fill_fields(self.working, destination, values, overwrite=overwrite)
            message = f"Form-filled PDF saved as:\n{destination}"
            if unsupported:
                message += "\nUnsupported fields: " + ", ".join(unsupported)
            tk.messagebox.showinfo("Forms updated", message, parent=self)
        except Exception as exc:
            show_error(self, "Form update failed", str(exc))

    def extract_text(self) -> None:
        if not self.working:
            show_error(self, "No document", "Open a PDF before extracting text.")
            return
        destination = filedialog.asksaveasfilename(
            parent=self,
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt")],
        )
        if not destination:
            return
        overwrite = False
        if Path(destination).exists():
            overwrite = confirm_overwrite(self)
            if not overwrite:
                return
        try:
            text = extract_text(self.working, [self.viewer.page_index])
            if not text.strip():
                show_error(self, "No extractable text", "No text was found on the selected page.")
                return
            export_text(text, destination, overwrite=overwrite)
            tk.messagebox.showinfo("Text extracted", f"Text saved as:\n{destination}", parent=self)
        except Exception as exc:
            show_error(self, "Text extraction failed", str(exc))

    def extract_images(self) -> None:
        if not self.working:
            show_error(self, "No document", "Open a PDF before extracting images.")
            return
        output_dir = filedialog.askdirectory(parent=self, title="Select image output directory")
        if not output_dir:
            return
        try:
            existing_targets = list(Path(output_dir).glob("page-*-image-*.png"))
            overwrite = False
            if existing_targets:
                overwrite = confirm_overwrite(self)
                if not overwrite:
                    return
            outputs = extract_images(
                self.working,
                output_dir,
                [self.viewer.page_index],
                overwrite=overwrite,
            )
            if not outputs:
                show_error(self, "No extractable images", "No images were found on the selected page.")
                return
            tk.messagebox.showinfo(
                "Images extracted",
                "Extracted:\n" + "\n".join(str(path) for path in outputs),
                parent=self,
            )
        except Exception as exc:
            show_error(self, "Image extraction failed", str(exc))

    def add_watermark(self) -> None:
        if not self.working:
            show_error(self, "No document", "Open a PDF before adding a watermark.")
            return
        kind = tk.messagebox.askyesno(
            "Watermark type",
            "Yes for text watermark; No for image watermark.",
            parent=self,
        )
        destination = save_pdf_dialog(self)
        if not destination:
            return
        overwrite = False
        destination_path = Path(destination)
        source_collision = False
        if self.source:
            try:
                source_collision = destination_path.resolve() == Path(self.source).resolve()
            except OSError:
                source_collision = False
        if destination_path.exists() or source_collision:
            overwrite = confirm_overwrite(self)
            if not overwrite:
                return
        scope = simpledialog.askstring(
            "Watermark pages",
            "Scope: all, odd, even, or selected",
            initialvalue="all",
            parent=self,
        )
        scope = (scope or "all").strip().lower()
        if scope not in {"all", "odd", "even", "selected"}:
            show_error(self, "Invalid watermark scope", "Use all, odd, even, or selected.")
            return
        selected = None
        if scope == "selected":
            selected = simpledialog.askstring(
                "Selected pages",
                "One-based comma-separated page numbers:",
                parent=self,
            )
            if not selected:
                return
        try:
            if kind:
                text = simpledialog.askstring("Text watermark", "Watermark text:", parent=self)
                if not text:
                    return
                add_watermark(self.working, destination, text, scope, selected, overwrite=overwrite)
            else:
                image_path = filedialog.askopenfilename(
                    parent=self,
                    filetypes=[("Image files", "*.png *.jpg *.jpeg")],
                )
                if not image_path:
                    return
                add_image_watermark(
                    self.working,
                    destination,
                    image_path,
                    scope,
                    selected,
                    overwrite=overwrite,
                )
            tk.messagebox.showinfo("Watermark added", f"Saved as:\n{destination}", parent=self)
        except Exception as exc:
            show_error(self, "Watermark failed", str(exc))

    def show_about(self) -> None:
        notice_path = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parents[1])) / "THIRD_PARTY_NOTICES.md"
        tk.messagebox.showinfo(
            "About PDF Editor",
            "PDF Editor 1.0.0\n"
            "Local offline PDF editing\n"
            f"Third-party notices: {notice_path}",
            parent=self,
        )

    def on_close(self) -> None:
        self.viewer.close()
        self._clear_working_temp()
        super().destroy()
