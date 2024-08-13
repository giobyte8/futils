import typer
from fu.exif import inspect_datetime
from .ls import ls_datetime


app = typer.Typer()


@app.command()
def ls(
    path: str = typer.Argument(
        ...,
        help='Path to inspect'
    )
):
    """List all image files and its exif dates in a given directory
    """
    ls_datetime(path)


@app.command('inspect-from-pathsfile')
def inspect_from_pathsfile(
    path: str = typer.Argument(
        ...,
        help='Path to file containing images paths'
    ),
    step: int = typer.Option(
        1,
        '--step',
        '-s',
        help='How many images/paths inspect at a time'
    ),
    display: bool = typer.Option(
        False,
        '--display',
        '-d',
        help='Indicates if each image should be displyed in system viewer'
    )
):
    """Inspects exif datetime metadata for all file paths contained in a specific text file
    """
    inspect_datetime.inspect_from_file(path, step, display)
