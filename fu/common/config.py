import tomllib
import logging
from typing import Optional

from fu.commands.config import config_file
from fu.common.errors import ConfigError


_CONFIG_CACHE: dict = {}
_CONFIG_LOADED = False
_logger = logging.getLogger(__name__)


def _read_config_file() -> dict:
    """Reads and returns raw config dict.

    Returns empty dict when file is missing or invalid shape.
    Raises ConfigError when TOML format is malformed.
    """
    try:
        raw_config = config_file.read_config()
    except FileNotFoundError:
        _logger.warning(
            "Config file not found. Run 'fu config --init' to create it."
        )
        return {}
    except tomllib.TOMLDecodeError as e:
        raise ConfigError("Invalid config file format (TOML parse error).") from e

    if not isinstance(raw_config, dict):
        return {}

    return raw_config


def _get_config(section: str) -> dict:
    global _CONFIG_LOADED
    global _CONFIG_CACHE

    if not _CONFIG_LOADED:
        _CONFIG_CACHE = _read_config_file()
        _CONFIG_LOADED = True

    section_data = _CONFIG_CACHE.get(section)
    if not isinstance(section_data, dict):
        raise ConfigError(f"Config section not found: {section}")

    return section_data


def tmdb(config_key: str) -> Optional[str]:
    section = _get_config("tmdb")
    value = section.get(config_key)
    if not isinstance(value, str):
        return None

    return value