from __future__ import annotations

from pathlib import Path
import os
import tempfile
import pymupdf

from core.document import require_destination_permission


def extract_text(path: str, page_numbers: list[int] | None = None) -> str:
    with pymupdf.open(path) as doc:
        indexes = page_numbers or list(range(doc.page_count))
        return "\n".join(doc.load_page(index).get_text("text") for index in indexes)


def extract_images(
    path: str,
    output_dir: str,
    page_numbers: list[int] | None = None,
    overwrite: bool = False,
) -> list[Path]:
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    outputs: list[Path] = []
    with pymupdf.open(path) as doc:
        indexes = page_numbers or list(range(doc.page_count))
        for page_index in indexes:
            for image_index, image in enumerate(doc.load_page(page_index).get_images(full=True)):
                pix = pymupdf.Pixmap(doc, image[0])
                target = output_dir / f"page-{page_index + 1}-image-{image_index + 1}.png"
                require_destination_permission(target, overwrite)
                fd, temp_name = tempfile.mkstemp(
                    prefix=f".{target.stem}-",
                    suffix=".png",
                    dir=output_dir,
                )
                os.close(fd)
                try:
                    pix.save(temp_name)
                    os.replace(temp_name, target)
                except Exception:
                    try:
                        os.unlink(temp_name)
                    except FileNotFoundError:
                        pass
                    raise
                outputs.append(target)
    return outputs


def export_text(text: str, output: str, overwrite: bool = False) -> Path:
    destination = Path(output)
    require_destination_permission(destination, overwrite)
    destination.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(
        prefix=f".{destination.stem}-",
        suffix=destination.suffix or ".txt",
        dir=destination.parent,
        text=True,
    )
    os.close(fd)
    try:
        Path(temp_name).write_text(text, encoding="utf-8")
        os.replace(temp_name, destination)
    except Exception:
        try:
            os.unlink(temp_name)
        except FileNotFoundError:
            pass
        raise
    return destination
