# ClaudeProjects

This repository contains agent workflow skills and script projects.

## Screen Area Recorder

The existing Windows screen-area recorder is maintained in
[projects/screen-recorder/](projects/screen-recorder/). Its behavior and review
gates are captured in
[requirements.md](projects/screen-recorder/requirements.md).

From the repository root, install its dependencies and run the Python app:

```powershell
py -m pip install -r projects\screen-recorder\requirements.txt
py projects\screen-recorder\screen_recorder.py
```

The standalone Windows executable is
[ScreenRecorder.exe](projects/screen-recorder/dist/ScreenRecorder.exe). Use
`/build-exe` to regenerate it after the project's requirements and code reviews
pass.

See [the project log](projects/screen-recorder/EXPERIENCE.md) for prior
implementation notes and verification history. See
[.github/copilot-instructions.md](.github/copilot-instructions.md) for the
repository's agent workflow.
