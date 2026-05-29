import typer

from .fix_name import FixNameCmd


app = typer.Typer()


@app.command()
def fix_name(
    src_dir: str = typer.Argument(
        "./",
        help="Directory containing movie files to rename"
    )
):
    """Renames movie files to make them scanners friendly
    """
    FixNameCmd(src_dir).execute()
