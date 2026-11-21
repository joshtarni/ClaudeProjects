---
name: change-script
description: "Manage a change request for an existing script project under projects/<script-name> by recording it in requirements.md, analyzing impacts and risks, and routing it through requirements review, explicit implementation, code review, and final packaging gates."
argument-hint: "Describe the requested change and identify its projects/<script-name> folder"
---

# Manage a Script Change Request

Record and plan a user-requested change against an existing
`projects/<script-name>/requirements.md`. This skill does not implement source
code, run a build, or package an executable.

## Workflow

1. **Locate and inspect the project.**
   - Read the existing `requirements.md`, source tree, tests, current workflow
     status, and relevant changes.
   - If the project or requirements file cannot be identified, ask which one.
     Never create a competing project or silently choose the wrong script.
2. **Create a traceable Change Request (CR).**
   - Append the next unique `CR-NNN` entry in the requirements document's
     Change Requests table. Preserve previous CRs and decisions.
   - Record the user's intent, affected requirement IDs/files, measurable
     acceptance criteria, dependencies, risks, tests, and implementation phase
     impact.
   - Add or update requirement rows and critical/recommendation items as needed.
     Do not rewrite unrelated requirements or mark a concern resolved without
     evidence and review.
   - Update the proposed script scaffold table for the change. Check off `[x]`
     existing deliverables only when their behavior remains verified; add `[ ]`
     rows or update row phases/states for new, rebuilt, renamed, tested, or
     packaged deliverables. Link every affected row to its requirement and test
     IDs.
3. **Analyze and propose fixes.**
   - Inspect current behavior and use authoritative documentation for external
     APIs, formats, platform rules, and security-sensitive claims.
   - Identify breaking changes, migration needs, compatibility, failure modes,
     and test coverage. Propose a concrete mitigation for every critical issue.
   - Distinguish blockers from optional recommendations and state trade-offs.
4. **Route through the review gates.**
   - Update review/build status in `requirements.md`: new or affected
     requirements require requirements review; critical issues block
     implementation until resolved and review passes.
   - Invalidate downstream approvals when the CR changes their basis. Mark
     implementation `Rebuild required` if already-built behavior is affected,
     reset code review to `Not reviewed`, requirements review to `Not reviewed`,
     overall status to `Draft`, and packaging to `Not authorized`.
   - Recommend `/review-req` to validate the revised specification. Iterate
     requirement fixes and `/review-req` until it passes. Recommendations may be
     accepted, deferred, or rejected by the user with rationale.
   - Do not implement code merely because the CR is documented or reviewed.
     Wait for an explicit request to run `/build-script` against the reviewed
     requirements (for example, “build based on this requirements.md”).
   - After implementation, `/review-script` is required. Code findings must be
     recorded in `requirements.md`, set implementation to `Rebuild required`,
     and invalidate prior review approval. Re-review the revised requirements;
     only an explicit user-requested rebuild may regenerate code.
   - `/build-exe` is the final packaging step, only after requirements and code
     reviews pass and implementation is current.
5. **Report the CR.**
   - Link `requirements.md`, state the CR ID, affected requirements, proposed
     mitigations, unresolved blockers, and the next required gate.
   - Render critical issues and recommendations with their proposed actions
     directly in the chat response. Do not use `requirements.md` as a substitute
     for presenting the choices available to the user.
   - State that no application code or executable was created.

## Safety Boundaries

- Do not overwrite or remove existing project files or CR history.
- Do not infer approval to implement, rebuild, or package from a change request.
- If requirements conflict with each other or the user's request, record the
  conflict and ask for the decision that changes scope or behavior.
