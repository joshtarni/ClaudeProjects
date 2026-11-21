# Repository Agent Instructions

## Project Layout

- Script projects live in `projects/<script-name>/`.
- Each project has a `requirements.md` that records behavior, acceptance
  criteria, critical issues, recommendations, Change Requests, review history,
  implementation status, and packaging status.
- The adopted Screen Area Recorder is at `projects/screen-recorder/`:
  - Source: `screen_recorder.py`
  - Runtime dependencies: `requirements.txt`
  - Executable: `dist/ScreenRecorder.exe`
  - Workflow specification: `requirements.md`
  - Historical notes: `EXPERIENCE.md`
- Its implementation predates this workflow. Its `requirements.md` is an
  adopted baseline, not evidence that the implementation has already passed
  requirements or code review.
- The repository-level `README.md` is the entry point; keep paths and commands
  there aligned with the project layout.

## Workflow and Authorization

Follow the project's on-demand skills; do not skip gates or infer approval:

1. `/new-script` creates a project folder and `requirements.md` only. It must
   not create application source or build artifacts.
2. `/change-script` records requested changes as traceable CR items in the
   existing project's `requirements.md`; it does not implement code.
3. `/review-req` checks only the requirements, scaffold, risks, and acceptance
   criteria. `/review-script` checks only implemented source against the passed
   requirements and tests.
4. Application source may be implemented or rebuilt only when the user
   explicitly requests `/build-script` for a named requirements file and its
   requirements review passes with no unresolved critical issues.
5. After implementation, `/review-script` must review the resulting code.
   Findings invalidate downstream approvals and require requirements updates,
   `/review-req` re-review, or an explicitly authorized rebuild as applicable.
   Source-only fixes keep a current requirements pass; requirements-changing
   fixes require `/review-req` to pass again before rebuilding.
6. `/build-exe` is packaging only. Run it only when implementation is current,
   code review passed, and packaging is authorized in `requirements.md`. It
   must verify the generated executable and record packaging completion only
   after a successful build.

A skill invocation is not permission to skip that skill's preconditions.
Planning, requirements review, implementation, code review, and packaging are
separate user-controlled phases. Do not silently combine them or claim a phase
passed without performing its checks. A review skill ends after its report;
it must not invoke implementation, rebuilding, re-review, or packaging.

## Evidence and Changes

- Treat user requirements and approved `requirements.md` criteria as the
  acceptance baseline. Record assumptions and unresolved decisions instead of
  inventing behavior.
- Prefer official, current documentation for external APIs, formats, and
  platform rules. Cite sources in the requirements or review record.
- Run the narrowest relevant tests and report exactly what passed, failed, or
  could not be verified.
- Preserve unrelated worktree changes. Never overwrite an existing project or
  requirements file without user approval.
- Update project docs and workflow status when behavior, paths, or build
  outputs change.
