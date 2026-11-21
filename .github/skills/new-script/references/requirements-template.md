# <Script Name> Requirements

## Document Control

- **Status:** Draft
- **Requirements review:** Not reviewed
- **Implementation:** Not started
- **Code review:** Not started
- **Packaging:** Not authorized
- **Last updated:** <YYYY-MM-DD>

Use these status values consistently:

- Overall status: `Draft`, `Requirements approved`, `Implementation in
  progress`, `Implementation complete; code review required`,
  `Rebuild required`, `Ready to package`, or `Packaged`.
- Requirements review: `Not reviewed`, `In progress`, `Passed`, or `Failed`.
- Implementation: `Not started`, `Authorized`, `In progress`,
  `Existing; review required`, `Rebuild required`, or `Current`.
- Code review: `Not reviewed`, `In progress`, `Passed`, or `Failed`.
- Packaging: `Not authorized`, `Authorized`, or `Complete`.

A requirements change or code finding invalidates downstream review/build
approvals as described below. A passing requirements review does not itself
authorize implementation; an explicit user request to run `/build-script` is
required. A passing code review authorizes packaging but does not run
`/build-exe` automatically.

For a pre-existing project adopted into this workflow, use
`Implementation: Existing; review required` until its requirements review and
code review pass. Do not claim existing code is current merely because it runs.

## 1. Purpose

<Problem this script solves and intended users.>

## 2. Scope

### Goals

- <Measurable outcome>

### Non-goals

- <Explicitly excluded behavior>

## 3. User Workflow

1. <User action>
2. <Expected script behavior>
3. <Observable result>

## 4. Requirements

| ID | Requirement | Priority | Acceptance test | Status |
|---|---|---|---|---|
| REQ-001 | <Specific, testable behavior> | Must | <Observable pass condition> | Proposed |

## 5. Inputs, Outputs, and Constraints

- **Inputs:** <Sources, formats, validation>
- **Outputs:** <Files, UI, side effects>
- **Platform/runtime:** <Known requirements>
- **Constraints:** <Performance, privacy, compatibility, limits>

## 6. Design and Implementation Plan

### Proposed design

<Components, responsibilities, data flow, and key decisions. Distinguish facts
from assumptions; link sources for external behavior.>

### Proposed script scaffold

<State whether this is a single-file script or a package. Include the entry
point and each planned source, configuration, test, fixture, and packaging
file or directory. Express the scaffold as a checkbox table: `[x]` means a
function or deliverable is already present and satisfies the review scope;
`[ ]` means it is planned but not yet implemented or not yet verified.>

| Scaffold item | Function / deliverable | Requirement IDs | Phase | State |
|---|---|---|---|---|
| `<entry-point>.py` | Application entry point, startup, and main workflow | `<REQ-...>` | 1 | [ ] |
| `<support-module>/` | `<Responsibility>` | `<REQ-...>` | 1 | [ ] |
| `tests/` | Unit, integration, and acceptance coverage | `<TEST-...>` | 1 | [ ] |
| `fixtures/` | Representative input and expected-output data | `<TEST-...>` | 1 | [ ] |
| `<build-config-or-lockfile>` | Reproducible build and dependency configuration | `<REQ-...>` | 2 | [ ] |

Use the existing implementation state to check items for adopted code:
`[x]` only when the item exists and has passed the relevant review evidence;
`[ ]` when it is missing, incomplete, not yet implemented, or not yet
verified. Add every required source module, test area, fixture, configuration
file, and packaging deliverable as a separate row. Group follow-on optional
features only if they are explicitly in scope or recorded as recommendations.

### Planned files/modules

| Path | Responsibility |
|---|---|
| <path> | <purpose> |

### Implementation phases

| Phase | Work | Exit criteria | Status |
|---|---|---|---|
| 1 | <Core behavior> | <Tests/criteria pass> | Not started |
| 2 | <Error handling and integration> | <Tests/criteria pass> | Not started |

## 7. Error Handling, Safety, and Security

| Scenario | Expected handling | User-visible outcome | Verification |
|---|---|---|---|
| <Failure or misuse> | <Safe behavior> | <Message/result> | <Test> |

## 8. Testing and Acceptance

| Test ID | Scenario | Expected result | Method |
|---|---|---|---|
| TEST-001 | <Normal case> | <Pass condition> | <Unit/integration/manual> |

## 9. Critical Issues

Critical issues are blockers or material risks that must be resolved before
implementation is authorized. A proposed fix is not considered resolved until
reviewed and accepted.

| ID | Issue / unknown | Impact | Evidence / confidence | Proposed mitigation | Status | Review evidence |
|---|---|---|---|---|---|---|
| <CRIT-NNN> | <Blocker or material risk> | <Impact> | <Source or uncertainty> | <Defensible mitigation or research needed> | Open | <Pending> |

If none are identified, write `None identified` below the table; do not create
an open placeholder issue.

## 10. Recommendations

Recommendations are non-blocking improvements. Record trade-offs and let the
user accept, defer, or reject them.

| ID | Recommendation | Benefit | Cost / trade-off | Proposed disposition | Status | Review evidence |
|---|---|---|---|---|---|---|
| <REC-NNN> | <Non-blocking improvement> | <Benefit> | <Cost> | <Accept/defer/reject recommendation> | Proposed | <Pending> |

If none are identified, write `None identified` below the table; do not create
a placeholder recommendation.

At the end of `/review-req`, repeat the Critical Issues and Recommendations
(Warnings) tables in the chat response with their full proposed mitigations and
dispositions. The requirements file is the audit record; chat presentation is
the user's in-session decision view.

## 11. Change Requests

Add one entry per user-requested change. Link each item to requirements,
acceptance tests, risks, and implementation phases it changes.

| ID | Request | Affected requirements/files | Acceptance criteria | Critical issues / recommendations | Status |
|---|---|---|---|---|---|
| <CR-NNN> | <User-requested change> | <Requirement IDs/paths> | <Testable criteria> | <Linked CRIT/REC IDs> | Proposed |

If there are no change requests, write `None yet` below the table.

## 12. Review Findings and Resolution Log

Record requirements-review findings and code-review findings here. For code
findings, describe the evidence and impact, update affected requirements or CRs,
and set implementation to `Rebuild required`. Do not record a finding as passed
until the relevant re-review confirms it.

| ID | Review stage | Finding and evidence | Linked requirement / CR | Proposed requirements fix | Status |
|---|---|---|---|---|---|
| <FIND-NNN> | <Requirements / code> | <Finding and evidence> | <REQ/CR IDs> | <Spec correction> | Open |

## 13. Review and Build Gate

- **Requirements review findings:** <None / list with IDs and status>
- **Critical issue gate:** Blocked until every critical issue is resolved and
  resolution has passed `/review-req`.
- **Implementation authorization:** Not authorized until the user explicitly
  requests `/build-script` implementation from this reviewed document.
- **Code review:** Must pass after implementation. Findings return to this
  document, invalidate the prior code-review pass, and require a requirements
  review only when they change requirements. Source-only findings keep a
  passing requirements review and require an explicitly requested rebuild.
- **Packaging:** Set to `Authorized` after code review passes. `/build-exe` may
  run only then and must set it to `Complete` only after a successful package.

## 14. Assumptions and Decisions

| ID | Assumption or decision | Owner | Status | Evidence / date |
|---|---|---|---|---|
| DEC-001 | <Open question or recorded decision> | <User/project> | Open | <Source/date> |

## 15. References

- <Official documentation title and URL, section, version/date, and what it
  supports>
