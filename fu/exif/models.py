from exif import Image
from pathlib import Path

from fu.utils.path import is_file
from .errors import PathIsntImageError


IMG_EXTENSIONS = ('.jpg', '.jpeg')


class ROExifImage:
    """Wraps an image file path to access its exif metadata.
        Metadata is available for read only.
    """

    def __init__(self, path: Path) -> None:
        if not is_file(path):
            raise PathIsntImageError(path)

        with open(path, 'rb') as image_file:
            self._path = path
            self._image = Image(image_file)

    def has_datetime(self):
        return self._image.has_exif and hasattr(self._image, 'datetime')

    def has_datetime_digitized(self):
        return self._image.has_exif and hasattr(self._image, 'datetime_digitized')

    def has_datetime_original(self):
        return self._image.has_exif and hasattr(self._image, 'datetime_original')

    @property
    def basename(self):
        return self._path.name

    @property
    def datetime(self):
        """Time when the file was created. \
            In a digital camera, usually is the same time the image \
            was taken.\
            If the image was edited, this could be the time the new \
            file (edited version) was created.

        Returns:
            datetime: Date and time of file creation
        """
        if self.has_datetime():
            return self._image.datetime
        return None

    @property
    def datetime_original(self):
        """Time when the image was taken

        Returns:
            datetime: Date and time when image was captured
        """
        if self.has_datetime_original():
            return self._image.datetime_original
        return None

    @property
    def datetime_digitized(self):
        """Time when image was digitalized, e.g. the moment it was scanned

        Returns:
            datetime: Date and time when image was digitalized
        """
        if self.has_datetime_digitized():
            return self._image.datetime_digitized
        return None

