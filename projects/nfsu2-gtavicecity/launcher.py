import os
import subprocess
from pathlib import Path
from typing import Sequence


class LaunchError(RuntimeError):
    pass


def validate_launch_target(value: str | os.PathLike[str]) -> Path:
    raw = os.fspath(value)
    if not isinstance(raw, str) or not raw.strip():
        raise LaunchError("A local executable path is required.")
    if "\x00" in raw or "\r" in raw or "\n" in raw:
        raise LaunchError("The executable path is malformed.")
    if any(char in raw for char in ";&|`$<>"):
        raise LaunchError("The executable path contains unsupported shell characters.")

    path = Path(os.path.abspath(raw))
    if not path.is_file():
        raise LaunchError("The configured executable is missing or is not a file.")
    return path


def launch_local(target: str | os.PathLike[str]) -> subprocess.Popen[bytes]:
    path = validate_launch_target(target)
    try:
        return subprocess.Popen(
            [str(path)],
            shell=False,
            cwd=str(path.parent),
            close_fds=True,
        )
    except OSError as exc:
        raise LaunchError(f"Could not start the local executable: {exc}") from exc


def process_arguments_contain_no_shell(arguments: Sequence[str]) -> bool:
    return not any("\x00" in argument or "\r" in argument or "\n" in argument for argument in arguments)
