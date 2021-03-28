import typer

from fu.imgresize.resizer import resize_images

def main(
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
    typer.echo(f"Converting {src_dir}")

if __name__ == "__main__":
    typer.run(main)
