import subprocess
import sys
from pathlib import Path

import pytest

from launcher import LaunchError, launch_local, validate_launch_target


def test_valid_fake_target_starts(tmp_path):
    process = launch_local(sys.executable)
    assert isinstance(process, subprocess.Popen)
    process.terminate()
    process.wait(timeout=5)


def test_missing_target_is_rejected(tmp_path):
    with pytest.raises(LaunchError, match="missing"):
        validate_launch_target(tmp_path / "missing.exe")


@pytest.mark.parametrize("suffix", [";calc.exe", " & calc.exe", "`calc.exe", "\ncalc.exe"])
def test_malformed_target_is_rejected(tmp_path, suffix):
    target = tmp_path / ("game.exe" + suffix)
    with pytest.raises(LaunchError):
        validate_launch_target(str(target))
