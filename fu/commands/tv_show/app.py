import typer

from .fix_names import FixNamesCmdBuilder


app = typer.Typer()


@app.command()
def fix_names(
    src_dir: str = typer.Argument(
        "./",
        help="Directory containing tv show files to rename"
    )
):
    """Renames TV Show files in a given directory
    """
    cmd = FixNamesCmdBuilder.from_src_dir(src_dir)
    cmd.execute()
