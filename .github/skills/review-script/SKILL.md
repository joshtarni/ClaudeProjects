---
name: review-script
description: "Review implemented script source against a passed requirements document and tests. Use after /build-script to report code findings, propose requirements corrections, and set the code-review and rebuild gates."
argument-hint: "Name the implemented projects/<script-name>/ and its requirements.md"
---

# Code Review

This skill reviews the implemented application after `/build-script`. It does
not implement fixes, rebuild source, package an executable, or invoke another
skill automatically.

## Preconditions

1. Locate the named project and read its full `requirements.md`, source,
   tests, worktree/diff, and review history.
2. Require `Requirements review: Passed` and no unresolved critical issue.
   A code review may inspect existing code for an adopted project only after
   the requirements gate has passed.
3. Set `Code review` to `In progress` before starting evidence collection.

## Procedure

1. Compare behavior, interfaces, error handling, security, dependencies, and
   test coverage against the approved requirements and acceptance tests.
2. Inspect the current diff or relevant source so pre-existing changes are not
   mistaken for findings. Run the narrowest relevant tests, syntax checks,
   builds, or runtime checks when available.
3. Report only actionable implementation defects or material gaps. Include exact
   file locations, impact, evidence, confidence, and a concrete correction or
   verification step.
4. Do not claim checks passed unless they were actually run. Report failed or
   unavailable checks explicitly.
5. If any actionable finding remains:
   - set `Code review` to `Failed`
   - set `Implementation` to `Rebuild required`
   - set `Packaging` to `Not authorized`
   - set overall `Status` to `Rebuild required`
   - leave `Requirements review: Passed` unchanged for a source-only defect
   - set `Requirements review` to `Not reviewed` if a finding requires a
     requirements correction or a previously approved requirement to change
   - record evidence and the proposed correction in
     `Review Findings and Resolution Log`
   - update linked requirements or Change Requests without weakening the user's
     intent
6. If no actionable finding remains and required checks pass (or limitations
   are explicitly accepted in the requirements):
   - set `Implementation` to `Current`
   - set `Code review` to `Passed`
   - set `Packaging` to `Authorized`
   - set overall `Status` to `Ready to package`
7. Return a short report and do not patch source, invoke `/build-script`,
   invoke `/review-req`, or invoke `/build-exe`.

## Review Output

End the report with:

1. `## Review Decision`
   - `Passed` or `Failed`
   - downstream implementation, requirements-review, and packaging gates
2. `## Proposed Script Scaffold`
   - compare the requirements scaffold to the actual file structure
   - Markdown table with `Scaffold item`, `Function / deliverable`,
     `Requirement / test IDs`, `Phase`, and `State`
   - mark missing, extra, moved, or unverified items explicitly
3. `## Critical Issues`
   - implementation findings that block correctness or safety
4. `## Recommendations (Warnings)`
   - non-blocking improvements and their proposed disposition
5. `## Next Prompt`
   - failed with source-only changes: "Explicitly invoke `/build-script` to
     rebuild from the unchanged, passing requirements."
   - failed with requirements changes: "Use `/change-script` or correct the
     named requirements, then invoke `/review-req` and wait for it to pass."
   - passed: "Invoke `/build-exe` only if you want the standalone executable."

Do not modify application source in this skill. If the user subsequently gives
an explicit fix or rebuild prompt, perform only that authorized scope and return
a change report. Re-running code review requires a separate `/review-script`
prompt.
