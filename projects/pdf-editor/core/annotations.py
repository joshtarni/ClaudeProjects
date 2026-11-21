from __future__ import annotations

import pymupdf
from datetime import datetime, timezone
from pathlib import Path

from core.document import save_atomic


def _default_output(path: str) -> str:
    source = Path(path)
    return str(source.with_name(f"{source.stem}-edited{source.suffix}"))


def _set_annotation_metadata(
    annot: pymupdf.Annot,
    author: str,
    content: str = "",
) -> None:
    now = datetime.now(timezone.utc).strftime("D:%Y%m%d%H%M%SZ")
    info = {"title": author, "content": content}
    annot.set_info(info)
    if hasattr(annot, "set_creation_date"):
        annot.set_creation_date(now)
    if hasattr(annot, "set_mod_date"):
        annot.set_mod_date(now)
    annot.update()


def _make_quads(
    quads: list[tuple[float, float, float, float]],
) -> list[pymupdf.Quad]:
    return [
        pymupdf.Quad(
            pymupdf.Point(x0, y0),
            pymupdf.Point(x1, y0),
            pymupdf.Point(x0, y1),
            pymupdf.Point(x1, y1),
        )
        for x0, y0, x1, y1 in quads
    ]


def insert_text(path: str, page_number: int, text: str, rect: tuple[float, float, float, float],
                font_size: float = 12, color: tuple[float, float, float] = (0, 0, 0),
                font_name: str = "helv", output: str | None = None,
                overwrite: bool = False) -> str:
    with pymupdf.open(path) as doc:
        page = doc.load_page(page_number)
        available_fonts = {"helv", "cour"}
        if font_name not in available_fonts:
            raise ValueError("Unsupported font")
        fitted = page.insert_textbox(
            pymupdf.Rect(*rect),
            text,
            fontsize=font_size,
            fontname=font_name,
            color=color,
        )
        if fitted < 0:
            raise ValueError("Text does not fit within the selected bounds")
        destination = output or _default_output(path)
        save_atomic(doc, destination, overwrite=overwrite)
        return destination


def add_text_annotation(path: str, page_number: int, rect: tuple[float, float, float, float],
                       text: str, author: str = "", output: str | None = None,
                       overwrite: bool = False) -> str:
    with pymupdf.open(path) as doc:
        page = doc.load_page(page_number)
        annot = page.add_text_annot(pymupdf.Rect(*rect), text)
        _set_annotation_metadata(annot, author, text)
        destination = output or _default_output(path)
        save_atomic(doc, destination, overwrite=overwrite)
        return destination


add_comment = add_text_annotation


def add_highlight_annotation(path: str, page_number: int,
                             quads: list[tuple[float, float, float, float]],
                             author: str = "", color: tuple[float, float, float] = (1, 1, 0),
                             opacity: float = 0.5, output: str | None = None,
                             overwrite: bool = False) -> str:
    with pymupdf.open(path) as doc:
        page = doc.load_page(page_number)
        if not quads:
            raise ValueError("At least one highlight region is required")
        annot = page.add_highlight_annot(
            _make_quads(quads)
        )
        annot.set_colors(stroke=color)
        annot.set_opacity(opacity)
        _set_annotation_metadata(annot, author)
        destination = output or _default_output(path)
        save_atomic(doc, destination, overwrite=overwrite)
        return destination


def add_underline_annotation(path: str, page_number: int,
                             quads: list[tuple[float, float, float, float]],
                             author: str = "", color: tuple[float, float, float] = (0, 0, 1),
                              opacity: float = 1.0, output: str | None = None,
                              overwrite: bool = False) -> str:
    with pymupdf.open(path) as doc:
        page = doc.load_page(page_number)
        if not quads:
            raise ValueError("At least one underline region is required")
        annot = page.add_underline_annot(
            _make_quads(quads)
        )
        annot.set_colors(stroke=color)
        annot.set_opacity(opacity)
        _set_annotation_metadata(annot, author)
        destination = output or _default_output(path)
        save_atomic(doc, destination, overwrite=overwrite)
        return destination


def add_shape_annotation(path: str, page_number: int,
                         rect: tuple[float, float, float, float],
                         author: str = "", color: tuple[float, float, float] = (1, 0, 0),
                         width: float = 1.0, output: str | None = None,
                         overwrite: bool = False) -> str:
    with pymupdf.open(path) as doc:
        page = doc.load_page(page_number)
        annot = page.add_rect_annot(pymupdf.Rect(*rect))
        annot.set_colors(stroke=color)
        annot.set_border(width=width)
        _set_annotation_metadata(annot, author)
        destination = output or _default_output(path)
        save_atomic(doc, destination, overwrite=overwrite)
        return destination


def add_freehand_annotation(path: str, page_number: int,
                            points: list[tuple[float, float]],
                            author: str = "", color: tuple[float, float, float] = (1, 0, 0),
                            width: float = 1.0, output: str | None = None,
                            overwrite: bool = False) -> str:
    with pymupdf.open(path) as doc:
        page = doc.load_page(page_number)
        annot = page.add_ink_annot([[[float(x), float(y)] for x, y in points]])
        annot.set_colors(stroke=color)
        annot.set_border(width=width)
        _set_annotation_metadata(annot, author)
        destination = output or _default_output(path)
        save_atomic(doc, destination, overwrite=overwrite)
        return destination


def parse_watermark_page_selection(selected: str | None, page_count: int) -> set[int]:
    error = "invalid-watermark-page-selection"
    if selected is None or not selected.strip():
        raise ValueError(error)
    indexes: set[int] = set()
    for raw in selected.split(","):
        value = raw.strip()
        if not value or not value.isdigit():
            raise ValueError(error)
        page_number = int(value)
        if page_number < 1 or page_number > page_count:
            raise ValueError(error)
        index = page_number - 1
        if index in indexes:
            raise ValueError(error)
        indexes.add(index)
    return indexes


def add_watermark(path: str, output: str, text: str, pages: str = "all",
                  selected: str | None = None, overwrite: bool = False) -> None:
    with pymupdf.open(path) as doc:
        if pages not in {"all", "odd", "even", "selected"}:
            raise ValueError("Invalid watermark page scope")
        selected_indexes = (
            parse_watermark_page_selection(selected, doc.page_count)
            if pages == "selected"
            else set()
        )
        for index in range(doc.page_count):
            apply = pages == "all"
            if pages == "odd":
                apply = (index + 1) % 2 == 1
            elif pages == "even":
                apply = (index + 1) % 2 == 0
            elif pages == "selected":
                apply = index in selected_indexes
            if apply:
                rect = doc[index].rect
                doc[index].insert_text(
                    pymupdf.Point(rect.width / 2 - 40, rect.height / 2),
                    text,
                    fontsize=36,
                    overlay=True,
                )
        save_atomic(doc, output, overwrite=overwrite)


def add_image_watermark(
    path: str,
    output: str,
    image_path: str,
    pages: str = "all",
    selected: str | None = None,
    overwrite: bool = False,
) -> None:
    with pymupdf.open(path) as doc:
        if pages not in {"all", "odd", "even", "selected"}:
            raise ValueError("Invalid watermark page scope")
        selected_indexes = (
            parse_watermark_page_selection(selected, doc.page_count)
            if pages == "selected"
            else set()
        )
        for index in range(doc.page_count):
            apply = pages == "all"
            if pages == "odd":
                apply = (index + 1) % 2 == 1
            elif pages == "even":
                apply = (index + 1) % 2 == 0
            elif pages == "selected":
                apply = index in selected_indexes
            if apply:
                rect = doc[index].rect
                size = min(rect.width * 0.35, rect.height * 0.35)
                target = pymupdf.Rect(
                    rect.width / 2 - size / 2,
                    rect.height / 2 - size / 2,
                    rect.width / 2 + size / 2,
                    rect.height / 2 + size / 2,
                )
                doc[index].insert_image(target, filename=image_path, overlay=True)
        save_atomic(doc, output, overwrite=overwrite)
