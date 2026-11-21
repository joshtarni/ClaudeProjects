---
name: build-script
description: "Implement or rebuild a script project from its reviewed projects/<script-name>/requirements.md after the user explicitly requests implementation. Use for 'build based on requirements.md'; do not package a standalone executable."
argument-hint: "Name the reviewed projects/<script-name>/requirements.md to implement"
---

# Implement a Script from Reviewed Requirements

This is the implementation/rebuild step for projects managed by `/new-script`
and `/change-script`. It changes application source only after the user
explicitly asks to build or implement from the named requirements document.
It does not package an executable; `/build-exe` is a separate final step.

## Preconditions

1. Locate the exact `projects/<script-name>/requirements.md` named by the user.
   If ambiguous, ask which project. Never choose a different project silently.
2. Read the full requirements, CR history, Review Findings and Resolution Log,
   Document Control, implementation plan, relevant source, tests, and current
   worktree/diff.
3. Confirm all of the following before editing application source:
   - `Requirements review` is `Passed`.
   - No critical issue or blocking decision is unresolved.
   - If this is a rebuild after code findings, each finding is recorded and
     resolved in the requirements, the updated requirements review has passed,
     and this user request explicitly authorizes the rebuild.
   - The user's prompt explicitly requests implementation from this
     requirements document. Merely invoking `/new-script`, `/change-script`,
     or `/review`, or asking to prepare/revise the plan, is not authorization.
   - For an adopted legacy project whose implementation status is
     `Existing; review required`, requirements review and code review must
     first pass before a requested change/rebuild can proceed. Preserve its
     behavior outside the approved Change Requests.
4. If a precondition fails, do not edit application source. Explain the failed
   gate and direct the user to `/review` or the missing decision.

## Implementation Procedure

1. Set implementation to `Authorized`, then `In progress`; set `Code review` to
   `Not reviewed` and `Packaging` to `Not authorized`. Update the overall status
   and implementation phase table to reflect active work.
2. Implement only the approved requirements and accepted Change Requests.
   Preserve existing behavior outside their scope. Follow project conventions,
   use authoritative references for external behavior, and do not invent
   undocumented API behavior.
3. Add or update tests for each affected acceptance criterion. Run the
   narrowest relevant tests first, then required project checks. Report failed
   or unavailable checks; do not claim unverified behavior works.
4. Update `requirements.md` with the actual implementation paths, completed
   phases, test commands/results, and any remaining limitations. When all
   approved acceptance criteria are implemented and checks pass, set
   `Implementation` to `Current`, `Code review` to `Not reviewed`, and
   `Packaging` to `Not authorized`. Set the overall status to `Implementation
   complete; code review required`.
5. If implementation reveals a material requirement gap or unresolved
   decision, stop rather than silently changing scope. Record the evidence and
   proposed requirement correction in the findings log, set Requirements
   review to `Not reviewed`, Code review to `Not reviewed`, Packaging to `Not
   authorized`, and the overall status to `Draft`. Ask the user to resolve the
   decision or run `/review` on the updated requirements before continuing.
6. Hand off for `/review` code review. Do not invoke `/build-exe` or create a
   standalone executable in this skill.

## Rebuilds After Code Review

When `/review` finds code defects, it must record evidence and the proposed
requirements correction, set implementation to `Rebuild required`, invalidate
code-review and packaging approvals, and require a passing requirements review
if the specification changed. Only after those gates pass and the user
explicitly asks for a rebuild may this skill update the application source.
After rebuilding, code review must pass again before `/build-exe` can package
it.

## Report

Summarize implemented requirements and CR IDs, changed application files,
checks performed and results, remaining limitations, and the next gate:
`/review` code review. State that no standalone executable was packaged.
