from __future__ import annotations

import pymupdf

from core.document import save_atomic


def _delete_images_in_rect(page: pymupdf.Page, rect: tuple[float, float, float, float]) -> int:
    target = pymupdf.Rect(*rect)
    deleted = 0
    if not hasattr(page, "delete_image"):
        raise RuntimeError("This PyMuPDF build cannot remove an individual image")
    for info in page.get_image_info(xrefs=True):
        xref = info.get("xref", 0)
        image_rect = pymupdf.Rect(info["bbox"])
        if xref and target.intersects(image_rect):
            page.delete_image(xref)
            deleted += 1
    return deleted


def insert_image(path: str, output: str, page_number: int, image_path: str,
                 rect: tuple[float, float, float, float], overwrite: bool = False) -> None:
    with pymupdf.open(path) as doc:
        doc.load_page(page_number).insert_image(pymupdf.Rect(*rect), filename=image_path)
        save_atomic(doc, output, overwrite=overwrite)


def replace_image(path: str, output: str, page_number: int,
                  rect: tuple[float, float, float, float], image_path: str,
                  overwrite: bool = False) -> None:
    with pymupdf.open(path) as doc:
        page = doc.load_page(page_number)
        deleted = _delete_images_in_rect(page, rect)
        if deleted == 0:
            raise ValueError("No image was found in the selected rectangle")
        page.insert_image(pymupdf.Rect(*rect), filename=image_path)
        save_atomic(doc, output, overwrite=overwrite)


def remove_image_rect(path: str, output: str, page_number: int,
                      rect: tuple[float, float, float, float],
                      overwrite: bool = False) -> None:
    with pymupdf.open(path) as doc:
        page = doc.load_page(page_number)
        deleted = _delete_images_in_rect(page, rect)
        if deleted == 0:
            raise ValueError("No image was found in the selected rectangle")
        save_atomic(doc, output, overwrite=overwrite)
