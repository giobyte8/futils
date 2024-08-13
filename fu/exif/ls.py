from pathlib import Path
from rich.table import Table
from fu.utils.console import console
from fu.utils.path import path_files
from .models import IMG_EXTENSIONS, ROExifImage


class ImgMetaTable:

    def __init__(self) -> None:
        self._table = Table()
        self._table.add_column('Filename')
        self._table.add_column('File creation time')
        self._table.add_column('Original datetime')
        self._table.add_column('Digitalized datetime')

    def add_image(self, img: ROExifImage):
        self._table.add_row(
            img.basename,
            img.datetime,
            img.datetime_original,
            img.datetime_digitized
        )

    def print(self) -> None:
        console.print(self._table)


def ls_datetime(path: Path, step: int = 0) -> None:
    """Scans given path for images and displays exif datetime for each
        image found.

    Args:
        path (Path): Path to scan for images
        step (int, optional): If > 0, indicates the number of images to display
            at a time in output table. Defaults to 0.
    """
    m_table = ImgMetaTable()

    for img_path in path_files(path, IMG_EXTENSIONS):
        img_path = Path(img_path)

        img = ROExifImage(img_path)
        m_table.add_image(img)

    m_table.print()
