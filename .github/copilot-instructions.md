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
3. `/review` checks requirements or implementation against the requirements,
   verifies evidence and authoritative references as needed, and updates the
   requirements document's findings and status fields.
4. Application source may be implemented or rebuilt only when the user
   explicitly requests `/build-script` for a named requirements file and its
   requirements review passes with no unresolved critical issues.
5. `/review` must review the resulting code. Findings invalidate downstream
   approvals and require requirements updates/re-review and an explicitly
   authorized rebuild.
6. `/build-exe` is packaging only. Run it only when implementation is current,
   code review passed, and packaging is authorized in `requirements.md`. It
   must verify the generated executable and record packaging completion only
   after a successful build.

A skill invocation is not permission to skip that skill's preconditions.
Planning, requirements review, implementation, code review, and packaging are
separate phases. Do not silently combine them or claim a phase passed without
performing its checks.

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
