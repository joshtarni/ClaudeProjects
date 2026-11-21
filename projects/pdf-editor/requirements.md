# PDF Editor Requirements

## Document Control

- **Status:** Packaged
- **Requirements review:** Passed
- **Implementation:** Current
- **Code review:** Passed
- **Packaging:** Complete
- **Last updated:** 2026-11-22

## 1. Purpose

Create a Windows PDF editor for local PDF files. The intended user is a
desktop user who needs to view, organize, annotate, and export common PDF
documents without uploading them to an internet service.

## 2. Scope

### Goals

- Provide a native-style desktop GUI for opening, reviewing, editing, and
  saving local PDF files.
- Support merge, split, text insertion, image insertion/replacement/removal,
  page rotation, page reordering/deletion, annotations, encryption/decryption,
  form-field filling, text/image extraction, and watermarks.
- Preserve PDF page geometry and existing content where the selected operation
  does not intentionally change it.
- Prevent accidental loss by requiring explicit confirmation for destructive
  actions and recommending save-to-new-file behavior.
- Produce both Python source and a standalone Windows executable after
  implementation and code review gates pass.

### Non-goals

- Server/cloud storage, account management, browser extension behavior, or
  collaborative real-time editing.
- Optical character recognition as a required baseline feature.
- Reconstruction of the original document layout or reflow of existing PDF
  text.
- Support for every PDF/A, signed-document, XFA, or specialized PDF dialect.
- Printing in the initial release unless identified by `/review-req` as needed
  for a complete user workflow.

## 3. User Workflow

1. Launch the application and open one or more local PDF files.
2. Review thumbnails and page content in a scrollable viewer.
3. Select a document operation or choose one or more pages.
4. Configure operation parameters through validated controls.
5. Preview the affected page or a thumbnail summary when applicable.
6. Apply the operation and observe success, warning, or recovery instructions.
7. Save to a new file, overwrite only after explicit confirmation, or export
   extracted content.

## 4. Requirements

| ID | Requirement | Priority | Acceptance test | Status |
|---|---|---|---|---|
| REQ-001 | Open a readable, unlocked PDF by drag-and-drop or file picker. | Must | A valid PDF displays without crashing and reports an explicit error for invalid or encrypted input. | Accepted |
| REQ-002 | Display pages, zoom, and page thumbnails. | Must | A 100-page fixture is navigable by thumbnail and page number; zoom does not corrupt page content. | Accepted |
| REQ-003 | Merge at least two PDFs into a page-ordered output. | Must | Source pages appear in selected file and page order exactly once in the generated PDF. | Accepted |
| REQ-004 | Split by one or more page ranges or individual selected pages. Page ranges use one-based inclusive PDF page numbers; `N-M` selects a range, `N` selects one page, and comma-separated expressions may be combined. Whitespace around commas and ranges is ignored. Reversed ranges (`3-1`), ranges outside the 1-page-count bounds, overlapping ranges, duplicate expressions, and duplicate pages are rejected with a named validation error; at least one valid page must be selected. Single-output mode preserves expression order and emits each selected page once. Separate-output mode creates one file per expression in expression order and rejects duplicate expressions. Range expressions may not overlap another expression. Output names default to `<base>-pages-<range>.pdf`; single-output mode uses `<base>-split.pdf`. If a generated name already exists, append `-2`, `-3`, and so on. | Must | A fixture with 12 pages split by `1-3,5,9-12` produces 8 uniquely ordered pages in single-output mode and separate range files `base-pages-1-3.pdf`, `base-pages-5.pdf`, and `base-pages-9-12.pdf`; malformed, reversed, out-of-bounds, overlapping, duplicate-expression, empty, and name-collision cases follow the documented outcomes. | Accepted |
| REQ-005 | Insert text onto a selected page with position, size, font, and color controls. | Must | Text renders within selected bounds and remains searchable/renderable in the saved output. | Accepted |
| REQ-006 | Insert, replace, or remove an image on selected pages. Insertion uses a selected top-left coordinate and target width/height or automatic proportional size. Replacement removes the selected rectangular image region and inserts the replacement at the same rectangle. Removal permanently removes the selected image content; this is not document text redaction unless separately requested. | Must | Inserted, replaced, and removed image results remain isolated to the selected page and rectangle after reopen and application verification. | Accepted |
| REQ-007 | Rotate selected pages in 90-degree increments. | Must | Page rotation is persisted and displayed correctly after reopening. | Accepted |
| REQ-008 | Reorder and delete selected pages. | Must | Final PDF follows the selected sequence and contains no deleted pages. | Accepted |
| REQ-009 | Add text, highlight, underline, shape, freehand, and comment annotations. Text, highlight, underline, shape, and freehand annotations store position, author, creation/modification time, and at least color and opacity or stroke width where applicable. Comments store text and author. | Must | Supported annotations remain visible and persist after save/reopen in the application. | Accepted |
| REQ-010 | Add password protection and remove a password when the correct password is available. Encryption uses separate non-empty owner and user passwords, each at least 12 characters, AES-256 encryption, and PDF 1.7-compatible encryption where supported. Owner credentials retain full control; user credentials receive only printing and copying permissions, with editing disabled unless a later change request adds it. Blank passwords are rejected. Passwords are never logged or retained after the operation. | Must | Encrypted output requires the user or owner password in the application; wrong passwords fail; the correct owner credential must enable removal of protection; no credential or permission setting is silently weakened. | Accepted |
| REQ-011 | Detect and fill supported AcroForm text, checkbox, radio, dropdown, and signature-placeholder fields. | Must | Form values persist after save/reopen; unsupported or damaged fields produce a warning rather than silent success. | Accepted |
| REQ-012 | Extract selected text or images to files or the clipboard. | Must | Extracted text matches fixture expectations; image export uses PNG or JPEG and reports no-match conditions. | Accepted |
| REQ-013 | Apply a text or image watermark to all, odd, even, or selected pages. Selected page numbers are one-based, comma-separated positive integers. Every selected value must be within 1 through the PDF page count; zero, negative values, malformed expressions, duplicate values, and out-of-bounds values are rejected with the named `invalid-watermark-page-selection` validation error and produce no output. | Must | Watermark appears on every valid selected page and never silently affects unselected pages. Zero, negative, non-numeric, malformed, duplicate, and out-of-bounds selections fail without creating or replacing a file. | Accepted |
| REQ-014 | Save changes to a new filename by default. Before any merge, split, reorder/delete, security, form, extraction, text edit, image edit, annotation, rotation, or watermark operation replaces an existing destination or source file, the application requires explicit confirmation. Cancellation preserves both source and destination; successful output is written completely through an atomic temporary-file/replacement transaction so no partial PDF is presented as successful. | Must | Applying edits never modifies the source file unless overwrite is explicitly selected and confirmed. Existing destinations for every operation require confirmation, cancellation is non-destructive, and failed PDF writes leave no partial output. | Accepted |
| REQ-015 | Treat corrupted, locked, unsupported, or failed-output files as recoverable errors. | Must | The application displays the filename and safe next action; no partial output is presented as successful. | Accepted |
| REQ-016 | Expose a help/about view containing version and third-party license information. | Should | Version and bundled dependency licenses are discoverable from the UI. | Accepted |

## 5. Inputs, Outputs, and Constraints

- **Inputs:** `.pdf` files selected locally; optional password; page ranges;
  text, font settings, colors, rectangles; image files; and export folders.
- **Outputs:** Modified PDF files, split/merged PDFs, extracted text, extracted
  images, and success/error notifications.
- **Platform/runtime:** Windows 10 or 11, 64-bit. The implementation will use
  Python 3.12 through 3.15, inclusive. The exact supported range is
  `>=3.12,<3.16`, and any upper-bound or minimum-Python change requires an
  accepted change request and requirements re-review.
- **Constraints:** Process local files offline. Do not transmit document
  contents or credentials to network services. Memory and output behavior must
  remain usable for normal documents; unusually large documents may require
  streaming or size warnings.
- **Privacy:** Passwords and file paths must not be written to application logs.
- **Compatibility:** Initial save output must be PDF 1.7 or an existing
  standards-compatible format supported by the chosen library.
- **Accepted PDF baseline:** The baseline is PDF 1.7 for normal saved documents
  and PDF 2.0 only when a feature or encryption policy requires it. Baseline
  fixtures are non-linearized, standard PDF 1.7/AcroForm documents; linearized
  PDFs, XFA, JavaScript, embedded portfolios, and signed-document workflows
  remain unsupported unless a change request adds test fixtures and acceptance
  criteria.
- **Fixture manifest:** `fixtures/pdf/manifest.json` must identify each fixture
  by relative path and SHA-256, document its PDF version and dialect, name the
  expected page count/text/images/forms, and list the pass/fail result for
  each open/edit/save operation. Required fixture categories are valid,
  malformed, password-protected, 100-page, image-only, text-only, standard
  AcroForm, malformed AcroForm, and annotation round-trip documents.
  Every required fixture operation must have an explicit machine-verifiable
  result of `pass`, `fail`, or `not-applicable`; `not-tested` is not a final
  acceptance result. Form and annotation fixtures must include save/reopen
  round-trip assertions, and integration tests must verify those results.
- **Viewer matrix:** External PDF-viewer validation is outside the initial
  release scope. Supported fixtures and acceptance checks are performed in the
  application itself. Adding external viewer requirements requires a later
  change request and requirements re-review.
- **Fixture baseline:** Before implementation begins, the project must add a
  manifest of local test PDFs covering valid, damaged, locked, 100-page,
  image-only, text-only, standard AcroForm, malformed AcroForm, and encrypted
  cases. Expected page images or text summaries and
  file hashes must be checked into or documented by the test fixture setup.
- **Viewer baseline:** Acceptance is performed in the application itself.
  No external PDF viewer is required for initial-release acceptance.
- **Packaging:** A single-file, windowed Windows executable is requested.
  The source and executable must be reproducible from a pinned dependency
  lockfile using the exact Python version and build commands documented in
  source control. Clean-build checks must compare package contents and document
  any unavoidable OS/runtime differences.

## 6. Design and Implementation Plan

### Proposed design

Use a Python GUI with a PDF library and an output transaction model. The
library will open documents read-only, render pages for preview, maintain page
operations as in-memory or temporary-document changes, then write to a uniquely
named temporary file before atomic replacement or explicit overwrite. UI,
document operations, security, and packaging concerns should remain separate
for testing.

PyMuPDF is a current candidate because its documentation describes text, image,
annotation, form, page, and document operations, but final dependency selection
must remain an implementation choice until compatibility, licensing, and test
fixtures are reviewed.

### Proposed script scaffold

This project is a modular Windows desktop application rather than a
single-file script. `pdf_editor.py` is the application entry point; UI, document
operations, security, extraction, and transaction behavior remain separated for
testing and review.

Legend: `[x]` = present and verified; `[ ]` = planned, missing, incomplete, or
not yet verified.

| Scaffold item | Function / deliverable | Requirement / test IDs | Phase | State |
|---|---|---|---|---|
| `pdf_editor.py` | Application entry point, startup validation, and main workflow | REQ-001; REQ-014; TEST-001 | 1 | [x] |
| `ui/main_window.py` | Native-style application shell and operation controls | REQ-001; REQ-014; TEST-009 | 1-2 | [x] |
| `ui/viewer.py` | PDF display, thumbnails, page navigation, zoom, and selection | REQ-002 | 2 | [x] |
| `ui/dialogs.py` | File, password, overwrite, warning, export, and help dialogs | REQ-001; REQ-010; REQ-014-016 | 2-4 | [x] |
| `core/document.py` | Open/save transactions, merge, split, rotate, reorder, and delete | REQ-001; REQ-003-004; REQ-007-008; REQ-014-015 | 1-3 | [x] |
| `core/annotations.py` | Text, highlight, underline, shape, freehand, comments, and watermarks | REQ-009; REQ-013 | 4 | [x] |
| `core/images.py` | Insert, replace, and remove individual images without redacting text | REQ-006 | 4 | [x] |
| `core/forms.py` | AcroForm discovery and supported field updates | REQ-011 | 4 | [x] |
| `core/security.py` | Password validation, encryption, and decryption | REQ-010 | 4 | [x] |
| `core/extraction.py` | Text and image extraction/export | REQ-012 | 4 | [x] |
| `tests/unit/` | Dependency, page-range, password, transaction, annotation, image, and extraction unit coverage | TEST-003-006; TEST-008-009; TEST-011 | 1-5 | [x] |
| `tests/integration/` | Fixture manifest and baseline valid/damaged/100-page integration coverage | TEST-001-010; TEST-012 | 2-5 | [x] |
| `fixtures/pdf/` | Valid, damaged, encrypted, form, annotation, image, watermark, and 100-page fixtures | TEST-002-008; TEST-011-012 | 1-5 | [x] |
| `pyproject.toml` | Python requirement, dependencies, tooling, and reproducible environment metadata | Input constraints; TEST-013 | 1 | [x] |
| `requirements.lock` | Pinned dependency set for reproducible source builds | Packaging constraints; TEST-013 | 1 | [x] |
| `pdf_editor.spec` | Windowed, single-file PyInstaller executable configuration | Packaging constraints; TEST-010; TEST-013 | 5 | [x] |
| `build/README.md` | Exact build commands, clean-build checks, license, and antivirus guidance | CRIT-001; CRIT-004; TEST-010; TEST-013 | 5 | [x] |

The scaffold may be split further only if it preserves the entry point,
separation of responsibilities, acceptance fixtures, and reproducible Windows
packaging requirements. Test fixtures should cover valid, damaged, encrypted,
form, annotation, image, watermark, and 100-page documents, with the viewer
matrix described in TEST-012. The final build configuration must produce the
windowed, single-file executable identified in the constraints.

### Planned files/modules

| Path | Responsibility |
|---|---|
| `pdf_editor.py` or split equivalent | Application entry point and startup validation |
| `ui/` | GUI views, dialogs, thumbnail and page rendering |
| `core/document.py` | Open/save, page operations, and file transactions |
| `core/annotations.py` | Annotation and watermark operations |
| `core/forms.py` | AcroForm discovery and field updates |
| `core/security.py` | Password validation and encryption/decryption |
| `core/extraction.py` | Text and image extraction |
| `tests/` | Unit, integration, and sample-document acceptance fixtures |

### Implementation phases

| Phase | Work | Exit criteria | Status |
|---|---|---|---|
| 1 | Dependency spike and document transaction prototype | Open/save, corrupted input, and atomic output behavior pass fixture tests | Complete |
| 2 | Viewer, thumbnails, zoom, navigation, and page selection | 100-page and encrypted fixture workflows pass manual tests | Complete |
| 3 | Merge, split, rotate, reorder, delete, and save flows | REQ-003, REQ-004, REQ-007, REQ-008 and save safety pass | Complete |
| 4 | Text, image, annotation, form, security, extraction, and watermark features | REQ-005 through REQ-013 pass fixture tests | Complete |
| 5 | Hardening, packaging, and Windows executable validation | Clean-machine launch, antivirus-signing caveats, and source/package acceptance pass | Source rebuild complete; executable validation remains pending code review/build-exe |

## 7. Error Handling, Safety, and Security

| Scenario | Expected handling | User-visible outcome | Verification |
|---|---|---|---|
| Invalid or damaged PDF | Reject open; preserve source | “Cannot open PDF” with filename and no false success | Unit test using malformed fixture |
| Wrong PDF password | Keep document closed | Password prompt or clear authentication failure | Integration test |
| Output write failure | Keep temporary file and source intact | Path, permission, disk-space guidance; no success claim | Unit test using unwritable destination |
| Existing destination selected for overwrite | Require explicit confirmation for every destination-producing workflow | Confirmed overwrite only; cancellation and failed writes preserve source/destination | UI and transaction tests |
| Invalid selected watermark pages | Reject before output creation or replacement | Named validation error; no partial or silently modified output | Unit test using zero, reversed, malformed, and out-of-bounds selections |
| Unsupported form field | Skip only unsupported field | Warning listing field names or types | Form fixture test |
| Extract no text or images | Return explicit no-match | “No extractable content found” | Test known image-only PDF |
| Large document or low memory | Cancel safely or show size warning | Source remains unchanged | Manual/fixture test |

## 8. Testing and Acceptance

| Test ID | Scenario | Expected result | Method |
|---|---|---|---|
| TEST-001 | Open and save unchanged document | Valid PDF reopens; page count and expected page image remain equivalent | Integration/manual |
| TEST-002 | Merge/split/rotate/reorder/delete | File structure and visual fixtures match requirement | Automated plus manual |
| TEST-003 | Text/image insertion and replacement | Applied content is visible at expected bounds after reopen | Automated image comparison |
| TEST-004 | Annotations, comments, and form values | Values survive reopen in app | Integration |
| TEST-005 | Password encryption/decryption | Correct password opens; incorrect password fails; source remains unchanged | Integration |
| TEST-006 | Text/image extraction | Results match fixture; no result produces explicit warning | Unit/integration |
| TEST-007 | Watermarks | Only selected pages contain the watermark; `0`, negative, non-numeric, malformed, duplicate, and out-of-bounds selections are rejected with `invalid-watermark-page-selection` without creating or replacing output | Automated page image comparison plus unit validation |
| TEST-008 | Invalid/corrupt/locked inputs | Safe, recoverable error and no output claims | Unit/UI |
| TEST-009 | Existing destination overwrite | Merge, split, reorder/delete, security, form, extraction, edit, annotation, rotation, and watermark destinations each require explicit confirmation; cancellation leaves source/destination unchanged; failed writes create no partial PDF | UI plus transaction tests |
| TEST-010 | Windows executable clean-machine launch | Launch and core open/save/merge workflow work without Python installed | Manual VM test |
| TEST-011 | Page-range grammar | `1-3,5,9-12` returns 8 unique pages; reversed, out-of-bounds, overlapping, duplicate, empty, whitespace, separate-output, and name-collision cases follow REQ-004 exactly | Unit |
| TEST-012 | Fixture baseline | Every listed baseline fixture opens or fails predictably; every required operation result is `pass`, `fail`, or `not-applicable`; supported annotations/forms save and persist after reopen in the application | Automated plus manual |
| TEST-013 | Reproducible packaging | Clean build from the pinned lockfile documents the same dependency set and launches on a clean Windows VM | Build automation/manual VM |

## 9. Critical Issues

| ID | Issue / unknown | Impact | Evidence / confidence | Proposed mitigation | Status | Review evidence |
|---|---|---|---|---|---|---|
| CRIT-001 | PDF-editing library, PDF feature coverage, and redistribution license have not been selected. | Wrong library may not support form fields, encrypted PDFs, or executable redistribution. | PyMuPDF provides the required editing surface, but redistribution terms require verification for the chosen distribution. | Select PyMuPDF for the implementation spike, pin its wheel/package version, and publish fixture/license evidence plus source and third-party notices. The executable may ship only under terms that explicitly permit redistribution. | Accepted resolution | Requirements re-review passed 2026-11-21 |
| CRIT-002 | Encryption, form handling, and annotation support vary by PDF implementation. | Visual or structural differences may appear in the output. | PDF files have broad dialect and encryption variations. | Limit baseline to PDF 1.7/standard AcroForm fixtures, SHA-256 fixture manifest entries, application-level round-trip checks, and explicit unsupported-feature warnings. | Accepted resolution | Requirements re-review passed 2026-11-21 |
| CRIT-003 | OCR and signature/XFA support are unclear. | User may expect OCR or signed/XFA workflows that this scope does not provide. | The selected scope includes text extraction but not OCR, digital signatures, or XFA editing. | Keep OCR, digital-signature editing, and XFA editing as explicit non-goals. Signed/XFA files may remain read-only if the library supports rendering. | Accepted resolution | Requirements re-review passed 2026-11-21 |
| CRIT-004 | Standalone Windows packaging can trigger antivirus warnings or require native runtime redistribution. | Executable may be blocked or report false positives. | PyInstaller official documentation describes OS-specific one-file/windowed distributions. | Ship both source and executable, test on clean Windows 10/11 VMs, publish SHA-256 and scan/build notes, and document allow-list or code-signing steps. Signing is not a runtime guarantee. | Accepted resolution | Requirements re-review passed 2026-11-21 |
| CRIT-005 | The save workflow does not preserve source files or provide a complete edit-and-save UI. | Required edits cannot be completed safely and source data may be lost. | The rebuilt UI now includes text, comment, highlight, underline, shape, freehand, image, and rotate controls wired to core APIs. | Save As uses the current working document and requires overwrite confirmation for source/destination collisions. | Implemented; code review required | Rebuild 2026-11-21 |
| CRIT-006 | Image replacement/removal uses redaction and destroys intersecting text. | Applying an image operation can permanently delete unrelated document content. | Confirmed by temporary-PDF runtime evidence for `core/images.py:13-20,23-29`. | Replace only the targeted image content and preserve intersecting text and other page content. | Accepted resolution; rebuild required | Requirements review 2026-11-21 |
| CRIT-007 | External PDF-viewer acceptance was part of the initial scope without available evidence. | External validation could block implementation despite not being required by the user. | The user confirmed that no Adobe Acrobat Reader validation use-case exists and that external-viewer validation should be removed. | Remove external PDF-viewer requirements from the initial scope; retain application-level fixture/viewer acceptance. | Resolved; scope correction accepted | Requirements re-review 2026-11-21 |
| CRIT-008 | The documented Python support was internally inconsistent. | Packaging and source builds could be validated against an unsupported or unstated runtime. | Section 5 now explicitly defines Python 3.12 through 3.15, inclusive as `>=3.12,<3.16`; `pyproject.toml` already declares that range. | Keep the range consistent in requirements and package metadata and require a change request for any range change. | Resolved; range accepted | Requirements re-review 2026-11-21 |
| CRIT-009 | The desktop UI does not expose several required PDF workflows. | Users cannot complete merge, split, reorder/delete, security, form, extraction, or watermark requirements through the application. | Core functions exist for some operations, but `ui/main_window.py:18-35` contained controls only for open/save and a subset of edit operations. | Add validated GUI workflows and acceptance coverage for every must-have scope operation. | Implemented; code review required | Rebuild 2026-11-21 |
| CRIT-010 | Page browsing and drag-and-drop do not satisfy the viewer/opening requirements. | 100-page navigation, direct page selection, and drag-and-drop open are missing. | `ui/viewer.py:7-29` previously had no thumbnails or page-number control; `ui/main_window.py:18-22` opened only through a file picker. | Add thumbnails/direct page navigation and drag-and-drop, or obtain an accepted requirements correction. | Implemented; code review required | Rebuild 2026-11-21 |
| CRIT-011 | Help/About does not include the required redistributable license and notice evidence. | REQ-016 and the packaging license constraint remain unmet, and bundled third-party terms may be undiscoverable or omitted. | The UI previously claimed bundled notices were present, but no third-party license or notice file was present. | Add discoverable license/notice data to the UI and package it with the executable, or use `/change-script` to change REQ-016 and re-review. | Implemented; code review required | Rebuild 2026-11-21 |
| CRIT-012 | Acceptance still required external cross-viewer validation after the initial-release scope removed it. | REQ-006 and TEST-004 could conflict with the application-only acceptance baseline and add an unapproved acceptance gate. | REQ-006 and TEST-004 have been corrected to application-level reopen and integration acceptance; Section 5 excludes external-viewer validation. | Keep external viewers outside initial-release scope. A later change request must add the viewer matrix and test owner. | Resolved; requirements correction applied | Requirements review 2026-11-21 |
| CRIT-013 | The documented fixture baseline required unsupported-feature coverage that was not part of the manifest category set. | The mismatch could prevent deterministic fixture acceptance or silently expand scope. | Section 5 now matches the manifest by excluding unsupported-feature fixtures from the mandatory initial baseline. | Keep unsupported/damaged feature behavior within explicit feature-specific warnings and reintroduce a dedicated fixture only through a change request. | Resolved; requirements correction applied | Requirements review 2026-11-21 |
| CRIT-014 | The fixture manifest records many required save/edit outcomes only as `not-tested`, rather than pass/fail evidence. | Section 5 requires per-fixture pass/fail open/edit/save operation metadata, and TEST-012 requires supported forms and annotations to persist after save/reopen. | `fixtures/pdf/manifest.json` marks form-save, annotation-save, image-extract, watermark, and thumbnail-navigation as `not-tested`, and the integration test validates file presence/hashes/page counts but does not perform save/reopen round trips. | Section 5 and TEST-012 now require machine-verifiable `pass`, `fail`, or `not-applicable` results and save/reopen round-trip assertions. | Resolved; requirements clarified | Requirements re-review passed 2026-11-21 |
| CRIT-015 | Duplicate watermark page selections have conflicting acceptance rules. | Duplicate handling may remain nondeterministic even though selected-page behavior is otherwise specified. | REC-013 proposes rejecting duplicate page selections, but REQ-013 and TEST-007 previously omitted duplicates. | REQ-013 and TEST-007 now reject duplicate values with `invalid-watermark-page-selection` and no output. | Resolved; requirements corrected | Requirements re-review passed 2026-11-21 |
| CRIT-016 | The text and image watermark UI references an overwrite variable that is not initialized. | Both watermark workflows raise `UnboundLocalError` and cannot create or save a destination PDF. | `ui/main_window.py:574-588` passed `overwrite=overwrite` without defining or confirming `overwrite`. | Initialize the overwrite decision only after selecting the destination, require explicit confirmation for existing destinations or source collisions, and pass one confirmed value to the core watermark API. | Resolved; rebuild implemented | Code review 2026-11-21 |
| CRIT-017 | Required text, image, and annotation operation parameters are hard-coded instead of exposed through validated controls. | Users cannot control required positions, bounds, font, size, color, opacity, stroke width, or selected image rectangles. | `ui/main_window.py:155-286` used fixed rectangles and fixed coordinate/point lists for text, annotation, and image operations. | Add validated controls for applicable operation parameters and selected page/rectangle values; preserve fixed defaults only where the control explicitly chooses them. | Resolved; rebuild implemented | Code review 2026-11-21 |

CRIT-001 through CRIT-004 are requirements decisions whose resolutions passed
requirements re-review on 2026-11-21. CRIT-005 and CRIT-006 are confirmed
implementation findings proposed for rebuild planning. CRIT-007 was resolved
by removing external PDF-viewer validation from the initial scope. CRIT-008
was resolved by accepting `>=3.12,<3.16`.

## 10. Recommendations

| ID | Recommendation | Benefit | Cost / trade-off | Proposed disposition | Status | Review evidence |
|---|---|---|---|---|---|---|
| REC-001 | Add searchable command-line equivalents for batch merge/split/extraction. | Enables automation and repeatable workflows. | Increases CLI design and test scope. | Defer as a post-GUI enhancement. | Accepted disposition: deferred | Requirements re-review passed 2026-11-21 |
| REC-002 | Add dark mode and configurable keyboard shortcuts. | Improves desktop usability. | Nonessential UI/test work. | Defer until core requirements pass. | Accepted disposition: deferred | Requirements re-review passed 2026-11-21 |
| REC-003 | Add a safe temporary backup/restore workflow. | Reduces edit-loss risk. | Additional disk use and cleanup behavior. | Accept if it does not change core PDF safety behavior. | Accepted disposition: accepted | Requirements re-review passed 2026-11-21 |
| REC-004 | Pin dependencies and verify package hashes in the build environment. | Improves reproducibility and supply-chain confidence. | Build maintenance and lock-file work. | Promote to a mandatory build acceptance requirement. | Accepted disposition: accepted | Requirements re-review passed 2026-11-21 |
| REC-005 | Implement source-overwrite protection for text edits and comments. | Prevents accidental source mutation and matches REQ-014. | Requires output-path transactions and explicit confirmation UI. | Save to a new filename by default; overwrite the source only after confirmation. | Accepted disposition: accepted | Code review 2026-11-21 |
| REC-006 | Implement highlight, underline, shape, freehand, and comment-author metadata. | Completes annotation requirements and preserves provenance. | Multi-quad highlight/underline geometry is now implemented for every supplied quad. | Reopen and persistence tests cover the rebuilt annotation implementations. | Implemented; code review required | Rebuild 2026-11-21 |
| REC-007 | Correct the page-range test count and rerun acceptance tests. | Restores an 8-page inclusive-range result and removes the failing unit assertion. | One test correction plus suite rerun. | Change `tests/unit/test_document.py:34` to expect 8 and rerun pytest. | Accepted disposition: accepted | Code review 2026-11-21 |
| REC-008 | Add baseline fixtures and integration/viewer acceptance evidence. | Demonstrates required document-fixture coverage. | Viewer matrix and external Viewer checks may require manual Windows validation. | Generate baseline fixtures, populate the manifest, and add integration tests; execute manual viewer checks when available. | Accepted disposition: accepted | Code review 2026-11-21 |
| REC-009 | Make fixture/viewer evidence machine-verifiable. | Prevents acceptance claims from relying on missing or stale metadata. | Adds manifest assertions and a maintained viewer-matrix record. | Extend the manifest and integration tests for dialect, page count, expected content/images/forms, pass/fail operations, text-only and malformed-AcroForm fixtures, and viewer versions/scope. | Implemented; requirements re-review required | 2026-11-21 correction |
| REC-010 | Give every review-log, change-request, and critical/recommendation record a unique, stable identifier. | Prevents ambiguous audit references and stale status updates. | Requires a requirements-document cleanup only. | Renumber duplicate FIND-018 through FIND-020 review-log entries; no behavior or test changes. | Resolved; requirements-only cleanup | Requirements re-review 2026-11-21 |
| REC-011 | Correct the build README's Python runtime wording to match the exact supported range. | Prevents source and package validation from targeting an unapproved runtime. | A requirements-only documentation correction. | Change `build/README.md:5` from `Python 3.12 or 3.15+` to `Python 3.12 through 3.15, inclusive (>=3.12,<3.16)`. | Accepted disposition; requirements-only correction recorded |
| REC-012 | Require overwrite confirmation and atomic PDF replacement for every destination-producing workflow. | Prevents accidental source/destination loss and partial-output success claims. | Adds explicit acceptance rules and rebuild verification work only. | Treat REQ-014 and TEST-009 as mandatory for merge, split, reorder/delete, security, form, extraction, edits, annotations, rotation, and watermarks; no source change is included in this requirements-only correction. | Requirements-only correction; implementation rebuild required | 2026-11-21 code review |
| REC-013 | Validate selected watermark pages before opening or replacing an output file. | Prevents silent selection of the wrong page and accidental output mutation. | Adds selected-page validation and acceptance coverage only. | Treat REQ-013 and TEST-007 as mandatory; reject zero, negative, non-numeric, malformed, duplicate, and out-of-bounds page selections without output. | Requirements-only correction; implementation rebuild required | 2026-11-21 code review |
| REC-014 | Make TEST-013 assert package-content parity and OS/runtime differences, not only dependency-set parity and launch. | Better verifies the stated reproducible-packaging constraint. | Requires build automation and clean-build evidence. | Proposed non-blocking test enhancement: require package manifests and documented OS/runtime differences to accompany the clean-build check. | Proposed; open | Requirements review 2026-11-21 |
| REC-015 | Initialize and verify one overwrite decision for the watermark destination. | Prevents the watermark workflow from crashing and prevents destination replacement without confirmation. | Adds one UI validation block and a focused runtime test. | In `ui/main_window.py`, define `overwrite=False`, confirm once when the destination exists or is the source, cancel on rejection, and pass the result to text and image watermark operations. | Resolved; rebuild implemented | Code review 2026-11-21 |
| REC-016 | Replace hard-coded edit geometry and styling with validated operation controls. | Enables the user-configurable behavior required by text, image, and annotation requirements. | Requires UI control updates and automated or manual parameter-validation coverage. | Add controls for text position/bounds/font/size/color, image target rectangle/proportional size, and annotation rectangle/quads/author/color/opacity/stroke width where applicable. | Resolved; rebuild implemented | Code review 2026-11-21 |
| REC-017 | Remove duplicate merge overwrite confirmation and make the decision singular. | Prevents contradictory confirmations and an overwrite reset before output replacement. | A small UI correction plus merge confirmation testing. | Delete the duplicate block in `ui/main_window.py:318-325`; set `overwrite=False`, confirm once if the selected destination exists, and pass that value once to `merge_pdfs`. | Resolved; rebuild implemented | Code review 2026-11-21 |

## 11. Change Requests

| ID | Request | Affected requirements/files | Acceptance criteria | Critical issues / recommendations | Status |
|---|---|---|---|---|---|
| CR-001 | Fix all findings and warnings from the 2026-11-21 code review. | REQ-004, REQ-006, REQ-009, REQ-014, TEST-003, TEST-004, TEST-009, TEST-011, TEST-012; `ui/main_window.py`, `core/document.py`, `core/annotations.py`, `core/images.py`, `tests/unit/test_document.py`, `tests/unit/test_rebuild_safety.py`, `tests/integration/test_fixture_acceptance.py`, `fixtures/pdf/manifest.json` | (1) Save As writes a valid selected output and source overwrite requires explicit confirmation. (2) Image replacement/removal changes only selected image content and preserves intersecting text. (3) Highlight, underline, shape, freehand, and comment annotations persist and comments store author metadata. (4) The 12-page `1-3,5,9-12` split returns 8 unique pages and the unit suite passes. (5) Deterministic baseline fixtures and manifest entries cover valid, damaged, encrypted, form, annotation, image, watermark, and 100-page documents; integration coverage is present. | CRIT-005, CRIT-006, REC-005, REC-006, REC-007, REC-008 | Implemented; code review required |
| CR-002 | Complete fixture acceptance evidence. | Section 5 fixture baseline; TEST-012; `fixtures/pdf/manifest.json`; `tests/integration/test_fixture_acceptance.py` | Manifest covers every required fixture category, per-fixture dialect/page/content/form metadata, operation outcomes, and SHA-256 hashes; text-only and malformed-AcroForm PDFs exist; integration tests verify the manifest and page counts. External-viewer validation is outside the initial scope. | CRIT-007, REC-009, FIND-025, FIND-026 | Resolved; requirements re-review passed |
| CR-003 | Correct FIND-030 and FIND-031 requirements-only findings. | REQ-013, REQ-014, TEST-007, TEST-009, Section 7, REC-012, REC-013 | (1) Every destination-producing workflow requires explicit confirmation before replacing a destination or source. (2) PDF outputs use atomic temporary-file/replacement behavior and failed writes leave no partial success. (3) Selected watermark pages use one-based positive integers, reject malformed and out-of-bounds values with a named error, and affect no unselected pages. No application source or executable changes are authorized by this requirements-only correction. | FIND-030, FIND-031, REC-012, REC-013 | Requirements corrected; implementation rebuild required |
| CR-004 | Fix the 2026-11-21 code-review findings for watermark runtime safety, configurable operation parameters, and merge overwrite confirmation. | REQ-005, REQ-006, REQ-009, REQ-013, REQ-014, TEST-003, TEST-004, TEST-007, TEST-009, `ui/main_window.py`; affected core APIs | (1) Text and image watermark workflows define and confirm overwrite state before output. (2) Text, image, and annotation controls expose and validate required parameters. (3) Merge uses exactly one explicit overwrite decision. (4) A runtime/UI test covers the corrected confirmation and parameter paths. | CRIT-016, CRIT-017, FIND-037, FIND-038, FIND-039, REC-015, REC-016, REC-017 | Implemented; code review required |

## 12. Review Findings and Resolution Log

| ID | Review stage | Finding and evidence | Linked requirement / CR | Proposed requirements fix | Status |
|---|---|---|---|---|---|
| FIND-001 | Requirements | PDF feature coverage, compatibility, and redistribution license had no implementation evidence. | CRIT-001 | Select and pin PyMuPDF after license/fixture verification. | Accepted resolution |
| FIND-002 | Requirements | No fixture manifest or cross-operation acceptance metadata was defined. | CRIT-002, TEST-001-TEST-013 | Add the fixture manifest and application-level round-trip acceptance metadata. | Accepted resolution |
| FIND-003 | Requirements | Password encryption mode, algorithm, owner/user roles, and minimum strength were unspecified. | REQ-010, TEST-005 | Require separate 12-character owner/user passwords, AES-256, and named permissions. | Accepted resolution |
| FIND-004 | Requirements | Packaging requested reproducibly but pinning/build commands remained optional. | REC-004, TEST-013 | Pin dependencies/runtime and make lockfile, build commands, and clean-build validation mandatory. | Accepted resolution |
| FIND-005 | Requirements | Split, image, and annotation semantics were not fully deterministic. | REQ-004, REQ-006, REQ-009 | Split, image, and annotation semantics are now specified. | Accepted resolution |
| FIND-006 | Requirements | Owner/user password roles and minimum password/key strength were unspecified. | REQ-010, TEST-005 | Require separate 12-character owner/user passwords, AES-256, and named permissions. | Accepted resolution |
| FIND-007 | Code review | The earlier review could not assess implementation because no implementation files were present at that time. | All requirements, TEST-001 through TEST-013 | Implementation is now present in partial form; reassess against requirements and rebuild if findings remain. | Superseded by FIND-009 through FIND-014 |
| FIND-008 | Implementation | REQ-004/TEST-011 said `1-3,5,9-12` produces 7 uniquely ordered pages, but inclusive counting produces 3 + 1 + 4 = 8 pages. | REQ-004, TEST-011 | Change the documented and test acceptance counts from 7 to 8 while retaining inclusive range semantics. | Resolved; requirements re-review required |
| FIND-009 | Code review | Save As does not save output and the desktop UI exposes no complete editing workflow. `ui/main_window.py:18-22,39-46` | REQ-001, REQ-014, TEST-001, TEST-009 | Implement the save transaction and connect validated operation controls to the core APIs. | Implemented; code review required |
| FIND-010 | Code review | Text insertion and comments call `saveIncr()` on the opened source path and ignore a separate output destination. `core/annotations.py:6-11,14-19` | REQ-014, TEST-001, TEST-009 | Default every edit to a new output; permit source overwrite only after explicit confirmation. | Implemented; code review required |
| FIND-011 | Code review | Image removal/replacement applies redactions to the selected rectangle, which also removes intersecting text. `core/images.py:13-20,23-29` Temporary-PDF evidence confirmed text loss. | REQ-006, TEST-003 | Remove or replace only image content while preserving unrelated text and page content. | Implemented; code review required |
| FIND-012 | Code review | The annotation module does not implement highlight, underline, shape, or freehand annotations; comment author metadata is also ignored. `core/annotations.py:1-47` | REQ-009, TEST-004 | Implement all required annotation types and persist author and applicable annotation metadata. | Implemented; code review required |
| FIND-013 | Code review | The unit test expects 7 pages for `1-3,5,9-12`, while inclusive ranges require 8. `tests/unit/test_document.py:34`; pytest returned 1 failed, 4 passed. | REQ-004, TEST-011 | Correct the expected count to 8 and rerun the unit suite. | Implemented; code review required |
| FIND-014 | Code review | Required PDF fixtures and integration/viewer evidence are absent. The fixture manifest has an empty list and no integration-test directory was found. | REQ-001-REQ-016, TEST-001-TEST-013 | Add the baseline fixtures, manifest hashes, integration tests, and viewer-matrix evidence before code review can pass. | Implemented; code review required |
| FIND-015 | Post-rebuild code review | The desktop UI exposes no edit-operation controls and Save As only copies the unchanged source. `ui/main_window.py:21-23,28-61` | REQ-001, REQ-005 through REQ-013, REQ-014, CRIT-005 | Add and wire validated editing controls to core APIs, preserving save-to-new-file and explicit overwrite behavior. | Implemented; code review required |
| FIND-016 | Post-rebuild code review | Highlight and underline functions use only `quads[0]` and silently discard additional regions. `core/annotations.py:55-77` | REQ-009, TEST-004, REC-006 | Apply every supplied quad or reject unsupported multi-quad input, and add geometry reopen tests. | Implemented; code review required |
| FIND-017 | Post-rebuild code review | `PdfViewer.open()` replaces `self.doc` without closing the prior PyMuPDF document. `ui/viewer.py:25` | REQ-001, REQ-002, REQ-015 | Close the previous document before opening a replacement and close it on window teardown. | Implemented; code review required |
| FIND-018 | Code review | The desktop UI has no controls or workflows for merge, split, page reorder/delete, encryption/decryption, form filling, text/image extraction, or watermarks. `ui/main_window.py:18-35` | REQ-003, REQ-004, REQ-008, REQ-010-013, TEST-002, TEST-005-007 | Wire validated GUI workflows to the existing core APIs or document an intentional implementation limitation only through an accepted requirements change. | Implemented; code review required |
| FIND-019 | Code review | The viewer provides previous/next and zoom only; it does not provide thumbnails or direct page-number navigation, and opening supports the file picker but no drag-and-drop. `ui/main_window.py:18-22, ui/viewer.py:7-29` | REQ-001, REQ-002, TEST-011-012 | Add thumbnail navigation and page-number entry, and implement drag-and-drop open if the approved requirement remains in scope. | Implemented; code review required |
| FIND-020 | Code review | Help/About claims bundled notices are present, but no third-party license or notice file is present in the implementation or executable specification. `ui/main_window.py:254-259, pdf_editor.spec:1-32` | REQ-016, CRIT-001, TEST-013 | Add discoverable license/notice data to the UI and package it with the executable, or change the requirement through `/change-script` and re-review. | Implemented; code review required |
| FIND-025 | Final code review | The fixture manifest contains hashes and names but not PDF dialect, page count, expected content, or pass/fail metadata. `fixtures/pdf/manifest.json:2`; integration tests do not validate this metadata or hash coverage. | REQ-001-REQ-016, TEST-012, REC-008 | Extend each manifest entry and viewer-matrix status with the required acceptance metadata and add hash/metadata assertions. | Resolved; requirements re-review passed |
| FIND-026 | Requirements re-review | The required fixture baseline is incomplete: the manifest previously lacked text-only and malformed-AcroForm fixture categories and some acceptance metadata. | Section 5 fixture baseline, TEST-012 | Add text-only and malformed-AcroForm fixtures plus per-fixture dialect/page/expected-content/form/operation metadata. External-viewer validation is excluded. | Resolved; requirements re-review passed |
| FIND-027 | Requirements re-review | The fixture files, manifest categories, hashes, and integration assertions have now been added, but prior external-viewer evidence was treated as required. | Section 5 viewer baseline, TEST-010, TEST-012 | Remove external-viewer validation from the initial-release requirements; application-level fixture acceptance remains required. | Resolved; external-viewer scope removed |
| FIND-030 | Code review | Existing destinations are overwritten without confirmation by merge, reorder/delete, encryption, decryption, form filling, text extraction, and watermark workflows. Save As alone confirms, and several core operations use direct `save()` or text `write_text()` instead of the atomic transaction. | REQ-014, Section 7 existing-destination rule, TEST-009 | Require explicit overwrite confirmation and atomic output for destination-producing workflows. | Resolved; rebuild implemented 2026-11-21 |
| FIND-031 | Code review | Selected watermark parsing accepts out-of-bounds and malformed page numbers. `0` is converted to index `-1`, so it silently applies to the last page of a document; other invalid values may silently affect no pages. | REQ-013, TEST-007 | Reject invalid selected watermark pages with `invalid-watermark-page-selection` before output creation. | Resolved; rebuild implemented 2026-11-21 |
| FIND-021 | Requirements re-review | Section 5 used open-ended supported-version wording while `pyproject.toml` declared `>=3.12,<3.16`. | Input constraints, TEST-013 | Document Python 3.12 through 3.15, inclusive, as `>=3.12,<3.16`, and require a change request for any range change. | Resolved |
| FIND-022 | Requirements re-review | `build/README.md:5` described `Python 3.12 or 3.15+`, which was not an exact requirements range. | CRIT-008, TEST-013 | Treat the requirements and `pyproject.toml` range `>=3.12,<3.16` as authoritative; build documentation requires a later explicit documentation correction. | Deferred; non-blocking implementation documentation |
| FIND-023 | Requirements re-review | The document previously declared Requirements review `Passed` while CRIT-009 and CRIT-010 remained unresolved rebuild blockers. | CRIT-009, CRIT-010, REQ-001, REQ-002, REQ-003, REQ-004, REQ-008, REQ-010 through REQ-013 | Keep implementation rebuild blocked; requirements review may pass independently once scope and acceptance criteria are complete. Set Requirements review to `Passed` and retain rebuild/code-review blocking statuses. | Resolved; requirements-only correction |
| FIND-024 | Requirements re-review | The Help/About UI and executable specification lack the third-party license and notice data required by REQ-016 and CRIT-001. | REQ-016, CRIT-001, TEST-013 | Add and package discoverable notices, or revise REQ-016 through `/change-script` and re-review. | Implemented; code review required |
| FIND-028 | Requirements re-review | The requirements still contain three unresolved critical implementation blockers: required GUI workflows are not exposed (CRIT-009), viewer/thumbnails/direct page navigation/drag-and-drop are missing (CRIT-010), and redistributable notices are absent (CRIT-011). | REQ-001, REQ-002, REQ-003, REQ-004, REQ-008, REQ-010 through REQ-013, REQ-016, TEST-010, TEST-012-013 | Preserve rebuild blocking until CRIT-009 through CRIT-011 are resolved and re-reviewed; set Requirements review to `Failed` while implementation behavior remains unresolved. | Open; requirements review failed |
| FIND-029 | Requirements correction | CRIT-009 through CRIT-011 and REC-011 now have explicit requirements-only dispositions. GUI workflows, complete viewer navigation, and redistributable notices remain rebuild requirements; implementation status is not represented as complete. | CRIT-009, CRIT-010, CRIT-011, REC-011 | Retain rebuild required for implementation; retain passed requirements review for the now-deterministic scope and acceptance requirements. | Accepted; requirements-only correction |
| FIND-032 | Requirements correction | REQ-006 and TEST-004 retained external cross-viewer acceptance language although Section 5 and FIND-027 removed external-viewer validation from the initial release. | REQ-006, TEST-004, Section 5, FIND-027 | Application-level reopen and integration acceptance now replace external-viewer wording. | Resolved; requirements correction applied |
| FIND-033 | Requirements correction | Section 5 mandated an unsupported-feature fixture baseline, but the fixture manifest has no unsupported-feature category or operation result. | Section 5 fixture baseline, TEST-012, `fixtures/pdf/manifest.json` | The unsupported-feature category was removed from the mandatory baseline; feature-specific unsupported behavior remains governed by Section 2 and Section 7 warnings. | Resolved; requirements correction applied |
| FIND-034 | Requirements re-review | The fixture manifest is machine-readable but still records several operation outcomes as `not-tested`, and the integration test does not perform the affected save/reopen assertions. This is implementation evidence status, while Section 5 and TEST-012 now clearly require final `pass`, `fail`, or `not-applicable` outcomes and save/reopen round trips. | Section 5 fixture manifest, TEST-012, `fixtures/pdf/manifest.json`, `tests/integration/test_fixture_acceptance.py` | Keep the requirements/acceptance correction; treat the remaining `not-tested` evidence as a rebuild/code-review blocker and require it to become a machine-verifiable pass/fail/not-applicable outcome before implementation approval. | Resolved as requirements clarification; implementation evidence remains rebuild-required |
| FIND-035 | Requirements correction | Duplicate watermark page selections were not defined by REQ-013 or TEST-007 even though REC-013 proposes rejecting them. | REQ-013, TEST-007, REC-013 | REQ-013 and TEST-007 now reject duplicates with `invalid-watermark-page-selection` and no output. | Resolved; requirements re-review passed |
| FIND-036 | Requirements re-review | The reviewed document has complete must-have scope and acceptance language for the remaining requirements; open implementation defects and recommendation REC-014 do not conflict with the requirements. `not-tested` fixture entries and rebuild blockers are implementation/evidence issues, not unresolved specification decisions. | CRIT-005, CRIT-006, CRIT-009 through CRIT-011, CRIT-014, CRIT-015, REC-014 | Set Requirements review to `Passed`; preserve Rebuild required, Code review Failed, and Packaging Not authorized until implementation evidence passes code review. | Accepted; requirements review passed |
| FIND-037 | Code review | The text and image watermark UI invoked `overwrite=overwrite` in `ui/main_window.py:574-588` without defining `overwrite`. Both text and image watermark actions raised `UnboundLocalError` instead of creating or saving output. | REQ-013, TEST-007, TEST-009 | Initialize and confirm the watermark destination before calling the core APIs, then pass the confirmed overwrite state. | Resolved; rebuild implemented |
| FIND-038 | Code review | Text, annotation, highlight, underline, shape, freehand, and image controls used fixed rectangles/point lists and did not provide required position, size, font, color, opacity, or target-rectangle controls. `ui/main_window.py:155-286` | REQ-005, REQ-006, REQ-009, TEST-003, TEST-004 | Add validated operation controls for position/bounds and applicable text/image/annotation parameters, rather than hard-coded coordinates and defaults. | Resolved; rebuild implemented |
| FIND-039 | Code review | Merge asked for destination overwrite confirmation in two consecutive blocks, which could contradict earlier confirmation and reset `overwrite` before the final decision. `ui/main_window.py:318-325` | REQ-014, TEST-009 | Remove the duplicate confirmation block and use one explicit confirmed overwrite decision for the merge destination. | Resolved; rebuild implemented |
| FIND-040 | Requirements re-review | Every requirement row remains labeled `Proposed` even though the requirements review and acceptance scope are declared passed. This creates stale status language and could make an approved requirement appear unresolved. | Section 4 requirement statuses, Section 13 review gate | Mark reviewed must/should requirements as `Accepted` in the requirement table while preserving implementation and code-review rebuild states as separate gates. | Resolved; requirements status corrected |
| FIND-041 | Code review | Encrypted PDFs cannot enter the application workflow. `open_pdf()` rejects `needs_pass` and `decrypt_document()` does not accept a locked file unless it is already open, while `open_document_path()` calls `open_pdf()` first. As a result, an encrypted PDF has no reachable decrypt workflow and cannot be opened with a user or owner credential in the UI. | REQ-001, REQ-010, TEST-005 | Add a password-aware open/decrypt path that authenticates the correct user or owner password, keeps the document closed on failure, and verifies decrypt output; then expose it through the UI. | Resolved; rebuild implemented |
| FIND-042 | Code review | The text-edit workflow exposes position, size, and RGB controls but no font choice, and `insert_text()` ignores the character-fit result returned by `insert_textbox()`. Oversize text can therefore be clipped without an error or warning even though REQ-005 requires text to render within the selected bounds. | REQ-005, TEST-003 | Add font selection/validation where supported and reject or warn when `insert_textbox()` reports overflow; add an acceptance test that verifies text remains inside the bounds after reopen. | Resolved; rebuild implemented |
| FIND-043 | Code review | AcroForm filling supports text and common choice widgets but explicitly treats signature fields as unsupported, and the UI exposes no signature-placeholder workflow. The malformed-field warning path is implemented, but supported signature-placeholder filling remains absent. | REQ-011, TEST-004, TEST-012 | Implement the supported signature-placeholder behavior or clearly isolate and test it as unsupported; ensure the UI lists and warns about it consistently with the requirement. | Resolved; rebuild implemented |
| FIND-044 | Code review | The fixture manifest previously recorded save/reopen, form, image extraction, watermark, 100-page navigation, and annotation outcomes as `not-tested`, and `viewer_matrix` was empty. Rebuild 2026-11-21 replaced placeholders with operation outcomes and added save/reopen round-trip assertions for forms, annotations, image extraction, and watermarks. | TEST-002 through TEST-012, Section 5 | Replace `not-tested` entries with machine-verifiable `pass`, `fail`, or `not-applicable` outcomes and assert the required operation/viewer round trips. | Resolved; rebuild/evidence implemented |
| FIND-045 | Code review | No Windows executable or clean-machine VM evidence is present for TEST-010 or TEST-013. The suite only verifies Python source behavior, and the build README remains packaging documentation rather than executed acceptance evidence. Re-review 2026-11-21: no executable or VM evidence was run or added. | TEST-010, TEST-013, Phase 5 | Perform clean Windows source/build checks and a clean-machine launch test, or explicitly record the unavailable checks as accepted limitations in the requirements. | Open; packaging blocked |
| FIND-046 | Code review | Image extraction previously wrote each Pixmap directly to its final `.png` path and lacked an atomic replacement transaction. Rebuild 2026-11-21 changed it to temporary-file save plus `os.replace`, destination confirmation, and temporary cleanup on failure. | REQ-014, TEST-009 | Extract each image to a temporary file in the destination directory and atomically replace each final image only after a confirmed overwrite decision; remove temporary files on failure and add a failure-transaction test. | Resolved; rebuild implemented |
| FIND-047 | Implementation rebuild | Text watermark runtime validation used a 45-degree rotation unsupported by PyMuPDF's `insert_text()` API. The first rebuild validation failed; the source was corrected to omit the unsupported rotation and rerun successfully. | REQ-013, TEST-007 | Use only supported PyMuPDF text insertion parameters and retain validated selected-page behavior. | Resolved; rebuild implemented |

## 13. Review and Build Gate

- **Requirements review:** Passed. FIND-034, FIND-035, and FIND-040 are resolved by explicit
  requirements and acceptance corrections. Remaining `not-tested` fixture evidence
  and implementation rebuild items are not unresolved requirements decisions.
- **Requirements review findings:** CRIT-012 through CRIT-015 are resolved in
  requirements text. REC-014 remains an open non-blocking packaging-test recommendation.
  CRIT-016 through CRIT-017 and REC-015 through REC-017 were implementation
  findings and are rebuilt; they do not change the approved requirements.
- **Critical issue gate:** CRIT-007 is resolved by removing external viewer
  validation from the initial-release scope. CRIT-008 is resolved by accepting
  `>=3.12,<3.16`. CRIT-009, CRIT-010, and CRIT-011 now have accepted
  requirements-only resolutions and remain rebuild items, not unresolved
  requirements decisions. FIND-022 is deferred as non-blocking build documentation.
- **Implementation authorization:** Rebuild of CRIT-016,
  CRIT-017, FIND-037 through FIND-039, REC-015 through REC-017, and the
  associated implementation acceptance coverage was completed for FIND-041
  through FIND-043.
- **Implementation:** Current. Password-aware open, text font/fit validation,
  and signature-field handling were rebuilt and unit-tested.
- **Code review:** Passed 2026-11-22. No actionable implementation defects
  remain in the source review; source compilation and 24 pytest tests passed.
- **Packaging:** Authorized. `/build-exe` may now validate the standalone
  executable and clean-machine evidence required by TEST-010 and TEST-013.
- **Implementation record:** CR-004 rebuild implemented operation parameter controls,
  watermark overwrite safety, and merge overwrite confirmation. The rebuild added merge, split, reorder/delete,
  encryption/decryption, form, extraction, and text/image watermark workflows
  to `ui/main_window.py`; thumbnails, direct page entry, and drop-open hooks to
  `ui/viewer.py`; image watermark support to `core/annotations.py`; and
  packaged third-party notices to `pdf_editor.spec` and
  `THIRD_PARTY_NOTICES.md`. `ui/main_window.py` now exposes validated text,
  comment, highlight, underline, shape, freehand, insert/replace/remove-image
  parameters and confirms watermark and merge overwrite decisions once.
- **Test record:** `python -m compileall -q core ui pdf_editor.py tests` passed
  on 2026-11-22.
  `python -m pytest tests/unit tests/integration` passed 24 tests on
  2026-11-22, with one PyMuPDF
  deprecation warning. Remaining limitation: executable clean-build and
  manual clean-VM evidence are not available under TEST-010/TEST-013.
  The source rebuild requires separate `/review-script` code review before packaging.
- **Rebuild implementation paths:** Destination overwrite guards and atomic
  save/replace behavior were rebuilt in `core/document.py`,
  `core/security.py`, `core/forms.py`, `core/images.py`, and
  `core/annotations.py`. Text extraction uses atomic export in
  `core/extraction.py`; affected UI workflows confirm existing destinations in
  `ui/main_window.py`.
- **Checks:** `python -m compileall -q core ui pdf_editor.py` passed.
  `python -m pytest` passed with 20 tests and 1 PyMuPDF
  deprecation warning on 2026-11-21. Windows clean-build and clean-machine
  executable checks were not available in this review.

## 14. Assumptions and Decisions

| ID | Assumption or decision | Owner | Status | Evidence / date |
|---|---|---|---|---|
| DEC-001 | The primary interface is a Windows desktop GUI. | User | Accepted for draft | User response 2026-11-21 |
| DEC-002 | Source and a standalone Windows executable are requested. | User | Accepted for draft | User response 2026-11-21 |
| DEC-003 | PDF text/image extraction and watermarks are in scope. | User | Accepted for draft | User response 2026-11-21 |
| DEC-004 | OCR, digital signatures, and XFA editing are not in scope without later change requests. | Project | Proposed resolution | 2026-11-21; CRIT-003 |
| DEC-005 | Page rendering and editing use PyMuPDF rather than handwritten PDF parsing, subject to license and fixture verification. | Project | Proposed resolution | 2026-11-21; CRIT-001 |

## 15. References

- [PyMuPDF: Text Recipes](https://pymupdf.readthedocs.io/en/latest/recipes-text.html),
  accessed 2026-11-21. Official candidate-library documentation for text,
  image, annotations, forms, page, and document operations.
- [PyInstaller: Operating Mode](https://pyinstaller.org/en/stable/operating-mode.html),
  accessed 2026-11-21. Describes OS-specific bundles, one-file executables,
  and the fact that users do not need Python installed.
