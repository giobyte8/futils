import typer

from fu.exif import inspect_datetime
from fu.imgresize.resizer import resize_images
from fu.iterate_files import iterate_and_open, iterate_from_file
from fu.movie.fixname import rename_movies
from fu.tvshow.fixname import rename_tvshow_files


app = typer.Typer()

@app.command()
def imgresize(
    src_dir: str = typer.Argument(
        "./",
        help="Directory containing images to resize"
    ),
    tgt_width: int = typer.Option(
        1920,
        "--width",
        "-w",
        help="Desired width in pixels"
    ),
    tgt_height: int = typer.Option(
        1080,
        "--height",
        "-h",
        help="Desired height in pixels"
    ),
    dst_dir: str = typer.Option(
        None,
        "--dst-dir",
        "-d",
        help="Destination directory for resized images"
    )
):
    """Resize images to smaller resolution applying same effect
    as css 'cover'
    """
    resize_images(src_dir, tgt_width, tgt_height, dst_dir)


@app.command()
def moviefixname(src_dir: str = typer.Argument(
    "./",
    help="Directory containing movie files to rename"
)):
    """Renames movie files to make them scanners friendly
    """
    rename_movies(src_dir)

@app.command()
def tvshowfixnames(
    src_dir: str = typer.Argument(
        "./",
        help="Directory containing tv show files to rename"
    )
):
    """Renames TV Show files to make them scanners friendly
    """
    rename_tvshow_files(src_dir)


@app.command()
def iterate(
    path: str = typer.Argument(
        "./",
        help="Directory containing files to iterate over"
    ),
    step: int = typer.Option(
        1,
        "--step",
        "-s",
        help="Number of files to open at a time"
    )
):
    """Iterates all files in given path and opens them
    in default system application
    """
    iterate_and_open(path, step)

@app.command()
def iteratefrom(
    path: str = typer.Argument(
        ...,
        help='Path to file containing the paths to iterate'
    ),
    step: int = typer.Option(
        1,
        '--step',
        '-s',
        help='Number of files to open at a time'
    )
):
    """Will iterate each line of given file as a path
    and will open it in default system program.

    Empty lines or lines starting with '#' will be
    ignored.
    """
    iterate_from_file(path, step)


@app.command()
def exif(
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
    """Will inspect exif date for all images found at given directory
    """
    inspect_datetime.inspect_dir(path, step)


@app.command()
def exif_pathsfile(
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


if __name__ == "__main__":
    app()