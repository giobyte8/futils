# About: Datetime in EXIF tags:
#
# EXIF:DateTimeOriginal: When the shutter was clicked. This field is
# stored inside the file's metadata, and Mac Finder won't display it.
# Windows File Explorer will display it as Date Taken.
#
# EXIF:DateTimeDigitized: When the image was converted to digital form.
# For digital cameras, DateTimeDigitized will be the same as
# DateTimeOriginal; for scans of analog pics, DateTimeDigitized is the
# date of the scan, while DateTimeOriginal was when the shutter was
# clicked on the film camera. Mac Finder won't display it
#
# EXIF:DateTime: When photo software last modified the image or its
# metadata. LR reads that field but doesn't update it, as required by
# the EXIF standard. Neither Finder nor File Explorer display it.
#

import argparse
import os
from exif import Image
from fu.utils.path import list_files


_parser = argparse.ArgumentParser()
_parser.add_argument(
    'path',
    type=str,
    help='Path containing images/photos to fix'
)

_args = _parser.parse_args()
_photo_extensions = ['.jpg', '.jpeg']


class PhotoExifTools:
    def __init__(self, img):
        """
        Initilizes exif tools wrapper around provided
        image

        :param img: exif Image
        """
        self.img = img
        self.has_exif = img.has_exif

    def has_datetime(self):
        return self.has_exif and hasattr(self.img, 'datetime')

    def has_datetime_digitized(self):
        return self.has_exif and hasattr(self.img, 'datetime_digitized')

    def has_datetime_original(self):
        return self.has_exif and hasattr(self.img, 'datetime_original')

    def get_datetime(self):
        if self.has_datetime():
            return self.img.datetime
        return None

    def get_datetime_digitized(self):
        if self.has_datetime_digitized():
            return self.img.datetime_digitized
        return None

    def get_datetime_original(self):
        if self.has_datetime_original():
            return self.img.datetime_original
        return None

    def has_missing_fields(self):
        return not self.img.has_exif or \
            not hasattr(self.img, 'datetime') or \
            not hasattr(self.img, 'datetime_original') or \
            not hasattr(self.img, 'datetime_digitized')


for file in list_files(_args.path, _photo_extensions):
    filename = os.path.basename(file)
    with open(file, 'rb') as img_file:
        img = Image(img_file)
        exif_wrapper = PhotoExifTools(img)

    if exif_wrapper.has_missing_fields():
        print('\n{}: '.format(filename))
        print(' Datetime:  {}'.format(exif_wrapper.get_datetime()))
        print(' Original:  {}'.format(exif_wrapper.get_datetime_original()))
        print(' Digitized: {}'.format(exif_wrapper.get_datetime_digitized()))

        if not exif_wrapper.has_datetime():
            print('\nFixing datetime')
            print(' x Stop program')
            print(' 0 Skip file')
            print(' 1 Enter manually')

            if exif_wrapper.has_datetime_original():
                print(' 2 Copy from "datetime original"')
            if exif_wrapper.has_datetime_digitized():
                print(' 3 Copy from "datetime digitized"')

            selection = input(' > ')
            if selection is 'x':
                # TODO Implement
                pass
            if selection is '0':
                continue
        
        print()
