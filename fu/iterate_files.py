import typer

from rich.prompt import Confirm

from fu.utils.console import console
from fu.utils.path import (
    is_dir,
    path_files
)


def iterate_and_open(path: str, step: int = 1) -> None:
    """Will iterate each file found inside given path
    and will open it in default system program

    Args:
        path (str): Path to iterate over its files
        step (int): How many files open at a time
    """
    if not is_dir(path):
        console.print(
            'Path is not a valid directory: {}'.format(path),
            style='error'
        )

    currently_open_count = 0
    for file in path_files(path, ):
        typer.launch(file)
        console.print(
            ' Opening {}'.format(file),
            'info'
        )
        currently_open_count += 1
        
        if currently_open_count == step:
            if Confirm.ask('Open next {} file(s)'.format(step)):
                currently_open_count = 0
            else:
                break
