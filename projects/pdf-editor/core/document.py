from __future__ import annotations

import os
import re
import tempfile
from pathlib import Path
from typing import Iterable

import pymupdf


class PageRangeError(ValueError):
    pass


def open_pdf(
    path: str | os.PathLike[str],
    password: str | None = None,
) -> pymupdf.Document:
    try:
        doc = pymupdf.open(str(path))
    except Exception as exc:
        raise ValueError(f"Cannot open PDF '{path}': {exc}") from exc
    if doc.needs_pass:
        if password:
            if not doc.authenticate(password):
                doc.close()
                raise ValueError(f"Incorrect password for '{path}'")
        else:
            doc.close()
            raise ValueError(f"Password required for '{path}'")
    return doc


def parse_page_ranges(expression: str, page_count: int) -> list[tuple[int, int, str]]:
    if not expression or not expression.strip():
        raise PageRangeError("Empty page selection")

    ranges: list[tuple[int, int, str]] = []
    for raw in expression.split(","):
        text = raw.strip()
        if not text:
            raise PageRangeError("Empty expression")
        if re.fullmatch(r"\d+", text):
            start = end = int(text)
            label = text
        else:
            match = re.fullmatch(r"(\d+)\s*-\s*(\d+)", text)
            if not match:
                raise PageRangeError(f"Malformed expression: {text}")
            start, end = map(int, match.groups())
            label = f"{start}-{end}"
            if start > end:
                raise PageRangeError(f"Reversed range: {text}")
        if start < 1 or end > page_count:
            raise PageRangeError(f"Page range outside 1-{page_count}: {text}")

        for old_start, old_end, old_label in ranges:
            if label == old_label:
                raise PageRangeError(f"Duplicate expression: {text}")
        for old_start, old_end, old_label in ranges:
            if start <= old_end and old_start <= end:
                raise PageRangeError(
                    f"Overlapping range: {text} overlaps {old_label}"
                )
        ranges.append((start, end, label))
    return ranges


def selected_pages(expression: str, page_count: int) -> list[int]:
    ranges = parse_page_ranges(expression, page_count)
    pages: list[int] = []
    seen: set[int] = set()
    for start, end, _ in ranges:
        for page in range(start, end + 1):
            if page in seen:
                raise PageRangeError(f"Duplicate page: {page}")
            seen.add(page)
            pages.append(page - 1)
    return pages


def merge_pdfs(
    paths: Iterable[str | os.PathLike[str]],
    output: str | os.PathLike[str],
    overwrite: bool = False,
) -> None:
    output_path = Path(output)
    require_destination_permission(output_path, overwrite)
    with pymupdf.open() as result:
        for path in paths:
            with open_pdf(path) as source:
                result.insert_pdf(source)
        save_atomic(result, output_path, overwrite=overwrite)


def split_pdf(
    path: str | os.PathLike[str],
    expression: str,
    output_dir: str | os.PathLike[str],
    separate: bool = False,
) -> list[Path]:
    source_path = Path(path)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    with open_pdf(source_path) as source:
        ranges = parse_page_ranges(expression, source.page_count)
        labels = [label for _, _, label in ranges]
        if len(set(labels)) != len(labels):
            raise PageRangeError("Duplicate expression")

        base = source_path.stem
        pages = selected_pages(expression, source.page_count)
        if separate:
            names = [f"{base}-pages-{label}.pdf" for label in labels]
            outputs: list[Path] = []
            for (start, end, _), name in zip(ranges, names):
                target = collision_free(output_dir / name)
                with pymupdf.open() as result:
                    result.insert_pdf(source, from_page=start - 1, to_page=end - 1)
                    save_atomic(result, target)
                outputs.append(target)
            return outputs

        target = collision_free(output_dir / f"{base}-split.pdf")
        with pymupdf.open() as result:
            for page in pages:
                result.insert_pdf(source, from_page=page, to_page=page)
            save_atomic(result, target)
        return [target]


def collision_free(path: Path) -> Path:
    if not path.exists():
        return path
    number = 2
    while True:
        candidate = path.with_name(f"{path.stem}-{number}{path.suffix}")
        if not candidate.exists():
            return candidate
        number += 1


def save_atomic(
    doc: pymupdf.Document,
    output: str | os.PathLike[str],
    close_before_replace: bool = False,
    overwrite: bool = False,
) -> None:
    output = Path(output)
    require_destination_permission(output, overwrite)
    output.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(prefix=f".{output.stem}-", suffix=".pdf", dir=output.parent)
    os.close(fd)
    try:
        doc.save(temp_name, garbage=4, deflate=True)
        if close_before_replace and not getattr(doc, "is_closed", False):
            doc.close()
        os.replace(temp_name, output)
    except Exception:
        try:
            os.unlink(temp_name)
        except FileNotFoundError:
            pass
        raise


def save_pdf(
    source: str | os.PathLike[str],
    output: str | os.PathLike[str],
    overwrite: bool = False,
) -> Path:
    source_path = Path(source)
    output_path = Path(output)
    if not overwrite and output_path.exists() and output_path.resolve() != source_path.resolve():
        raise FileExistsError(f"Destination already exists: {output_path}")
    if output_path.resolve() == source_path.resolve() and not overwrite:
        raise PermissionError("Overwriting the source requires explicit confirmation")
    doc = open_pdf(source_path)
    try:
        save_atomic(doc, output_path, close_before_replace=True, overwrite=overwrite)
    finally:
        if hasattr(doc, "is_closed") and not doc.is_closed:
            doc.close()
    return output_path


def require_destination_permission(
    output: str | os.PathLike[str],
    overwrite: bool = False,
) -> None:
    output_path = Path(output)
    if output_path.exists() and not overwrite:
        raise FileExistsError(f"Destination already exists: {output_path}")


def rotate_pages(
    path: str,
    output: str,
    page_numbers: Iterable[int],
    degrees: int,
    overwrite: bool = False,
) -> None:
    if degrees not in (90, 180, 270):
        raise ValueError("Rotation must be 90, 180, or 270 degrees")
    with open_pdf(path) as doc:
        selected = set(page_numbers)
        for index in selected:
            doc.load_page(index).set_rotation(degrees)
        save_atomic(doc, output, overwrite=overwrite)


def reorder_and_delete(
    path: str,
    output: str,
    page_order: Iterable[int],
    overwrite: bool = False,
) -> None:
    order = list(page_order)
    if len(set(order)) != len(order) or any(index < 0 for index in order):
        raise PageRangeError("Page order must contain unique non-negative page indexes")
    with open_pdf(path) as doc:
        if any(index >= doc.page_count for index in order):
            raise PageRangeError("Page index out of bounds")
        with pymupdf.open() as result:
            for index in order:
                result.insert_pdf(doc, from_page=index, to_page=index)
            save_atomic(result, output, overwrite=overwrite)
