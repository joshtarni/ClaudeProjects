from __future__ import annotations

import pymupdf

from core.document import save_atomic


def list_fields(path: str) -> list[tuple[str, str]]:
    with pymupdf.open(path) as doc:
        fields = []
        for page in doc:
            for widget in page.widgets() or []:
                fields.append((widget.field_name or "", widget.field_type_string))
        return fields


def fill_fields(path: str, output: str, values: dict[str, str], overwrite: bool = False) -> list[str]:
    unsupported: list[str] = []
    with pymupdf.open(path) as doc:
        for page in doc:
            for widget in page.widgets() or []:
                name = widget.field_name or ""
                if name not in values:
                    continue
                if widget.field_type_string in {
                    "Text",
                    "CheckBox",
                    "RadioButton",
                    "ComboBox",
                    "Choice",
                    "Signature",
                    "Sig",
                }:
                    widget.field_value = values[name]
                    widget.update()
                else:
                    unsupported.append(name)
        save_atomic(doc, output, overwrite=overwrite)
    return unsupported
