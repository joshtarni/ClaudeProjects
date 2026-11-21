from __future__ import annotations

import pymupdf

import os
import tempfile
from pathlib import Path

from core.document import require_destination_permission, save_atomic


def validate_password_pair(owner: str, user: str) -> None:
    if not owner or not user:
        raise ValueError("Owner and user passwords are required")
    if len(owner) < 12 or len(user) < 12:
        raise ValueError("Owner and user passwords must be at least 12 characters")


def encrypt_pdf(path: str, output: str, owner: str, user: str, overwrite: bool = False) -> None:
    validate_password_pair(owner, user)
    destination = Path(output)
    require_destination_permission(destination, overwrite)
    destination.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(
        prefix=f".{destination.stem}-",
        suffix=".pdf",
        dir=destination.parent,
    )
    os.close(fd)
    doc = pymupdf.open(path)
    try:
        doc.save(
            temp_name,
            encryption=pymupdf.PDF_ENCRYPT_AES_256,
            owner_pw=owner,
            user_pw=user,
            permissions=pymupdf.PDF_PERM_PRINT | pymupdf.PDF_PERM_COPY,
            garbage=4,
            deflate=True,
        )
        doc.close()
        os.replace(temp_name, destination)
    except Exception:
        if not doc.is_closed:
            doc.close()
        try:
            os.unlink(temp_name)
        except FileNotFoundError:
            pass
        raise


def decrypt_pdf(path: str, output: str, owner_password: str, overwrite: bool = False) -> None:
    with pymupdf.open(path) as doc:
        if doc.needs_pass:
            if not doc.authenticate(owner_password):
                raise ValueError("Incorrect owner password")
        save_atomic(doc, output, overwrite=overwrite)
