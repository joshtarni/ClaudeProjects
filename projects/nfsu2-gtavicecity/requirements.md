# Offline Combined Driving Game Requirements

## Document Control

- **Status:** Draft
- **Requirements review:** Passed
- **Implementation:** Rebuild required
- **Code review:** Not reviewed
- **Packaging:** Not authorized
- **Last updated:** 2026-11-22

## 1. Purpose

Specify one private, offline, single-player game combining the requested
high-level gameplay systems into one shared open-world experience. The player
can explore and drive through a city, enter street races and story missions,
build and customize a vehicle collection, and encounter police pursuits.

The deliverable is a playable game, not a launcher for two separate games. The
existing launcher does not satisfy this purpose.

## 2. Scope

### Goals

- Build one Windows game with a shared city and a connected gameplay loop:
  free driving, street races/events, story missions, police pursuits, vehicle
  progression, garages, and customization.
- Keep the game single-player and fully playable offline, without accounts,
  multiplayer, telemetry, cloud saves, or remote content fetching.
- Keep the initial playable scope achievable: one small original city area,
  one drivable vehicle, one race event, one story mission, one police pursuit,
  and one garage/economy/upgrade loop.
- Use original implementation and original or properly licensed content.

### Non-goals

- Copying either game's source code, maps, characters, story, music, art,
  models, or other proprietary assets; extracting or downloading content from
  either game or linked website.
- Reproducing either title as a whole or using either title as a game runtime.
- Multiplayer, online races, social features, cloud saves, or other network
  features.
- Public release, distribution, or packaging for others; the intended use is
  private play by the requesting user.

## 3. User Workflow

1. The user starts the game locally on Windows.
2. The player drives freely in the shared city and discovers or enters race
   events and story missions.
3. Races and missions award in-game currency/progression; the player uses
   garages to acquire, collect, and customize vehicles.
4. Police pursuits can occur during free driving or relevant activities and
   resolve through playable evade/capture outcomes.
5. The game saves progress locally and remains playable with networking
   disabled.

## 4. Requirements

| ID | Requirement | Priority | Acceptance test | Status |
|---|---|---|---|---|
| REQ-001 | Former requirement for two separate launcher entries. Superseded by CR-001; retained for history. | — | Not applicable to the combined-game scope. | Superseded by CR-001 |
| REQ-002 | Former requirement to launch authorized local copies of the two separate games. Superseded by CR-001. | — | Not applicable to the combined-game scope. | Superseded by CR-001 |
| REQ-003 | Former launcher-specific network and service restriction. Its offline/single-player intent is retained in REQ-020. | — | Covered by TEST-006. | Superseded by CR-001 |
| REQ-004 | Former launcher executable-path validation requirement. | — | Not applicable to the game. | Superseded by CR-001 |
| REQ-005 | Former requirement not to modify the two separate games' files. | — | Not applicable to the game. | Superseded by CR-001 |
| REQ-006 | Former launcher packaging/content restriction. Original-content safeguards are restated in REQ-018. | — | Covered by TEST-007. | Superseded by CR-001 |
| REQ-007 | Former unavailable-edition UI requirement. | — | Not applicable to the game. | Superseded by CR-001 |
| REQ-008 | Preserve Windows as the target platform. | Must | Build and launch the playable game on the selected supported Windows version. | Superseded by REQ-019 |
| REQ-009 | Former per-title offline-integration gate. | — | Not applicable to the new game. | Superseded by CR-001 |
| REQ-010 | Former separate-launcher/configuration requirement. | — | Not applicable to the game. | Superseded by CR-001 |
| REQ-011 | Record exact target environment versions before implementation acceptance. | Should | The selected engine and supported Windows/runtime versions are documented before implementation. | Retained; update for game engine |
| REQ-012 | Deliver one playable game that integrates both requested games' high-level gameplay systems; do not deliver separate launch choices or a launcher as the game. | Must | Starting the application enters the combined game's own playable experience without starting either source game or a separate game process. | Proposed |
| REQ-013 | Provide one shared, traversable city for free driving, discoverable race events, story missions, and police pursuits. | Must | In-game acceptance demonstrates continuous free driving and entry into at least one race and one mission in the same world/session. | Proposed |
| REQ-014 | Integrate street racing/events with a playable progression loop that awards in-game currency or progression. | Must | Completing the race changes the player's recorded result and grants the configured reward. | Proposed |
| REQ-015 | Provide story mission progression and a police pursuit with at least an evade outcome and a failure/capture outcome. | Must | Acceptance playthrough starts and completes the mission, triggers a pursuit, and verifies both pursuit outcomes. | Proposed |
| REQ-016 | Provide a local vehicle ownership and garage loop with at least one earnable upgrade or customization change. | Must | An earned reward can be spent in a garage; the vehicle change and resulting gameplay state persist after save/load. | Proposed |
| REQ-017 | Save and load single-player progress locally without cloud or account services. | Must | Save/reload preserves mission/event progress, currency, and owned vehicle configuration with networking disabled. | Proposed |
| REQ-018 | Create original game-specific implementation and use original or properly licensed content. Reuse third-party source code only after the exact revision, license, and obligations are reviewed and recorded. Do not copy or extract proprietary code, assets, maps, characters, music, story, or saves from either source game. | Must | Source/content audit finds no copied or extracted source-game material; each reused component has a compatible documented license and required notices. | Proposed |
| REQ-019 | Unreal Engine 5.5.4 is the selected engine. Implement in C++ and support Windows 11 64-bit as the minimum and tested baseline. Before implementation, document the exact Visual Studio/SDK/build-tool requirements and all runtime redistributables. | Must | The game launches and passes the acceptance checks with Unreal Engine 5.5.4 and C++ on Windows 11 64-bit, using only the documented build tools and runtime dependencies. | Proposed |
| REQ-020 | Keep the game single-player and usable offline after installation; no accounts, multiplayer, telemetry, cloud saves, online fallback, or runtime remote-content requirements. | Must | With networking disabled, the complete acceptance loop runs and network monitoring shows no outbound attempt by the game. | Proposed |
| REQ-021 | Bound the first playable release to one small original city area, one drivable vehicle, one race event, one story mission, one police pursuit, and one garage/economy/upgrade loop. | Must | Each listed feature is present and playable in the same offline session. | Proposed |
| REQ-022 | Define deterministic first-release progression values: race reward 500 currency, story-mission reward 300 currency, starting currency 0, and one earnable upgrade costing 400 currency and increasing configured baseline top speed by exactly 10%. | Must | Acceptance fixtures start at 0 currency, show the configured rewards once, and verify the 400-currency upgrade increases baseline top speed by exactly 10% and is unaffordable until 400 earned currency is available. | Proposed |
| REQ-023 | Define pursuit outcomes for the first release: police detect the player within a 25-metre radius; escape only after 30 consecutive seconds outside that radius, and capture when police remain within 1 metre of the player for 15 consecutive seconds. Escape clears heat and returns normal driving; capture places the player at the city garage entrance, clears heat, and deducts 100 currency with a minimum balance of 0. | Must | Automated or manual acceptance exercises both paths and verifies the heat state, city garage entrance respawn, and capture deduction exactly. | Proposed |
| REQ-024 | Define the local save schema and failure behavior for first-release progress. The save must preserve race completion, mission completion, currency, owned vehicles, and equipped upgrade state. Malformed or unreadable saves must be reported without silently overwriting recoverable data. | Must | Save/reload preserves every listed field once; malformed-save fixtures produce an actionable error and leave the recoverable file unchanged. | Proposed |

## 5. Inputs, Outputs, and Constraints

- **Inputs:** Local keyboard/controller input and local save data; no credentials
  or network input.
- **Outputs:** Playable local game state, locally persisted progress, and
  user-visible gameplay feedback. No network output.
- **Platform/runtime:** Unreal Engine 5.5.4 is the selected engine. Windows 11
  64-bit is the minimum and tested baseline. The implementation language,
  exact Visual Studio/SDK/build-tool requirements, and runtime redistributables
  remain to be documented before implementation.
- **Content constraints:** Use original content or content with documented
  licenses. The requested private use does not authorize copying or extracting
  source-game code or assets.
- **Offline definition:** After installation, the game must reach and complete
  the entire first playable loop with the device disconnected from the
  internet. Setup must not require an account or runtime download.

## 6. Design and Implementation Plan

### Proposed design

Build a new, original, single-player driving game. Its central loop is a shared
city for free driving, street races, story missions, police pursuits, and
vehicle ownership/customization. The first playable scope is deliberately
small; expansion beyond the vertical slice requires a later requirements
change.

Public repositories may inform requirements and technical research. Any
source-code reuse requires a separate review of the exact repository revision,
all applicable licenses, third-party components, and any conditions before
implementation. Repository visibility alone is not permission. Do not use
source-game assets, maps, music, story, or extracted data. Unreal Engine 5.5.4 and Windows 11 64-bit are selected, with C++ implementation.
Record the input approach, exact build tools, runtime dependencies, and tested
Windows environment before implementation.

### Proposed script scaffold

| Scaffold item | Function / deliverable | Requirement IDs | Phase | State |
|---|---|---|---|---|
| Game project root and engine configuration | One Unreal Engine 5.5.4 C++ Windows 11 game application and reproducible local project setup | REQ-012, REQ-019, REQ-020 | 1 | [ ] Runtime and build dependencies not yet documented |
| World and vehicle systems | Original small city, driveable vehicle, camera, and controls | REQ-013, REQ-021 | 1 | [ ] |
| Race, mission, pursuit, and progression systems | Integrated playable activities and reward loop | REQ-014, REQ-015, REQ-021 | 1–2 | [ ] |
| Garage and local save system | Vehicle ownership, customization, economy, and persistence | REQ-016, REQ-017, REQ-021 | 1–2 | [ ] |
| Original game assets | Original or properly licensed placeholder art/audio; no extracted game data | REQ-018 | 1–2 | [ ] |
| `tests/` or engine-native test scenes | Gameplay, persistence, offline, and Windows acceptance coverage | TEST-001–TEST-008 | 1–2 | [ ] Rebuild required |
| `THIRD_PARTY_NOTICES.md` or equivalent | Record engine/plugin/content licenses and any permitted source reuse | REQ-018, TEST-007 | Before implementation / 2 | [ ] |

### Planned files/modules

| Path | Responsibility |
|---|---|
| Game project root | Engine project, startup scene, and Windows game configuration |
| World/vehicle modules or scenes | Shared city traversal, driving, camera, and controls |
| Activity/progression modules or scenes | Races, missions, pursuits, rewards, and progression |
| Garage/save modules or scenes | Vehicle collection, upgrades, customization, and local saves |
| `tests/` or engine-native tests | Automated and manual gameplay/offline acceptance |
| Existing `app.py`, `launcher.py`, `config.py` | Prior launcher only; not the combined game and not an implementation of CR-001 |

### Implementation phases

| Phase | Work | Exit criteria | Status |
|---|---|---|---|
| 0 | Complete the requirements re-review, document the UE 5.5.4 build environment, and audit proposed code/content sources. | Requirements review passes; engine, build tools, runtime dependencies, and source/license decisions are documented. | Passed |
| 1 | Create the playable vertical slice in a small original city. | Player can drive, complete a race and story mission, experience a police pursuit, use a garage/upgrade loop, and save/load locally. | Not started |
| 2 | Validate full offline loop, Windows behavior, persistence, and content/source compliance. | TEST-001–TEST-008 pass on the documented environment. | Not started |
| 3 | Optional private local packaging only after the user explicitly requests it and gates pass. | Package contains the game only, has compliant notices, and works offline. | Not authorized |

## 7. Error Handling, Safety, and Security

| Scenario | Expected handling | User-visible outcome | Verification |
|---|---|---|---|
| Game starts without required local resources or save directory | Fail clearly; do not silently claim gameplay or replace the state with success-shaped defaults | Explain the missing/corrupt resource and how to retry or reset the local save | TEST-001, TEST-005 |
| Player completes or fails an activity | Resolve the result once and persist the corresponding progress/reward | Clear completion/failure feedback; no duplicated or lost reward after reload | TEST-003, TEST-005 |
| Game encounters network loss or has networking disabled | Do not require a connection or attempt online fallback | The game remains playable offline | TEST-006 |
| External code, plugin, or content is proposed | Verify provenance, exact license, and all obligations before use | Unverified material is excluded until reviewed | TEST-007 |
| Game exits or save data is malformed | Report the failure; preserve recoverable data and avoid silently overwriting it | Actionable local-save error or safe recovery path | TEST-005 |

## 8. Testing and Acceptance

| Test ID | Scenario | Expected result | Method |
|---|---|---|---|
| TEST-001 | Start the game from a clean local install | The application enters the game's own menu/world and does not launch either source game or a second game process | Windows smoke test |
| TEST-002 | Drive around the original city and enter the race and story activity in the same session | Vehicle controls respond; the player remains in the shared world and activities can be started and completed | Gameplay acceptance |
| TEST-003 | Complete the race and story mission | The race grants exactly 500 currency once and the mission grants exactly 300 currency once; results remain visible and are unchanged after reload | Gameplay/integration |
| TEST-004 | Trigger and resolve a police pursuit by escape and capture | Detection begins within 25 metres; escape occurs after 30 consecutive seconds outside that radius and clears heat; capture occurs after police remain within 1 metre for 15 consecutive seconds, respawns the player at the city garage entrance, clears heat, and deducts 100 currency without reducing below 0 | Gameplay/integration |
| TEST-005 | Earn currency, purchase the 400-currency 10% top-speed upgrade, then save/reload | The upgrade increases the vehicle's configured baseline top-speed value by exactly 10%, reduces currency by exactly 400, cannot be purchased before 400 currency, and vehicle/progress/currency persist; malformed-save fixtures produce an error without overwriting the recoverable file | Integration |
| TEST-006 | Disable networking and play through the complete vertical slice while monitoring game network activity | The full loop remains playable and the game makes no outbound network attempt | Manual Windows offline acceptance |
| TEST-007 | Audit source, dependencies, assets, and notices for all included material | Reused material has a verified compatible license and required notices; no source-game content was copied or extracted | Provenance/license review |
| TEST-008 | Launch and play the vertical slice on the documented Windows and engine versions | No blocking startup, input, save, or gameplay failures occur | Windows acceptance |

Validation commands and engine-specific test steps will be recorded after the
engine is selected. The earlier `python -m pytest -q` result covers only the
superseded launcher and is not evidence that these game tests pass.

### Implementation validation

- **Historical launcher implementation:** `app.py`, `launcher.py`, `config.py`,
  and `tests/test_*.py`.
- **Historical result:** 13 launcher tests passed on 2026-11-22. Those tests
  validate launcher behavior only; they do not satisfy TEST-001–TEST-008 for
  the combined game.
- **Current combined-game validation:** Not implemented or tested.

## 9. Critical Issues

| ID | Issue / unknown | Impact | Evidence / confidence | Proposed mitigation | Status | Review evidence |
|---|---|---|---|---|---|---|
| CRIT-001 | Rights to use or redistribute the two original games' engines, code, data, and assets remain unknown. | Copying source-game material could violate rights even for a private project. | The prior linked-game pages do not establish rights for this new game. | Do not copy or extract source-game code or content. Consult repositories only as allowed by their exact licenses; audit any reused code and third-party material before implementation. | Resolved; fail-closed by REQ-018 | CR-001; TEST-007 |
| CRIT-002 | Offline behavior of the original linked editions is unverified. | Irrelevant to the new game unless either original edition is later proposed as a dependency. | The new scope is a standalone original game, not integration of either web edition. | Keep both original games out of the runtime and verify the new game itself with TEST-006. | Superseded for current scope by CR-001 | CR-001; REQ-012, REQ-020 |
| CRIT-003 | “Those two games as one” was previously interpreted as a launcher, contrary to the user's intent. | The launcher cannot provide the requested combined gameplay. | The user clarified that they want the mechanics combined in one offline game for private play. | Replace launcher requirements with the shared-world playable-game requirements in CR-001; do not treat launcher completion as satisfying this project. | Resolved by user clarification 2026-11-22 | CR-001; REQ-012–REQ-021 |
| CRIT-004 | The requested open-world driving game is too broad for an unbounded first build. | Attempting a full commercial-scale city/game could stall before anything is playable. | The requested systems span driving, racing, missions, pursuits, economy, collection, and customization. | Deliver the bounded vertical slice in REQ-021 first; defer expansion until that slice passes acceptance. | Resolved; bounded by REQ-021 | CR-001; REQ-021; TEST-001–TEST-008 |
| CRIT-005 | The implementation language and exact build/runtime environment were initially undecided. | The implementation language affects tooling and repository structure; exact build dependencies remain implementation documentation work. | C++ was explicitly selected for Unreal Engine 5.5.4; REQ-019 now records the decision and retains exact toolchain documentation as a Phase 0 implementation prerequisite. | Document exact Visual Studio/SDK/build-tool and runtime requirements before implementation. | Resolved; implementation prerequisite | REQ-019; REC-004 |
| CRIT-006 | Pursuit detection ranges, police contact, safe-road position, and upgrade vehicle effect were previously undefined. | Undefined predicates prevented TEST-004 and TEST-005 from being unambiguously passable or failable. | REQ-023 and TEST-004–TEST-005 now define 25-metre detection, 1-metre capture contact, city garage entrance respawn, and a 10% top-speed upgrade. | No further correction required for first-release acceptance. | Resolved | REQ-022–REQ-024; TEST-004–TEST-005 |

## 10. Recommendations

| ID | Recommendation | Benefit | Cost / trade-off | Proposed disposition | Status | Review evidence |
|---|---|---|---|---|---|---|
| REC-001 | Keep the launcher separate from both game installations and store only user-selected local paths in its configuration. | Reduces accidental game-file changes. | Does not provide the requested combined game. | Superseded by CR-001; launcher behavior is not the target deliverable. | Superseded | CR-001 |
| REC-002 | Show offline readiness independently for each original title. | Makes unsupported integrations transparent. | Not relevant to a standalone game. | Superseded by CR-001. | Superseded | CR-001 |
| REC-003 | Use a small playable vertical slice before adding more world/content. | Makes the project achievable and validates the whole gameplay loop early. | Less content in the first playable build. | Adopted in REQ-021. | Accepted | CR-001 |
| REC-004 | Pin the implementation language, 3D input approach, build toolchain, runtime dependencies, and tested Windows environment. | Avoids repeatability gaps after engine selection and enables reproducible testing. | Adds setup/configuration documentation and tooling constraints. | Adopted only as a requirements fix; exact Visual Studio/SDK/runtime details remain pending before implementation. | Accepted; proposed requirements-only documentation |
| REC-005 | Use public repositories as research references, and reuse code only after checking the exact license and provenance. | Provides practical insight into driving, event, customization, and engine implementation while managing rights risk. | Requires source-by-source license and dependency review; some repos may be unsuitable. | Adopted in REQ-018 and TEST-007. | Accepted | CR-001; repository license review |

## 11. Change Requests

| ID | User intent and change | Affected requirements/files | Acceptance criteria | Dependencies and risks | Tests / phase impact | Status |
|---|---|---|---|---|---|---|
| CR-001 | Replace the two-title launcher concept with one private, offline, single-player game combining open-world driving, street races/events, car upgrades/tuning/customization, story missions/progression, police pursuits, economy/garages, and vehicle collection in one shared world. The user also asked that public repositories for both games be used as help. | Supersedes launcher REQ-001–REQ-010; retains Windows target and updates REQ-011; adds REQ-012–REQ-024. Affects `requirements.md` and the future game project; existing `app.py`, `launcher.py`, and `config.py` do not implement this scope. | One game starts locally; all listed systems work in one shared-world vertical slice; the loop is playable with networking disabled; local progress persists; no copied/extracted source-game assets or unreviewed code are included. | Unreal Engine 5.5.4, C++, and Windows 11 64-bit are resolved. Pursuit, economy, upgrade, save, and provenance predicates are defined. Exact build tools remain a Phase 0 implementation prerequisite. | Add TEST-001–TEST-008 plus REQ-022–REQ-024 fixtures. Requirements review passed; implementation remains Rebuild required; code review resets; packaging is not authorized. | Passed; implementation not authorized |

## 12. Review Findings and Resolution Log

| ID | Review stage | Finding and evidence | Linked requirement / CR | Proposed requirements fix | Status |
|---|---|---|---|---|---|
| RF-001 | Requirements review 2026-11-22 | CRIT-001 rights evidence was absent for the former launcher integration. | Historical CRIT-001; former REQ-006/REQ-009 | Former fail-closed launcher requirements are retained as history; current content/source constraints are REQ-018 and TEST-007. | Historical; superseded by CR-001 |
| RF-002 | Requirements review 2026-11-22 | Offline support for the exact browser editions was unverified. | Historical CRIT-002; former TEST-003 | The original editions are not dependencies in the new scope; verify the new game offline with TEST-006. | Historical; superseded by CR-001 |
| RF-003 | Requirements review 2026-11-22 | “As one” was interpreted as separate launcher entries. | Historical CRIT-003; CR-001 | User clarification now defines a single shared-world game. | Superseded by CR-001 |
| RF-004 | Requirements review 2026-11-22 | Exact environment versions were not selected. | REQ-011; now REQ-019 | Record game engine/version and tested Windows environment before implementation. | Carried forward |
| RF-005 | Code review 2026-11-22 | Former launcher path handling had a missing-target state issue; corrected for launcher behavior. | Historical former TEST-001; former REQ-004/REQ-007 | Kept as launcher review history; unrelated to gameplay acceptance. | Historical; superseded by CR-001 |
| RF-006 | Change request 2026-11-22 | Existing implementation is a launcher, so prior implementation, review, and packaging approvals do not establish that the requested game exists. | CR-001; REQ-012–REQ-021; TEST-001–TEST-008 | Reset active gates; replace the launcher specification with the bounded shared-world game scope. | Open; requirements review required |
| RF-007 | Repository research 2026-11-22 | Public repositories have different scopes and license terms. OpenUG2 describes an MIT-licensed engine reimplementation that requires the user's own game data; reVC has an additional automated-system usage-record condition. | CR-001; REQ-018; TEST-007 | Treat repositories as references only until each exact code/dependency/license path is reviewed. Exclude reVC from code or derived-material use because its required upstream record cannot be made here. | Open; source audit required before any reuse |
| RF-008 | Requirements review 2026-11-22 | Engine and exact tested Windows/runtime baseline were unresolved in the initial review. | REQ-019; CRIT-005; DEC-008 | Unreal Engine 5.5.4, C++, and Windows 11 64-bit are selected; exact build tools remain a Phase 0 implementation prerequisite. | Resolved |
| RF-009 | Requirements review 2026-11-22 | Acceptance criteria were not deterministic for reward, pursuit, economy, and save/recovery behavior. | REQ-014–REQ-017; TEST-003–TEST-005; CRIT-006 | Exact values and observable predicates were added in REQ-022–REQ-024 and TEST-003–TEST-005. | Resolved |
| RF-010 | Requirements correction 2026-11-22 | Selected Unreal Engine 5.5.4 and Windows 11 64-bit; added deterministic progression, pursuit, garage, save, and malformed-save acceptance fixtures. | REQ-019, REQ-022–REQ-024, TEST-003–TEST-005, CRIT-005–CRIT-006 | C++ and explicit pursuit/upgrade predicates remained to be selected; those blockers were subsequently corrected. | Resolved |
| RF-011 | Requirements re-review 2026-11-22 | REQ-019 and the implementation language remained to be completed. | REQ-019; CRIT-005; DEC-008 | User selected C++; requirements now require C++ and defer only exact build-tool documentation to the implementation prerequisite. | Resolved |
| RF-012 | Requirements re-review 2026-11-22 | REQ-023 and TEST-004–TEST-005 did not define exact detection/contact/respawn/upgrade predicates. | REQ-023, TEST-004, TEST-005, CRIT-006 | User selected 25-metre detection, 1-metre capture contact, city garage entrance respawn, and 10% top-speed upgrade; requirements and tests now match. | Resolved |

## 13. Review and Build Gate

- **Requirements review:** Passed. No unresolved critical findings remain.
- **Critical issue gate:** Closed for requirements review; exact build-tool documentation remains a Phase 0 implementation prerequisite.
- **Implementation:** Rebuild required. Existing source and any existing launcher package implement only the superseded launcher scope; no combined game has been built.
- **Code review:** Not reviewed for the combined-game requirements.
- **Packaging:** Not authorized. No new game package was created for CR-001; the user's stated intent is private local play, not release or distribution.
- **Historical evidence:** The prior launcher had 13 passing tests and a launcher-only packaged executable. This evidence does not satisfy the game requirements.

## 14. Assumptions and Decisions

| ID | Assumption or decision | Owner | Status | Evidence / date |
|---|---|---|---|---|
| DEC-001 | “As one” means one desktop launcher with two separate game entries, not a fused game. | Prior project scope | Superseded by CR-001 | User clarified the requested single shared-world game, 2026-11-22 |
| DEC-002 | Windows is the target platform. | User/project | Retained | Prior user selection; confirmed in CR-001 requirements |
| DEC-003 | Multiplayer and online features are out of scope; full offline functionality is desired. | User/project | Retained | User reiterated offline single-player intent, 2026-11-22 |
| DEC-004 | Source-game rights are unknown; no source-game assets/code are presumed authorized. | User/project | Retained safeguard | REQ-018; public/private intent does not change content provenance requirements |
| DEC-005 | The requested game combines all selected gameplay systems in one shared open world. | User | Accepted | User selected free driving, races, customization, story/progression, police, economy/garages/collection, and shared-world integration, 2026-11-22 |
| DEC-006 | The game is for the user's private offline play and is not intended for public release. | User | Accepted | User clarification, 2026-11-22 |
| DEC-007 | Public repositories may be used as help. | User | Accepted with license/provenance gate | CR-001; REQ-018; TEST-007 |
| DEC-008 | Unreal Engine 5.5.4 is the selected engine; C++ is the implementation language; Windows 11 64-bit is the minimum and tested baseline. | User/project | Accepted | Selected 2026-11-22 |

## 15. References

- [Underground 2 Revived](https://nfsu2.xyz/) — project page, accessed
  2026-11-22. Describes browser recompilation of the PC game's code, game data
  on the device, online play, and save synchronization. This page is evidence
  of the site's stated behavior, not proof of offline availability or
  redistribution rights.
- [Vice City Web Edition](https://quenq.com/apps/vice-city/) — project page,
  accessed 2026-11-22. Describes a browser port based on revcDOS/reVC and
  dynamic asset streaming. This page is evidence of the site's stated behavior,
  not proof of offline availability or redistribution rights.
- [OpenUG2](https://github.com/whoismept/OpenUG2) — public repository and
  README/license reviewed 2026-11-22. The README describes an open-source
  reimplementation of the NFSU2 engine, free roam, AI races, and customization;
  it requires the user's own game data. Its repository license is MIT. Candidate
  research reference only; no code or game data was copied.
- [nfsu2-web](https://github.com/th0mk/nfsu2-web) — public, archived repository;
  root license identifies MIT terms. Not adopted; project/dependency provenance
  requires separate review before any code reuse.
- [reVCDOS](https://github.com/Lolendor/reVCDOS) — public repository with an
  MIT license. Candidate research reference only; no code or game data was
  copied.
- [reVC](https://github.com/mrxenginner/reVC) — license file reviewed only.
  Its license includes an additional condition requiring automated systems to
  create an upstream provenance record and include a matching hash in credits.
  That upstream record was not created, so this repository is excluded from
  code and derived-material use in this task.
