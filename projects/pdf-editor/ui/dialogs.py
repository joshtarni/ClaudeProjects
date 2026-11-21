from __future__ import annotations

import tkinter as tk
from tkinter import filedialog, messagebox
from pathlib import Path


def open_pdf_dialog(parent: tk.Misc) -> str | None:
    return filedialog.askopenfilename(parent=parent, filetypes=[("PDF files", "*.pdf")])


def save_pdf_dialog(parent: tk.Misc, source: str | None = None) -> str | None:
    initial = None
    if source:
        initial = str(Path(source).with_name(Path(source).stem + "-edited.pdf"))
    return filedialog.asksaveasfilename(
        parent=parent,
        defaultextension=".pdf",
        initialfile=initial,
        filetypes=[("PDF files", "*.pdf")],
    )


def confirm_overwrite(parent: tk.Misc) -> bool:
    return messagebox.askyesno(
        "Confirm overwrite",
        "Overwrite the selected destination? This is destructive.",
        parent=parent,
    )


def show_error(parent: tk.Misc, title: str, message: str) -> None:
    messagebox.showerror(title, message, parent=parent)
