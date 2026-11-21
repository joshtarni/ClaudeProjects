# Screen Area Recorder Requirements

## Document Control

- **Status:** Draft
- **Requirements review:** Not reviewed
- **Implementation:** Existing; review required
- **Code review:** Not reviewed
- **Packaging:** Not authorized
- **Last updated:** 2026-11-21
- **Project origin:** Existing repository application adopted into the
  `projects/<script-name>/` workflow; this is a baseline capture, not a new
  implementation.

The source and executable already exist. Their presence does not mean they have
passed the new requirements or code review gates. Do not change application
behavior or package a new executable until review and authorization gates pass.

## 1. Purpose

Provide a Windows desktop app for recording a user-selected screen region with
system playback audio, controlling the recording with GUI actions and global
hotkeys, and optionally optimizing existing video files.

## 2. Scope

### Goals

- Record screen video and default Windows playback audio into an MP4.
- Allow the user to select a screen region, pause/resume, stop, and choose
  whether and where to save the resulting recording.
- Provide configurable global recording hotkeys.
- Offer video optimization profiles while preserving the original input file.
- Support running from Python and distributing a standalone Windows GUI
  executable.

### Non-goals

- Microphone capture.
- Cross-platform support; Windows is the target platform.

## 3. User Workflow

1. Launch the GUI and position or resize the outlined capture region.
2. Start recording with the GUI or configured global hotkey.
3. Pause/resume as needed; stop to finalize the recording.
4. Choose the output path/name, or cancel to discard the temporary recording.
5. Optionally select a video in the Optimize Video tab, choose a profile and
   maximum resolution, and save an optimized copy beside the original.

## 4. Requirements

| ID | Requirement | Priority | Acceptance test | Status |
|---|---|---|---|---|
| REQ-001 | Display a movable, resizable, transparent screen-region outline and capture only the selected region. | Must | Manually verify region movement/resizing and inspect a short capture. | Existing; requires review |
| REQ-002 | Capture video at the configured 20 FPS target using H.264 and combine it with default Windows playback audio encoded as AAC. | Must | Record on a real Windows playback device; verify video and audio streams and playback in the finalized MP4. | Existing; live-device test pending |
| REQ-003 | Pause and resume recording so paused intervals are omitted from the final recording. | Must | Pause during a timed capture, resume, and verify output duration/content excludes the pause. | Existing; requires review |
| REQ-004 | Let the user save the finalized recording to a chosen path, and delete temporary output when the user cancels. | Must | Exercise both save and cancel flows and verify resulting files. | Existing; prior verification documented |
| REQ-005 | Provide configurable global Start, Pause/Resume, and Stop hotkeys and persist settings for the Windows user. | Must | Change shortcuts, restart the app, and verify persisted settings and actions. | Existing; requires review |
| REQ-006 | Provide video optimization with selectable compression profile and maximum resolution, saving `<name>_optimized.mp4` without modifying the original and confirming overwrite. | Must | Optimize a sample video, compare original hash, and test existing-output confirmation. | Existing; requires review |
| REQ-007 | Show actionable errors for unavailable audio or recording/finalization failures; do not silently produce a success-shaped recording without required audio. | Must | Simulate unavailable audio and mux failures; verify visible error and cleanup. | Existing; requires review |
| REQ-008 | Run from Python using the declared project dependencies and produce a standalone one-file Windows GUI executable containing required runtime dependencies and FFmpeg. | Must | Install from project `requirements.txt`, launch source, inspect executable archive, then smoke-test the packaged GUI. | Existing; packaging review pending |

## 5. Inputs, Outputs, and Constraints

- **Inputs:** Screen capture region, Windows default playback output, user
  hotkey settings, and videos selected for optimization.
- **Outputs:** User-selected MP4 recording; optional optimized MP4 beside the
  input; temporary recording files that must be cleaned up on cancel/failure.
- **Platform/runtime:** Windows; Python source uses Tkinter, `mss`, NumPy,
  SoundCard, and `imageio-ffmpeg`.
- **Constraints:** The recorder captures default system playback, not a
  microphone. Actual loopback behavior depends on an available Windows audio
  output device.
- **Project paths:** `screen_recorder.py`, `requirements.txt`,
  `dist/ScreenRecorder.exe`, and `EXPERIENCE.md` in this directory.

## 6. Design and Implementation Plan

### Existing design

The implementation uses Tkinter/ttk for the GUI, `mss` for screen capture,
`imageio-ffmpeg` for FFmpeg, and SoundCard/NumPy to record system playback to a
temporary WAV before muxing it with video. Worker-thread updates are sent to the
Tkinter event loop through a queue. See the existing implementation and
`EXPERIENCE.md`; verify these details against the code during review.

### Planned project files

| Path | Responsibility |
|---|---|
| `screen_recorder.py` | GUI, screen capture, audio, hotkeys, and optimization behavior |
| `requirements.txt` | Python runtime dependencies |
| `dist/ScreenRecorder.exe` | Existing standalone Windows executable |
| `EXPERIENCE.md` | Historical implementation and verification notes |
| `requirements.md` | Approved behavior, review findings, workflow state |

### Workflow phases

| Phase | Work | Exit criteria | Status |
|---|---|---|---|
| Adoption | Move the existing source, executable, dependencies, and project log into this folder; document the baseline. | Paths and repository docs agree; Python syntax and executable archive/startup checks pass. | Complete |
| Requirements review | Compare this baseline with source, project docs, and user intent; resolve critical issues. | `/review-req` passes with critical issues resolved and status recorded. | Not started |
| Code review | Review the adopted implementation against approved requirements. | `/review-script` reports no actionable implementation findings; limitations are recorded. | Not started |
| Change implementation | Implement only user-authorized, reviewed Change Requests. | Acceptance tests pass and implementation state is current. | Not started |
| Packaging | Regenerate the standalone EXE after requirements and code reviews pass. | `/build-exe` succeeds, archive and startup are verified, and status is recorded. | Not authorized |

## 7. Error Handling, Safety, and Security

| Scenario | Expected handling | User-visible outcome | Verification |
|---|---|---|---|
| No default output or loopback device | Fail recording and report the cause; do not claim audio recording succeeded. | Actionable error dialog; temporary files cleaned up. | Test on a system without a usable output or inject a simulated failure. |
| FFmpeg process or audio/video mux fails | Report the failure and preserve/clean temporary files according to the user's save flow. | Error is visible and no invalid final output is reported as successful. | Simulate a non-zero FFmpeg exit and inspect cleanup. |
| User cancels save dialog | Delete the temporary recording. | No saved recording remains. | Exercise cancel flow and inspect files. |
| Optimized output already exists | Ask before replacing; preserve original input. | Clear overwrite prompt. | Test both confirmation choices and compare input hash. |

## 8. Testing and Acceptance

| Test ID | Scenario | Expected result | Method |
|---|---|---|---|
| TEST-001 | Source syntax after migration | Python source compiles. | `py -m py_compile projects\screen-recorder\screen_recorder.py` |
| TEST-002 | Dependency setup | Declared project requirements install in the supported Python environment. | `py -m pip install -r projects\screen-recorder\requirements.txt` |
| TEST-003 | Audio/video recording | Resulting MP4 contains playable video and system audio on a real target device. | Windows hardware smoke test; not yet verified |
| TEST-004 | Standalone executable | EXE includes application, Python runtime, required packages, and FFmpeg and starts on Windows. | PyInstaller archive inspection and GUI startup smoke test |
| TEST-005 | Save/cancel and optimizer flows | Expected outputs, cleanup, overwrite behavior, and original preservation hold. | Targeted functional tests/manual checks |

### Historical verification

`EXPERIENCE.md` records prior syntax, simulated audio/mux, and save/cancel
checks. Those records predate the project migration and are not a substitute
for rerunning checks against the moved paths or reviewing code against this
requirements baseline.

### Migration verification (2026-11-21)

- `py -m py_compile projects\screen-recorder\screen_recorder.py` passed.
- PyInstaller archive inspection confirmed the embedded `screen_recorder`
  module and FFmpeg binary are present in the moved executable.
- The moved EXE remained running for a 20-second startup smoke check. This
  verifies process startup only; GUI interaction, recording, and real-device
  audio capture were not verified.

## 9. Critical Issues

Critical issues block new implementation or packaging until resolved and
accepted through `/review-req`.

| ID | Issue / unknown | Impact | Evidence / confidence | Proposed mitigation | Status | Review evidence |
|---|---|---|---|---|---|---|
| CRIT-001 | Actual system loopback recording on a real target Windows playback device has not been verified. | The app's required audio capture may fail or select an unexpected device on the user's machine. | `EXPERIENCE.md` explicitly lists live capture as unverified. High confidence that verification is missing; runtime impact remains unverified. | Test start/pause/resume/stop on the intended Windows audio device; confirm the finalized MP4 has synchronized playable audio/video; record Windows/device setup and result. If it fails, trace the issue and propose a requirements-linked fix. | Open; blocks final approval | Pending |

## 10. Recommendations

| ID | Recommendation | Benefit | Cost / trade-off | Proposed disposition | Status | Review evidence |
|---|---|---|---|---|---|---|
| REC-001 | Add repeatable Windows integration coverage for recording, save/cancel, hotkeys, and optimization flows. | Reduces regression risk beyond syntax and simulated mux checks. | Requires Windows test environment and possibly audio-device simulation. | Recommend accept; phase coverage based on available hardware. | Proposed | Pending |

## 11. Change Requests

None yet.

## 12. Review Findings and Resolution Log

| ID | Review stage | Finding and evidence | Linked requirement / CR | Proposed requirements fix | Status |
|---|---|---|---|---|---|

## 13. Review and Build Gate

- **Requirements review findings:** Not reviewed.
- **Critical issue gate:** Blocked by open `CRIT-001`.
- **Implementation authorization:** Existing source is adopted but not yet
  reviewed against this baseline. No behavioral change or rebuild is
  authorized by this migration.
- **Code review:** Not reviewed; review after requirements review passes.
- **Packaging:** Not authorized until requirements and code reviews pass.

## 14. Assumptions and Decisions

| ID | Assumption or decision | Owner | Status | Evidence / date |
|---|---|---|---|---|
| DEC-001 | The existing recorder is adopted as project `screen-recorder`; its behavior is to be preserved unless an approved CR changes it. | User | Accepted | User request, 2026-11-21 |

## 15. References

- `README.md` in the repository root — user-visible feature and launch overview.
- `EXPERIENCE.md` — implementation history and previously recorded validation.
- `screen_recorder.py` and `requirements.txt` — current implementation and runtime dependencies; verify directly during review.
