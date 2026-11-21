import json
import os
import re
from pathlib import Path
from typing import Mapping


TITLES = ("nfsu2_revived", "vice_city_web")
SHELL_METACHARS = re.compile(r"[;&|`$<>]")


class ConfigurationError(ValueError):
    pass


def default_config_path() -> Path:
    app_data = os.environ.get("APPDATA")
    base = Path(app_data) if app_data else Path.home() / "AppData" / "Roaming"
    return base / "NFSU2ViceCityLauncher" / "config.json"


def validate_local_executable(value: object) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str):
        raise ConfigurationError("The configured executable path must be text.")
    if not value.strip():
        return None
    if "\x00" in value or "\r" in value or "\n" in value:
        raise ConfigurationError("The configured executable path contains invalid characters.")
    if SHELL_METACHARS.search(value):
        raise ConfigurationError("The configured executable path contains unsupported shell characters.")

    path = Path(os.path.abspath(os.path.expandvars(value.strip())))
    if not path.is_absolute():
        raise ConfigurationError("The configured executable path must be absolute.")
    if not path.is_file():
        raise ConfigurationError(f"Configured executable does not exist: {path}")
    return str(path)


def validate_stored_local_executable(value: object) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str):
        raise ConfigurationError("The configured executable path must be text.")
    if not value.strip():
        return None
    if "\x00" in value or "\r" in value or "\n" in value:
        raise ConfigurationError("The configured executable path contains invalid characters.")
    if SHELL_METACHARS.search(value):
        raise ConfigurationError("The configured executable path contains unsupported shell characters.")

    path = Path(os.path.abspath(os.path.expandvars(value.strip())))
    if not path.is_absolute():
        raise ConfigurationError("The configured executable path must be absolute.")
    return str(path)


def load_config(path: Path | None = None) -> dict[str, str | None]:
    config_path = path or default_config_path()
    if not config_path.exists():
        return {title: None for title in TITLES}
    try:
        data = json.loads(config_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ConfigurationError(f"Could not read launcher configuration: {exc}") from exc
    if not isinstance(data, dict):
        raise ConfigurationError("Launcher configuration must be a JSON object.")

    result: dict[str, str | None] = {}
    for title in TITLES:
        result[title] = validate_stored_local_executable(data.get(title))
    return result


def save_config(config: Mapping[str, object], path: Path | None = None) -> None:
    unknown = set(config) - set(TITLES)
    if unknown:
        raise ConfigurationError("Launcher configuration contains unknown fields.")

    validated: dict[str, str | None] = {}
    for title in TITLES:
        value = config.get(title)
        if value is None:
            validated[title] = None
        else:
            validated[title] = validate_stored_local_executable(value)

    config_path = path or default_config_path()
    config_path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = config_path.with_suffix(config_path.suffix + ".tmp")
    temp_path.write_text(json.dumps(validated, indent=2), encoding="utf-8")
    temp_path.replace(config_path)
