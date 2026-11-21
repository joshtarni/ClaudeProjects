import base64
import ast
import inspect
import tkinter as tk
from pathlib import Path

import pymupdf

from core.annotations import (
    add_freehand_annotation,
    add_highlight_annotation,
    add_shape_annotation,
    add_text_annotation,
    add_underline_annotation,
    insert_text,
)
from core.document import save_pdf
from core.images import remove_image_rect, replace_image
from core.annotations import add_image_watermark
from core.annotations import parse_watermark_page_selection
from core.extraction import extract_images
from core.forms import fill_fields, list_fields
from ui.main_window import parse_color, parse_points, parse_quads, parse_rect
from ui.viewer import (
    bind_drop_target,
    canvas_point_to_pdf,
    canvas_rect_to_pdf,
    rendered_point_to_pdf,
    rendered_rect_to_pdf,
)


PNG_1X1 = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk+A8AAQUBAScY42YAAAAASUVORK5CYII="
)


def make_source(path: Path) -> None:
    doc = pymupdf.open()
    page = doc.new_page(width=200, height=200)
    page.insert_text((30, 40), "KEEP THIS TEXT")
    doc.save(path)
    doc.close()


def test_save_pdf_default_output_and_source_overwrite(tmp_path):
    source = tmp_path / "source.pdf"
    make_source(source)
    original = source.read_bytes()

    output = tmp_path / "edited.pdf"
    save_pdf(source, output)
    assert output.exists()
    assert source.read_bytes() == original

    try:
        save_pdf(source, source)
    except PermissionError:
        pass
    else:
        raise AssertionError("Source overwrite did not require confirmation")

    save_pdf(source, source, overwrite=True)
    with pymupdf.open(source) as doc:
        assert doc.page_count == 1


def test_text_and_comment_edit_leave_source_unchanged(tmp_path):
    source = tmp_path / "source.pdf"
    make_source(source)
    original = source.read_bytes()

    text_output = tmp_path / "text.pdf"
    insert_text(str(source), 0, "INSERTED", (20, 60, 180, 100),
                output=str(text_output))
    assert source.read_bytes() == original
    assert text_output.exists()

    comment_output = tmp_path / "comment.pdf"
    add_text_annotation(str(source), 0, (20, 20, 80, 80),
                        "Review note", "Alice", str(comment_output))
    with pymupdf.open(comment_output) as doc:
        annot = doc[0].first_annot
        assert annot is not None
        assert annot.info.get("title") == "Alice"


def test_required_annotation_types_persist(tmp_path):
    source = tmp_path / "source.pdf"
    make_source(source)

    highlight = tmp_path / "highlight.pdf"
    add_highlight_annotation(str(source), 0, [(30, 30, 100, 50)],
                             "Alice", output=str(highlight))
    underline = tmp_path / "underline.pdf"
    add_underline_annotation(str(source), 0, [(30, 30, 100, 50)],
                            "Alice", output=str(underline))
    shape = tmp_path / "shape.pdf"
    add_shape_annotation(str(source), 0, (20, 20, 100, 80),
                         "Alice", output=str(shape))
    ink = tmp_path / "ink.pdf"
    add_freehand_annotation(str(source), 0, [(20, 20), (40, 40), (60, 20)],
                            "Alice", output=str(ink))

    for path in (highlight, underline, shape, ink):
        assert path.exists()
        with pymupdf.open(path) as doc:
            assert doc[0].first_annot is not None


def test_multi_quad_highlight_and_underline_persist(tmp_path):
    source = tmp_path / "source.pdf"
    make_source(source)

    highlight = tmp_path / "highlight.pdf"
    add_highlight_annotation(
        str(source),
        0,
        [(20, 20, 60, 40), (80, 80, 120, 100)],
        "Alice",
        output=str(highlight),
    )
    underline = tmp_path / "underline.pdf"
    add_underline_annotation(
        str(source),
        0,
        [(20, 20, 60, 40), (80, 80, 120, 100)],
        "Alice",
        output=str(underline),
    )

    with pymupdf.open(highlight) as doc:
        annots = list(doc[0].annots())
        assert len(annots) == 1
    with pymupdf.open(underline) as doc:
        annots = list(doc[0].annots())
        assert len(annots) == 1


def test_remove_image_preserves_intersecting_text(tmp_path):
    source = tmp_path / "source.pdf"
    doc = pymupdf.open()
    page = doc.new_page(width=200, height=200)
    page.insert_text((30, 40), "KEEP THIS TEXT")
    image_path = tmp_path / "image.png"
    image_path.write_bytes(PNG_1X1)
    page.insert_image(pymupdf.Rect(20, 20, 100, 100), filename=str(image_path))
    doc.save(source)
    doc.close()

    output = tmp_path / "removed.pdf"
    remove_image_rect(str(source), str(output), 0, (20, 20, 100, 100))
    with pymupdf.open(output) as doc:
        assert "KEEP THIS TEXT" in doc[0].get_text()


def test_replace_image_preserves_intersecting_text(tmp_path):
    source = tmp_path / "source.pdf"
    doc = pymupdf.open()
    page = doc.new_page(width=200, height=200)
    page.insert_text((30, 40), "KEEP THIS TEXT")
    image_path = tmp_path / "image.png"
    image_path.write_bytes(PNG_1X1)
    page.insert_image(pymupdf.Rect(20, 20, 100, 100), filename=str(image_path))
    doc.save(source)
    doc.close()

    output = tmp_path / "replaced.pdf"
    replace_image(str(source), str(output), 0, (20, 20, 100, 100),
                  str(image_path))
    with pymupdf.open(output) as doc:
        assert "KEEP THIS TEXT" in doc[0].get_text()


def test_image_watermark_only_changes_selected_pages(tmp_path):
    source = tmp_path / "source.pdf"
    doc = pymupdf.open()
    doc.new_page(width=200, height=200)
    doc.new_page(width=200, height=200)
    doc.save(source)
    doc.close()

    image_path = tmp_path / "watermark.png"
    image_path.write_bytes(PNG_1X1)
    output = tmp_path / "watermarked.pdf"
    add_image_watermark(
        str(source),
        str(output),
        str(image_path),
        pages="selected",
        selected="2",
    )

    with pymupdf.open(output) as doc:
        assert len(doc[0].get_images(full=True)) == 0
        assert len(doc[1].get_images(full=True)) == 1


def test_watermark_selection_rejects_invalid_values(tmp_path):
    source = tmp_path / "source.pdf"
    make_source(source)

    for selected in ("0", "-1", "abc", "1-2", "", "1,1", "2"):
        try:
            parse_watermark_page_selection(selected, 1)
        except ValueError as exc:
            assert str(exc) == "invalid-watermark-page-selection"
        else:
            raise AssertionError(f"Invalid watermark selection accepted: {selected}")


def test_unsupported_drop_binding_does_not_crash():
    class UnsupportedDropMaster:
        def bind(self, sequence, callback):
            if sequence == "<Drop>":
                raise tk.TclError('bad event type or keysym "Drop"')

    bind_drop_target(UnsupportedDropMaster(), lambda _event: "break")


def test_visual_selection_coordinate_mapping():
    assert canvas_point_to_pdf(600, 300, 2.0) == (300.0, 150.0)
    assert canvas_rect_to_pdf(600, 300, 200, 100, 2.0) == (100.0, 50.0, 300.0, 150.0)


def test_visual_selection_zoom_and_page_size_mapping():
    assert canvas_point_to_pdf(450, 225, 1.5) == (300.0, 150.0)


def test_rendered_selection_mapping_accounts_for_page_rotation_and_cropbox():
    page_rect = pymupdf.Rect(10, 20, 310, 220)
    assert rendered_point_to_pdf(600, 400, page_rect, 600, 400) == (310.0, 220.0)
    assert rendered_rect_to_pdf(600, 400, 200, 100, page_rect, 600, 400) == (
        110.0,
        70.0,
        310.0,
        220.0,
    )


def test_rendered_selection_mapping_clamps_scroll_overflow():
    page_rect = pymupdf.Rect(10, 20, 210, 220)
    assert rendered_point_to_pdf(-20, 500, page_rect, 400, 400) == (10.0, 220.0)


def test_rendered_selection_save_reopen(tmp_path):
    source = tmp_path / "source.pdf"
    make_source(source)
    page_rect = pymupdf.Rect(0, 0, 200, 200)
    rect = rendered_rect_to_pdf(40, 40, 160, 100, page_rect, 400, 400)

    output = tmp_path / "selected-text.pdf"
    insert_text(
        str(source),
        0,
        "SELECTED",
        rect,
        font_size=10,
        output=str(output),
    )
    with pymupdf.open(output) as doc:
        assert "SELECTED" in doc[0].get_text()


def test_existing_destination_requires_confirmation(tmp_path):
    source = tmp_path / "source.pdf"
    make_source(source)
    destination = tmp_path / "existing.pdf"
    make_source(destination)

    try:
        save_pdf(source, destination)
    except FileExistsError:
        pass
    else:
        raise AssertionError("Existing destination accepted without confirmation")


def test_image_extraction_existing_destination_requires_confirmation(tmp_path):
    fixture = Path(__file__).resolve().parents[2] / "fixtures" / "pdf" / "image.pdf"
    output_dir = tmp_path / "images"
    output_dir.mkdir()
    target = output_dir / "page-1-image-1.png"
    target.write_bytes(b"existing")

    try:
        extract_images(str(fixture), str(output_dir))
    except FileExistsError:
        pass
    else:
        raise AssertionError("Existing image destination accepted without confirmation")
    assert target.read_bytes() == b"existing"


def test_operation_parameter_parsers():
    assert parse_rect("10,20,100,200") == (10.0, 20.0, 100.0, 200.0)
    assert parse_color("1,0.5,0") == (1.0, 0.5, 0.0)
    assert parse_quads("10,20,100,200;110,20,150,80") == [
        (10.0, 20.0, 100.0, 200.0),
        (110.0, 20.0, 150.0, 80.0),
    ]
    assert parse_points("10,20;30,40") == [(10.0, 20.0), (30.0, 40.0)]

    for invalid in ("", "10,20", "-1,20,30,40", "10,20,10,40"):
        try:
            parse_rect(invalid)
        except ValueError:
            pass
        else:
            raise AssertionError(f"Invalid rectangle accepted: {invalid}")


def test_text_font_and_overflow_validation(tmp_path):
    source = tmp_path / "source.pdf"
    make_source(source)

    fitted = tmp_path / "fitted.pdf"
    insert_text(
        str(source),
        0,
        "Fitted",
        (20, 20, 180, 180),
        font_size=12,
        font_name="cour",
        output=str(fitted),
    )
    with pymupdf.open(fitted) as doc:
        assert "Fitted" in doc[0].get_text()

    try:
        insert_text(
            str(source),
            0,
            "This text is intentionally too large for this tiny target",
            (20, 20, 21, 21),
            font_size=12,
            font_name="helv",
            output=str(tmp_path / "overflow.pdf"),
        )
    except ValueError as exc:
        assert "does not fit" in str(exc)
    else:
        raise AssertionError("Overflowing text was accepted")

    try:
        insert_text(
            str(source),
            0,
            "Text",
            (20, 20, 180, 180),
            font_name="not-a-font",
            output=str(tmp_path / "bad-font.pdf"),
        )
    except ValueError as exc:
        assert "Unsupported font" in str(exc)
    else:
        raise AssertionError("Unsupported font was accepted")


def test_acroform_text_field_persists(tmp_path):
    fixture = Path(__file__).resolve().parents[2] / "fixtures" / "pdf" / "form.pdf"
    fields = list_fields(str(fixture))
    assert ("name", "Text") in fields

    output = tmp_path / "filled.pdf"
    unsupported = fill_fields(str(fixture), str(output), {"name": "Ada Lovelace"})
    assert unsupported == []

    with pymupdf.open(output) as doc:
        widgets = list(doc[0].widgets() or [])
        assert widgets
        assert widgets[0].field_value == "Ada Lovelace"


def test_merge_and_watermark_use_single_overwrite_confirmation():
    from ui.main_window import MainWindow

    tree = ast.parse(inspect.getsource(MainWindow))
    methods = {
        node.name: node
        for node in tree.body
        if isinstance(node, ast.ClassDef)
        for node in node.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    }

    for method_name in ("merge_documents", "add_watermark"):
        confirmations = sum(
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id == "confirm_overwrite"
            for node in ast.walk(methods[method_name])
        )
        assert confirmations == 1
