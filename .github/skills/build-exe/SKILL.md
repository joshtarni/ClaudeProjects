---
name: build-exe
description: "Build or regenerate a standalone one-file Windows .exe from a Python app. Use for PyInstaller one-file packaging, refreshing an executable after source changes, or bundling runtime dependencies and tools such as FFmpeg."
argument-hint: "Optionally name the Python entry point or executable to build"
---

# Build a Standalone One-File Windows Executable

Build or refresh a Python application's Windows executable so it includes the
Python runtime and required dependencies. The result should run on a compatible
Windows machine without a separate Python installation.

## Procedure

1. Inspect the repository and worktree before building:
   - Find the Python entry point, dependency manifests, README build instructions,
     existing PyInstaller spec files or scripts, and expected output location.
   - Review relevant uncommitted changes. Preserve them and build from the
     current source; do not revert, stash, or overwrite unrelated work.
   - Prefer the project's established build configuration when it produces the
     requested one-file executable. Otherwise use PyInstaller if available.
2. Confirm the target platform and application type. Build Windows executables
   on Windows. Use a GUI/no-console option only for GUI applications.
3. Ensure build dependencies are already available. Install or restore packages
   only when the project manifest changed or a required build command reports a
   missing dependency. Do not edit the dependency manifest just to add
   PyInstaller unless the user requested a reproducible build setup.
4. Build in one-file mode from the current entry point. Include required package
   data and binaries, not just Python modules. For example, when using
   `imageio-ffmpeg`, collect its data so its FFmpeg binary is available at
   runtime:

   ```powershell
   py -m PyInstaller --noconfirm --clean --onefile --windowed `
     --name MyApp --distpath dist --workpath build --specpath build `
     --collect-all imageio_ffmpeg main.py
   ```

   Adapt the options to the application. Do not add `--windowed` for a
   console application, and use `--collect-all` for packages whose required
   resources or binaries are not otherwise collected. Prefer maintaining a
   project's existing spec file if it already captures those requirements.
5. Verify the exact output path exists and has a fresh timestamp. Review
   PyInstaller warnings for missing modules or data that the app actually
   requires. Inspect the executable archive (for example,
   `py -m PyInstaller.utils.cliutils.archive_viewer -l dist\MyApp.exe`) to
   confirm it contains the application entry point and required bundled
   dependencies/binaries.
6. Smoke-test the built executable. For a GUI, confirm the process starts and
   stays alive long enough to initialize; for a console app, check its expected
   startup behavior. Stop only the specific process started for the test. Run
   relevant source tests or syntax checks when appropriate. Do not claim that a
   smoke test proves every feature works.
7. Leave the requested executable in its expected output location. Remove only
   temporary build outputs created for this invocation when safe and clearly
   disposable; preserve pre-existing user files and build configuration.
   Report the output path, size, validation performed, and any limitations.

## Important Notes

- One-file means the runtime, Python code, and collected dependencies are
  packaged together. It does not mean the program has no operating-system or
  hardware requirements. PyInstaller one-file apps commonly extract bundled
  files to a temporary directory on launch; external resources must be
  explicitly included and located correctly by the application.
- Large executables are expected when bundling substantial native packages,
  media libraries, or FFmpeg. Do not remove required components merely to reduce
  size.
- Do not overwrite or commit generated binaries unless the user requested an
  updated executable. Preserve repository conventions for tracking build
  artifacts.
