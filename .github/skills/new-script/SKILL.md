---
name: new-script
description: "Start a new script project from a user description by creating projects/<script-name>/requirements.md with implementation plans, critical issues, recommendations, proposed mitigations, and review gates. Use when planning a new script; do not implement code until explicitly asked to build from the approved requirements."
argument-hint: "Describe the script you want to create"
---

# Plan a New Script

Turn the user's description into a reviewable specification. This skill creates
the project folder and `requirements.md`; it does not create application source,
run a build, or package an executable.

## Workflow

1. **Understand the request.**
   - Extract purpose, users, inputs/outputs, platform, expected behavior,
     constraints, and success criteria from the prompt.
   - Ask focused questions only for decisions that materially affect the design
     or safety. Record unresolved assumptions explicitly rather than inventing
     answers.
   - Research external APIs, formats, platform behavior, or security-sensitive
     requirements using current official documentation when applicable. Cite
     sources in `requirements.md`; do not present guesses as facts.
2. **Create the project folder.**
   - Derive a short lowercase kebab-case slug and use
     `projects/<script-name>/requirements.md`.
   - Inspect the target first. Never overwrite an existing folder or
     `requirements.md`; if it exists, ask whether to continue it or choose a
     different name.
   - Create only the folder and requirements document. Do not add code,
     generated files, or dependencies.
3. **Write a complete initial specification.**
   - Use [the requirements template](./references/requirements-template.md).
   - Describe intended behavior and architecture at the level needed to
     implement and test the script. Keep requirements specific and testable.
   - Include implementation phases, acceptance criteria, validation commands
     when known, operational constraints, failure behavior, and relevant
     documentation links.
   - Populate the **Critical Issues** table with material blockers, risks, and
     unresolved design decisions. For each, include impact, evidence or
     uncertainty, a reliable proposed mitigation, and review status.
   - Populate the **Recommendations** table with worthwhile non-blocking
     improvements, rationale, cost/trade-off, proposed disposition, and status.
     Do not label optional polish as critical.
   - Use a checkbox scaffold table in `requirements.md`, with separate rows for
     source entry points, modules, tests, fixtures, configuration, and packaging
     deliverables. Link each row to requirement/test IDs and an implementation
     phase. Use `[x]` only for present and verified behavior; use `[ ]` for
     planned, missing, incomplete, or unverified work.
   - A proposed resolution is not an accepted resolution. Keep unresolved items
     visible until the user and `/review-req` have accepted their resolution.
4. **Iterate on the specification.**
   - Recommend `/review-req` for a requirements review. Address each finding in
     `requirements.md`, preserving an audit trail and marking review status.
   - For critical issues, propose a defensible mitigation grounded in project
     constraints and authoritative sources where relevant. Do not mark the
     blocker resolved merely because a mitigation was suggested.
   - Repeat review and document updates until all critical issues are resolved
     and requirements review passes. Recommendations may remain open or be
     accepted/deferred by the user; explain trade-offs.
   - Once the requirements pass and all critical issues have accepted
     resolutions, present the implementation plan and remaining optional
     recommendations. Do not begin implementation automatically. Wait for an
     explicit user request to run `/build-script` on this requirements file
     (for example, “build based on this requirements.md”).
5. **Report the handoff.**
   - Link the requirements file and summarize unresolved critical issues,
     recommendations, assumptions, and the next review/build gate.
   - Render unresolved critical issues and recommendations with their proposed
     mitigations/dispositions in the chat response; do not tell the user to read
     the requirements file as the in-session source for those decisions.
   - State plainly that no script code or executable was created.

## Hard Boundary

Only an explicit request to build/implement from the named, reviewed
`requirements.md` authorizes application code changes through `/build-script`.
A request to create a script plan, fix/review requirements, or make
recommendations does not authorize implementation or packaging. `/build-exe`
is only for packaging after implementation and code review pass.
