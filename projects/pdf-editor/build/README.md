# PDF Editor Build

## Source environment

Use Python 3.12 through 3.15, inclusive (`>=3.12,<3.16`) with the pinned
PyMuPDF wheel.
Install the pinned source environment:

```powershell
cd projects/pdf-editor
python -m pip install -r requirements.lock
python -m pip install -e ".[test]"
```

Run checks:

```powershell
python -m pytest
```

## Windows executable

Packaging is authorized only after `/review-script` passes code review.

```powershell
cd projects/pdf-editor
python -m PyInstaller --clean --noconfirm pdf_editor.spec
```

The one-file, windowed executable is written to `dist/PDFEditor.exe`.
No standalone executable is produced by `/build-script`.

PyMuPDF licensing and third-party notices must be retained in the distribution.
Antivirus allow-listing or code signing may be needed on managed Windows systems.
