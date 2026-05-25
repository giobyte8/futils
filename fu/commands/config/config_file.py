"""Config file management for futils application."""

from pathlib import Path
import tomllib

from platformdirs import user_config_dir


def config_file_path() -> Path:
    """Return the path to the futils config file."""
    config_dir = Path(user_config_dir("futils"))
    return config_dir / "config.toml"


def config_file_exists() -> bool:
    """Check if the config file exists."""
    return config_file_path().exists()


def init_config_file() -> None:
    """Initialize the config file with default values."""
    path = config_file_path()

    # Create directory if it doesn't exist
    path.parent.mkdir(parents=True, exist_ok=True)

    # Write default config
    default_content = """[tmdb]
api_key = "<your_api_key_here>"
"""
    path.write_text(default_content)


def read_config() -> dict:
    """Read and parse the config file.

    Returns:
        dict: Parsed TOML configuration

    Raises:
        FileNotFoundError: If config file does not exist
        tomllib.TOMLDecodeError: If config file has invalid TOML syntax
    """
    path = config_file_path()
    if not path.exists():
        raise FileNotFoundError(f"Config file not found at {path}")

    with open(path, "rb") as f:
        return tomllib.load(f)


def get_config_content_str() -> str:
    """Read the raw config file content as a string."""
    path = config_file_path()
    if not path.exists():
        raise FileNotFoundError(f"Config file not found at {path}")
    return path.read_text()
