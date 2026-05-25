import tomllib
from unittest import mock

import pytest

import fu.common.config as config_module
from fu.common.config import tmdb
from fu.common.errors import ConfigError


def _reset_config_cache() -> None:
    config_module._CONFIG_CACHE = {}
    config_module._CONFIG_LOADED = False


def _config_with_tmdb_value(value):
    return {
        "tmdb": {
            "api_key": value
        }
    }


@pytest.fixture(autouse=True)
def reset_config_cache_fixture():
    _reset_config_cache()


class TestTmdbConfigAccess:
    @mock.patch("fu.common.config.config_file.read_config")
    def test_tmdb_returns_value(self, mock_read_config):
        mock_read_config.return_value = _config_with_tmdb_value("abc123")

        assert tmdb("api_key") == "abc123"

    @mock.patch("fu.common.config.config_file.read_config")
    def test_tmdb_raises_when_section_missing(self, mock_read_config):
        mock_read_config.return_value = {}

        with pytest.raises(ConfigError, match="Config section not found: tmdb"):
            tmdb("api_key")

    @mock.patch("fu.common.config.config_file.read_config")
    def test_tmdb_returns_raw_placeholder_value(self, mock_read_config):
        mock_read_config.return_value = _config_with_tmdb_value("<your_api_key_here>")

        assert tmdb("api_key") == "<your_api_key_here>"

    @mock.patch("fu.common.config.config_file.read_config")
    @mock.patch("fu.common.config._logger")
    def test_tmdb_logs_warning_and_raises_when_file_missing(
        self, mock_logger, mock_read_config
    ):
        mock_read_config.side_effect = FileNotFoundError("missing")

        with pytest.raises(ConfigError, match="Config section not found: tmdb"):
            tmdb("api_key")

        mock_logger.warning.assert_called_once_with(
            "Config file not found. Run 'fu config --init' to create it."
        )

    @mock.patch("fu.common.config.config_file.read_config")
    def test_tmdb_raises_parse_errors(self, mock_read_config):
        mock_read_config.side_effect = tomllib.TOMLDecodeError("invalid", "", 0)

        with pytest.raises(ConfigError, match="Invalid config file format"):
            tmdb("api_key")

    @mock.patch("fu.common.config.config_file.read_config")
    def test_tmdb_returns_none_when_key_missing(self, mock_read_config):
        mock_read_config.return_value = {
            "tmdb": {
                "other": "x"
            }
        }

        assert tmdb("api_key") is None

    @mock.patch("fu.common.config.config_file.read_config")
    def test_tmdb_returns_none_for_non_string_value(self, mock_read_config):
        mock_read_config.return_value = _config_with_tmdb_value(123)

        assert tmdb("api_key") is None

    @mock.patch("fu.common.config.config_file.read_config")
    def test_tmdb_uses_cached_config_after_first_read(self, mock_read_config):
        mock_read_config.return_value = _config_with_tmdb_value("abc123")

        assert tmdb("api_key") == "abc123"
        assert tmdb("api_key") == "abc123"
        assert mock_read_config.call_count == 1