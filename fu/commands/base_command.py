from abc import ABC, abstractmethod
from fu.utils.console import console


class CmdLogger(ABC):
    """Depending on the context where the command is executed \
    it's logger might be configured different. For example if its \
    manually executed from terminal, then, a console rich color \
    logger would be nice, however, if executed in background, then, \
    a file logger might fit better
    """

    @abstractmethod
    def info(self, msg: str) -> None:
        pass

    @abstractmethod
    def warning(self, msg: str) -> None:
        pass

    @abstractmethod
    def error(self, msg: str) -> None:
        pass


class RichConsoleLogger(CmdLogger):

    def info(self, msg: str) -> None:
        console.print(msg)

    def warning(self, msg: str) -> None:
        console.print(msg, style='warning')

    def error(self, msg: str) -> None:
        console.print(msg, style='error')


class Command:
    name: str

    def __init__(self, name: str, logger: CmdLogger = RichConsoleLogger()):
        self.name = name
        self.logger = logger

    def execute(self):
        raise NotImplementedError()
