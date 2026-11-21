from pathlib import Path
import pymupdf

from core.document import (
    PageRangeError,
    merge_pdfs,
    open_pdf,
    parse_page_ranges,
    reorder_and_delete,
    rotate_pages,
    split_pdf,
)
from core.security import encrypt_pdf, decrypt_pdf, validate_password_pair


def make_pdf(path: Path, pages: int = 12) -> None:
    doc = pymupdf.open()
    for index in range(pages):
        page = doc.new_page(width=200, height=200)
        page.insert_text((20, 40), f"Page {index + 1}")
    doc.save(path)
    doc.close()


def test_parse_and_split(tmp_path):
    source = tmp_path / "base.pdf"
    make_pdf(source)

    ranges = parse_page_ranges("1-3,5,9-12", 12)
    assert [end - start + 1 for start, end, _ in ranges] == [3, 1, 4]

    outputs = split_pdf(source, "1-3,5,9-12", tmp_path)
    assert len(outputs) == 1
    with pymupdf.open(outputs[0]) as result:
        assert result.page_count == 8

    separate = split_pdf(source, "1-3,5,9-12", tmp_path / "separate", separate=True)
    assert [path.name for path in separate] == [
        "base-pages-1-3.pdf",
        "base-pages-5.pdf",
        "base-pages-9-12.pdf",
    ]


def test_invalid_ranges(tmp_path):
    for expression in ("", "3-1", "13", "1-3,3-5", "5,5", "1-"):
        try:
            parse_page_ranges(expression, 12)
        except PageRangeError:
            pass
        else:
            raise AssertionError(f"Expected rejection: {expression}")


def test_merge_rotate_reorder(tmp_path):
    first = tmp_path / "first.pdf"
    second = tmp_path / "second.pdf"
    make_pdf(first, 2)
    make_pdf(second, 3)

    merged = tmp_path / "merged.pdf"
    merge_pdfs([first, second], merged)
    with pymupdf.open(merged) as doc:
        assert doc.page_count == 5

    rotated = tmp_path / "rotated.pdf"
    rotate_pages(str(merged), str(rotated), [0, 2], 90)
    with pymupdf.open(rotated) as doc:
        assert doc.load_page(0).rotation == 90
        assert doc.load_page(1).rotation == 0

    reordered = tmp_path / "reordered.pdf"
    reorder_and_delete(str(merged), str(reordered), [4, 2, 0])
    with pymupdf.open(reordered) as doc:
        assert doc.page_count == 3


def test_password_validation_and_encryption(tmp_path):
    source = tmp_path / "source.pdf"
    make_pdf(source, 1)
    encrypted = tmp_path / "encrypted.pdf"

    try:
        validate_password_pair("", "123456789012")
    except ValueError:
        pass
    else:
        raise AssertionError("Blank password accepted")

    owner = "owner-password-123"
    user = "user-password-456"
    encrypt_pdf(str(source), str(encrypted), owner, user)
    try:
        pymupdf.open(encrypted)
    except pymupdf.FileDataError:
        pass

    try:
        open_pdf(encrypted)
    except ValueError as exc:
        assert "Password required" in str(exc)
    else:
        raise AssertionError("Encrypted PDF opened without a password")

    try:
        open_pdf(encrypted, "wrong-password")
    except ValueError as exc:
        assert "Incorrect password" in str(exc)
    else:
        raise AssertionError("Encrypted PDF accepted a wrong password")

    with open_pdf(encrypted, owner) as unlocked:
        assert unlocked.page_count == 1

    decrypted = tmp_path / "decrypted.pdf"
    decrypt_pdf(str(encrypted), str(decrypted), owner)
    with pymupdf.open(decrypted) as doc:
        assert doc.page_count == 1
