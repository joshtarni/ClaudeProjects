from pathlib import Path

import pytest

from config import ConfigurationError, load_config, save_config, validate_local_executable


def test_missing_config_is_empty(tmp_path):
    assert load_config(tmp_path / "missing.json") == {
        "nfsu2_revived": None,
        "vice_city_web": None,
    }


def test_shell_metacharacters_are_rejected(tmp_path):
    target = tmp_path / "game.exe"
    target.write_text("")
    for value in (
        f"{target} & calc.exe",
        f"{target};calc.exe",
        f"{target}|calc.exe",
        f"{target}`calc.exe",
        f"{target}$env",
        f"{target}\ncalc.exe",
    ):
        with pytest.raises(ConfigurationError):
            validate_local_executable(value)


def test_config_round_trip_preserves_only_local_paths(tmp_path):
    executable = tmp_path / "game.exe"
    executable.write_text("")
    config_path = tmp_path / "config.json"

    save_config(
        {"nfsu2_revived": str(executable), "vice_city_web": None},
        path=config_path,
    )

    loaded = load_config(config_path)
    assert loaded == {"nfsu2_revived": str(executable), "vice_city_web": None}
    assert "http" not in config_path.read_text(encoding="utf-8")


def test_load_preserves_missing_configured_path_for_title(tmp_path):
    missing = tmp_path / "removed-game.exe"
    config_path = tmp_path / "config.json"
    config_path.write_text(
        '{"nfsu2_revived": "%s", "vice_city_web": null}' % missing.as_posix(),
        encoding="utf-8",
    )

    loaded = load_config(config_path)
    assert loaded == {"nfsu2_revived": str(missing), "vice_city_web": None}
