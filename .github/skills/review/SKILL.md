---
name: review
description: "Review repository implementations and AI customizations for correctness against the user's actual requirements. Use for code reviews, audits, or checking skills, agents, tools, MCP servers, hooks, prompts, instructions, and other repo automation; verify claims with tests and official references when needed."
argument-hint: "Optionally identify the files, implementation, or repository capability to review"
---

# Evidence-Based Repository Review

Review the requested implementation or repository capability against its
stated purpose. Look for meaningful gaps between what the user expects and what
the repository actually does, including whether customizations are discoverable,
valid, correctly integrated, and verified.

For script projects managed by `/new-script` or `/change-script`, use the
project's `requirements.md` as the acceptance baseline. Requirements review
findings must be incorporated into that file as proposed resolutions or new
issues, then re-reviewed. When reviewing implemented code, record confirmed
findings in `requirements.md`, link them to requirements or Change Request
items, and mark the implementation as requiring a rebuild. Update the
document-control and review-gate status fields on every review outcome using
the transitions below. Do not silently patch application code during a
review-only request. Code changes happen only when the user explicitly invokes
`/build-script` or otherwise requests implementation from the approved
requirements; after rebuilding, review the code again. A clean code review
authorizes packaging with `/build-exe`.

## Review Procedure

1. **Establish the expectation and scope.**
   - Use the user's exact request and explicit constraints as the primary
     acceptance criteria. Inspect relevant project docs, prior decisions, and
     conventions when they clarify intent.
   - If the target is inside a `projects/<name>/` workflow folder, read its
     `requirements.md` and current workflow status before reviewing. Do not
     infer that implementation or packaging is authorized merely because a
     requirements file exists.
   - Identify the requested files, changed behavior, and integration surfaces.
     For a general review with no target specified, review the current changes
     first; include related files needed to understand their behavior.
   - Ask a focused question only if materially different interpretations would
     change what is reviewed. Do not silently substitute a narrower or broader
     task.
2. **Gather repository evidence.**
   - Read the implementation and enough surrounding code, callers, tests,
     configuration, and documentation to trace the behavior under review.
   - Inspect the worktree and relevant diff so pre-existing edits are not
     mistaken for review changes.
   - For code, verify important claims with targeted tests, type checks, builds,
     or execution where available. For configuration and agent instruments,
     validate the actual format, location, referenced files, and discovery or
     integration behavior where the environment permits.
3. **Review the instrument as well as its text.**
   - For skills, agents, prompts, and instructions, check naming and schema,
     activation/discovery description, correct workspace or user location,
     references and assets, and whether the procedure actually fulfils its
     stated purpose.
   - For tools and MCP servers, check the declared interface against its
     implementation or authoritative tool schema, configuration, permissions,
     required runtime, and how the consuming agent discovers and invokes it.
     Do not execute untrusted servers, hooks, or scripts just to inspect them.
   - For hooks and automation, check event names, payloads, commands, working
     directories, dependencies, permissions, failure behavior, and whether the
     intended runtime actually supports them.
   - For any other repo capability, trace the full path from configuration or
     entry point through execution to the outcome the user asked for.
4. **Verify external requirements when needed.**
   - Use current, primary sources for claims that cannot be established from
     the repository alone: the official product documentation, schema or API
     reference for the exact tool and harness, or the maintained protocol
     specification. Match the documentation to the project's versions and
     runtime; do not assume similarly named features share a format.
   - Prefer official documentation over blogs, generated examples, and memory.
     Search or browse for the specific requirement, then check the relevant
     passage rather than relying on a page title or search snippet.
   - Cite the source URL and relevant section for findings that rely on external
     rules. If authoritative documentation is unavailable or ambiguous, say so
     and lower confidence; never invent citations, schema rules, test results,
     or runtime behavior.
5. **Validate findings.**
   - Report only actionable defects or material gaps relative to the stated
     requirements. Trace each finding to direct evidence and explain its real
     impact. Check plausible alternative explanations and existing safeguards
     before calling something a bug.
   - Use exact file locations and line numbers when available. Clearly separate
     confirmed findings from unverified risks, assumptions, and follow-up
     suggestions. Give confidence based on evidence, not tone.
   - Do not claim a build, test, executable, customization, or integration works
     unless you actually verified it. State the exact checks performed and
     relevant limitations.
   - For managed script projects, keep findings traceable in `requirements.md`:
     record the finding, evidence, impact, proposed requirement/spec correction,
     and status in the Review Findings and Resolution Log, and update linked
     Critical Issues, Recommendations, or Change Requests as appropriate.
     Preserve original user intent; do not mark a critical issue resolved
     until its proposed resolution is reviewed and accepted.
   - Apply evidence-backed, unambiguous corrections directly to the
     requirements document. If a correction changes user-visible behavior or
     needs a user decision, record the proposed options and leave it blocked
     for the user. Never weaken a requirement merely to make defective code
     appear compliant.
   - If code review discovers a defect, update the requirements/change record
     and set implementation status to `Rebuild required`. Do not directly alter
     generated code unless the user explicitly asks for code fixes. A
     requirements review must then pass before rebuilding from the updated
     requirements.
6. **Update workflow status for managed script projects.**
   - At the start of a requirements review, set `Requirements review` to `In
     progress`. At completion, set it to `Passed` only when no unresolved
     critical issue or blocking decision remains and every actionable finding
     has an accepted requirements resolution. Otherwise set it to `Failed`.
     A failed review remains failed until the corrected requirements are
     reviewed again; set overall `Status` to `Draft` while it is failed.
   - At the start of a code review, set `Code review` to `In progress`. Set it
     to `Passed` only when no actionable implementation finding remains and
     the required acceptance checks have passed or any limits are explicitly
     accepted in the requirements. Otherwise set it to `Failed`.
   - A code finding sets `Implementation` to `Rebuild required`, `Code review`
     to `Failed`, `Packaging` to `Not authorized`, and the overall `Status` to
     `Rebuild required`, and `Requirements review` to `Not reviewed`; rebuilding
     must wait for that requirements review to pass and for an explicit
     `/build-script` request.
   - If a requirements correction changes behavior already implemented, set
     `Implementation` to `Rebuild required`, `Code review` to `Not reviewed`,
     `Packaging` to `Not authorized`, and overall `Status` to `Draft` until the
     user authorizes an implementation/rebuild after requirements review.
     Preserve `Implementation: Existing; review required` for adopted code
     when a requirements edit does not itself change its required behavior;
     preserve `Not started` for projects without code.
   - When requirements review passes, set overall `Status` to `Requirements
     approved`; do not authorize implementation. Preserve any
     `Rebuild required` state. Only `/build-script` after an explicit user
     request may set `Implementation` to `Authorized` and then `In progress`.
   - When code review passes, set `Implementation` to `Current`, overall
     `Status` to `Ready to package`, and `Packaging` to `Authorized`. This is
     the gate for the user's later `/build-exe` request, not permission to
     package automatically.
   - If the document uses an older template without these fields or values,
     add/update its Document Control and Review and Build Gate sections so the
     state is explicit. Never preserve a stale `Passed` or `Authorized` value
     after a relevant requirement or code change.
7. **Return a concise review.**
   - List findings first, ordered by severity and then confidence. For each,
     include location, issue, impact, evidence, and a concrete correction or
     verification step.
   - If no actionable findings are supported, say so and summarize what was
     checked and what could not be verified. Do not manufacture findings to
     make the review appear comprehensive.
   - Do not make changes during a review-only request. If the user asks for
     fixes, implement only the agreed findings, then run relevant validation
     and report what changed.
   - The managed-script requirements/change-record updates above are part of
     the user's requested review workflow. For unrelated review-only requests,
     do not edit files unless asked.

## Official References for VS Code and Copilot Customizations

Use the sources relevant to the artifact, and verify their current contents
before relying on them:

- [VS Code Agent Skills](https://code.visualstudio.com/docs/agent-customization/agent-skills)
- [VS Code Custom Agents](https://code.visualstudio.com/docs/agent-customization/custom-agents)
- [VS Code MCP Servers](https://code.visualstudio.com/docs/agent-customization/mcp-servers)
- [VS Code Agent Hooks](https://code.visualstudio.com/docs/agent-customization/hooks)
- [VS Code Custom Instructions](https://code.visualstudio.com/docs/agent-customization/custom-instructions)
- [Agent Skills specification](https://agentskills.io/specification)
- [Model Context Protocol specification](https://modelcontextprotocol.io/specification/latest)

These are starting points, not proof that a particular repository file is
valid. Check the exact file, version, harness, and runtime behavior under review.
