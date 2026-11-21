from pathlib import Path
import pymupdf

from core.extraction import extract_text


def test_extract_text(tmp_path):
    source = tmp_path / "text.pdf"
    doc = pymupdf.open()
    page = doc.new_page()
    page.insert_text((72, 72), "Fixture text")
    doc.save(source)
    doc.close()

    assert "Fixture text" in extract_text(str(source), [0])
