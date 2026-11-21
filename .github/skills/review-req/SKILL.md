---
name: review-req
description: "Review a script project's requirements, scaffold, risks, critical issues, recommendations, and acceptance criteria only. Use after /new-script or /change-script, or to re-review corrected requirements; propose /build-script eligibility only when no critical findings remain, and never implement or build source."
argument-hint: "Name the projects/<script-name>/requirements.md file to review"
---

# Requirements Review

This skill has one purpose: review the named requirements document. It does not
review application source, rebuild code, package an executable, or start the
next workflow skill.

## Procedure

1. Locate the exact `projects/<script-name>/requirements.md` named by the user.
   If ambiguous, ask which project. Read the full document and relevant
   Change Requests, source file list, review history, assumptions, and
   official references needed to evaluate it.
2. Set `Requirements review` to `In progress`. Do not change implementation,
   code-review, or packaging approvals unless the requirements correction
   invalidates them.
3. Evaluate the specification for:
   - internal consistency and testability
   - completeness of the scaffold and acceptance checks
   - unresolved critical decisions or material risks
   - contradictions, missing failure behavior, security/privacy issues,
     unsupported assumptions, and stale references
   - whether existing or proposed requirements genuinely match the user's
     requested behavior
4. Report only evidence-backed findings. Separate confirmed findings from
   assumptions or unverified risks. Include direct evidence and a concrete
   proposed correction for each finding.
5. Update the requirements document audit trail only:
   - add or update findings in `Review Findings and Resolution Log`
   - update critical issues and recommendations
   - record accepted decisions or unresolved choices without inventing approval
   - invalidate implementation, code-review, and packaging status when a
     relevant requirements change invalidates them
   - set `Requirements review` to `Passed` only when no unresolved critical
     issue or blocking decision remains; otherwise set it to `Failed`
   - do not edit application source, tests, executable files, build outputs, or
     any other implementation artifact in this skill
   - proposed fixes may be added only to `requirements.md`; implementation
     of those fixes belongs to a later explicit `/build-script` request
6. Render the complete finding and proposal summary in chat. Do not require the
   user to open `requirements.md` to see the scaffold, critical issues, or
   recommendations.

## Status Rules

- `Passed` means the requirements are ready for an explicit implementation
  decision. It does not authorize `/build-script` or packaging.
- `Failed` or `Needs user decision` means implementation remains blocked.
- Recommendations are non-blocking only; an open recommendation does not
  prevent `Passed` when no unresolved critical issue or blocking decision
  remains. If a recommendation is promoted to a requirement or becomes
  blocking, move it to the Critical Issues table and keep implementation
  blocked until accepted and reviewed.
- A correction made after a passing review invalidates that pass and must be
  re-reviewed with this skill.
- Re-reviewing the corrected document is a separate user prompt.
- When a requirements change affects implemented behavior, set implementation
  to `Rebuild required` and code review to `Not reviewed`.

## Review Output

End the report with:

1. `## Review Decision`
   - state `Passed`, `Failed`, or `Needs user decision`
   - state whether implementation remains blocked and the next user-controlled
     gate
2. `## Proposed Script Scaffold`
   - Markdown table with `Scaffold item`, `Function / deliverable`,
     `Requirement / test IDs`, `Phase`, and `State`
   - use `[x]` only for existing, evidenced deliverables and `[ ]` for planned,
     missing, incomplete, or unverified deliverables
3. `## Critical Issues`
   - columns `ID`, `Issue`, `Impact`, `Evidence / confidence`, `Proposed fix`,
     `Status`
   - write `None identified` if empty
4. `## Recommendations (Warnings)`
   - columns `ID`, `Warning`, `Benefit`, `Cost / trade-off`, `Proposed action`,
     `Status`
   - write `None identified` if empty
   - for every recommendation left open, state the concrete requirements-only
     fix or disposition proposed; distinguish proposed from accepted
   - list any recommendation accepted into scope as a requirements/test change,
     or explicitly deferred/rejected as non-blocking
5. Add a brief `## Next Prompt`
   - if failed: "Fix [critical/warning IDs] in requirements, then invoke
     `/review-req` again."
   - if passed: state "No unresolved critical findings remain. `/build-script`
     is now available for you to prompt explicitly to implement the named,
     reviewed requirements; I will not start it as part of this review."
     Then separately state whether any recommendations remain and their
     proposed requirements-only fixes or dispositions.

Do not ask which findings to fix inside this skill. Do not treat a user's
request for a review as authorization to edit source or requirements. Requirements
may be edited during this skill only to record review evidence and proposed
corrections; application source edits require a separate explicit implementation
request. Fixes selected for implementation must be specified in
`requirements.md`, then implemented only after the user separately prompts
`/build-script`. Never invoke `/build-script` automatically or imply that passing
the review starts implementation.
