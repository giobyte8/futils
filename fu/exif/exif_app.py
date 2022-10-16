import typer
from fu.exif import inspect_datetime


app = typer.Typer()


@app.command()
def inspect(
    path: str = typer.Argument(
        ...,
        help='Path to directory containing images to inspect'
    ),
    step: int = typer.Option(
        100,
        '--page-size',
        '-p',
        help='How many images inspect at a time'
    )
):
    """Display exif date for all images found at given directory
    """
    inspect_datetime.inspect_dir(path, step)