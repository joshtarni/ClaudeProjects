from pathlib import Path
import hashlib
import json

import pymupdf

from core.annotations import add_highlight_annotation, add_watermark
from core.extraction import extract_images
from core.forms import fill_fields


FIXTURES = Path(__file__).resolve().parents[2] / "fixtures" / "pdf"


def test_fixture_manifest_and_baseline_files():
    manifest = json.loads((FIXTURES / "manifest.json").read_text())
    assert len(manifest["fixtures"]) == 10
    assert {fixture["category"] for fixture in manifest["fixtures"]} >= {
        "valid",
        "malformed",
        "password-protected",
        "standard AcroForm",
        "malformed AcroForm",
        "text-only",
        "image-only",
        "annotation",
        "watermark",
        "100-page",
    }
    assert set(manifest["viewer_matrix"]) == {
        fixture["name"] for fixture in manifest["fixtures"]
    }
    assert set(manifest["viewer_matrix"].values()) == {"pass"}

    for fixture in manifest["fixtures"]:
        path = FIXTURES / fixture["file"]
        assert path.exists()
        assert hashlib.sha256(path.read_bytes()).hexdigest() == fixture["sha256"]
        assert fixture["dialect"]
        assert fixture["open_result"]
        assert fixture["operation_results"]

        if fixture["page_count"] is not None:
            with pymupdf.open(path) as doc:
                assert doc.page_count == fixture["page_count"]



def test_valid_fixture_and_100_page_fixture_open():
    with pymupdf.open(FIXTURES / "valid.pdf") as doc:
        assert doc.page_count == 1
    with pymupdf.open(FIXTURES / "100-page.pdf") as doc:
        assert doc.page_count == 100


def test_damaged_fixture_is_rejected():
    try:
        pymupdf.open(FIXTURES / "damaged.pdf")
    except pymupdf.FileDataError:
        pass
    else:
        raise AssertionError("Damaged fixture opened as a valid PDF")


def test_required_text_and_form_fixture_categories():
    with pymupdf.open(FIXTURES / "text-only.pdf") as doc:
        assert "TEXT ONLY FIXTURE" in doc[0].get_text()

    with pymupdf.open(FIXTURES / "form.pdf") as doc:
        fields = [field for field in doc[0].widgets() or []]
        assert len(fields) == 1
        assert fields[0].field_name == "name"

    with pymupdf.open(FIXTURES / "malformed_acroform.pdf") as doc:
        fields = [field for field in doc[0].widgets() or []]
        assert len(fields) == 1
        assert fields[0].field_name == "malformed_field"


def test_save_reopen_form_annotation_watermark_and_image_operations(tmp_path):
    form_output = tmp_path / "form-filled.pdf"
    unsupported = fill_fields(str(FIXTURES / "form.pdf"), str(form_output), {"name": "Ada"})
    assert unsupported == []
    with pymupdf.open(form_output) as doc:
        widgets = list(doc[0].widgets() or [])
        assert widgets
        assert widgets[0].field_value == "Ada"

    annotation_output = tmp_path / "annotation-highlighted.pdf"
    add_highlight_annotation(
        str(FIXTURES / "valid.pdf"),
        0,
        [(20, 20, 100, 40)],
        "Acceptance",
        output=str(annotation_output),
    )
    with pymupdf.open(annotation_output) as doc:
        assert doc[0].first_annot is not None

    image_output_dir = tmp_path / "images"
    extracted = extract_images(str(FIXTURES / "image.pdf"), str(image_output_dir))
    assert len(extracted) == 1
    assert extracted[0].exists()

    watermark_output = tmp_path / "watermarked.pdf"
    add_watermark(
        str(FIXTURES / "watermark.pdf"),
        str(watermark_output),
        "TEST",
        pages="all",
    )
    with pymupdf.open(watermark_output) as doc:
        assert doc.page_count == 1
