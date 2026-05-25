import typer

from fu.commands.base_command import Command, RichConsoleLogger
from . import config_file


class ViewConfigCmd(Command):
    """Displays the current application configuration.
    Auto-initializes the config file with defaults if it does not exist.
    """

    def __init__(self, logger=None):
        super().__init__("config", logger or RichConsoleLogger())

    def execute(self) -> None:
        if not config_file.config_file_exists():
            self.logger.info("Config file not found. Initializing with defaults...")
            config_file.init_config_file()
            self.logger.info(
                f"Config file created at {config_file.config_file_path()}"
            )

        try:
            content = config_file.get_config_content_str()
            self.logger.info(content)
        except Exception as e:
            self.logger.error(f"Error reading config file: {e}")
            raise typer.Exit(code=1)


class InitConfigCmd(Command):
    """Initializes the application config file with default values.
    Warns and exits if the config file already exists.
    """

    def __init__(self, logger=None):
        super().__init__("config", logger or RichConsoleLogger())

    def execute(self) -> None:
        if config_file.config_file_exists():
            self.logger.warning(
                f"Config file already exists at {config_file.config_file_path()}"
            )
            raise typer.Exit()

        config_file.init_config_file()
        self.logger.info(
            f"Config file initialized at {config_file.config_file_path()}"
        )


class EditConfigCmd(Command):
    """Opens the application config file in the system default editor.
    Auto-initializes the config file with defaults if it does not exist.
    """

    def __init__(self, logger=None):
        super().__init__("config", logger or RichConsoleLogger())

    def execute(self) -> None:
        if not config_file.config_file_exists():
            self.logger.info("Config file not found. Initializing with defaults...")
            config_file.init_config_file()
            self.logger.info(
                f"Config file created at {config_file.config_file_path()}"
            )

        typer.launch(str(config_file.config_file_path()))
