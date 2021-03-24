import os
from PIL import Image
from pathlib import Path
from dataclasses import (
    dataclass,
    field
)
from resizeimage import resizeimage

from futils.utils.path import (
    get_file_name,
    is_dir,
    path_files
)


_img_formats = ['.png', '.jpg', '.jpeg']

@dataclass
class ResizeOrder:
    """A Wrapper for results of resize preview operations

    Args:
        src_dir (str): uri to directory where images to resize   \
            are located
        tgt_width (int): Desired width in pixels
        tgt_height (int): Desired height in pixels
        dst_dir (str): Path to destination directory where       \
            resized image are going to be saved
        gral_errors (list[str]): General errors, resize will not \
            be possible
        invalid_images (list[str]): uri of images that can't be  \
            resized, most likely cause it has smaller size than  \
            desired output
        existent_images (list[ResizedImg]): Images that already  \
            exists in target directory
        ok_images (list[ResizedImg]): Images that can be resized \
            without issues
        execute (bool): Indicates if order was approved by user  \
            for execution
        overwrite (bool): Indicate if user request overwrite     \
            already existent images
    """

    src_dir: str
    tgt_width: int
    tgt_height: int

    dst_dir: str = None
    gral_errors: list = field(default_factory=list)

    invalid_images: list = field(default_factory=list)
    existent_images: list = field(default_factory=list)
    ok_images: list = field(default_factory=list)

    execute: bool = False
    overwrite: bool = False

    def has_warnings(self) -> bool:
        return self.existent_images or self.invalid_images


@dataclass
class ResizedImg:
    src_file: str
    dst_file: str


class TargetSizeError(Exception):
    pass


class TargetDirNotFoundError(Exception):
    pass


def resize_images(
        src_dir: str,
        tgt_width: int,
        tgt_height: int,
        dst_dir: str = None
    ) -> None:
    
    if tgt_width < 320 or tgt_height < 480:
        raise TargetSizeError()

    resize_order = ResizeOrder(src_dir, tgt_width, tgt_height, dst_dir)
    _evaluate_preview_result(_preview_resize(resize_order))

    if not resize_order.execute:
        return None

    if not resize_order.dst_dir:
        resize_order.dst_dir = _make_destination_dir_uri(
            resize_order.src_dir,
            resize_order.tgt_width,
            resize_order.tgt_height
        )

    if not is_dir(resize_order.dst_dir):
        Path(resize_order.dst_dir).mkdir(parents=True, exist_ok=True)
        
        # Verify directory was created
        if not is_dir(resize_order.dst_dir):
            raise TargetDirNotFoundError()

    for resize_img in resize_order.ok_images:
        resize_img.dst_file = _resize(
            resize_img.src_file,
            tgt_width,
            tgt_height,
            dst_dir
        )

    if resize_order.overwritten_images and resize_order.overwrite_allowed:
        for resize_img in resize_order.overwritten_images:
            resize_img.dst_file = _resize(
                resize_img.src_file,
                tgt_width,
                tgt_height,
                dst_dir
            )
        

def _resize(src_file: str, tgt_width: int, tgt_height: int, dst_dir: str):
    """Resizes provided image file into indicated width    \
    and height and stores resulting images into dst_dir

    Args:
        src_file (str): Path to source file image
        tgt_width (int): Desired width in pixels
        tgt_height (int): Desired height in pixels
        dst_dir (str): Path to destination directory where \
            resized image is going to be saved

    Returns:
        str: Path to resized image file
    """
    if tgt_width < 320 or tgt_height < 480:
        raise TargetSizeError()

    dst_file = ''
    with Image.open(src_file) as img:
        resized_img = resizeimage.resize_cover(
            img,
            [tgt_width, tgt_height]
        )

        dst_file = _make_destination_uri(
            src_file,
            dst_dir,
            tgt_width,
            tgt_height
        )
        
        resized_img.save(dst_file, img.format)
    
    return dst_file


def _preview_resize(resize_order: ResizeOrder) -> ResizeOrder:
    """Verify if resize operation will be possible with provided
    parameters. Resize operations will NOT be done by this method.

    Args:
        resize_order (ResizeOrder): Resize order with tgt_width \
            and tgt_height assigned
    Returns
        ResizeOrder: Resize order with images and errors updated
    """

    if resize_order.tgt_width < 320:
        resize_order.gral_errors.append('Minimal supported width is 320px')

    if resize_order.tgt_height < 480:
        resize_order.gral_errors.append('Minimal supported height is 480px')
    
    if resize_order.gral_errors:
        return resize_order

    if not resize_order.dst_dir:
        resize_order.dst_dir = _make_destination_dir_uri(
            resize_order.src_dir,
            resize_order.tgt_width,
            resize_order.tgt_height
        )

    # Validate each image
    for img_file in path_files(resize_order.src_dir, _img_formats):
        with Image.open(img_file) as img:
            img_w, img_h = img.size
            
            if img_w < resize_order.tgt_width:
                resize_order.invalid_images.append(img_file)
                continue
            
            if img_h < resize_order.tgt_height:
                resize_order.invalid_images.append(img_file)
                continue

            destination = _make_destination_uri(
                img_file,
                resize_order.dst_dir,
                resize_order.tgt_width,
                resize_order.tgt_height
            )
            if Path(destination).exists():
                resize_order.existent_images.append(ResizedImg(
                    src_file=img_file,
                    dst_file=None
                ))

            else:
                resize_order.ok_images.append(ResizedImg(
                    src_file=img_file,
                    dst_file=None
                ))

    # Verify there are images to resize
    if not resize_order.ok_images and not resize_order.existent_images:
        resize_order.gral_errors.append('Valid images for resize not found')

    return resize_order


def _evaluate_preview_result(resize_order: ResizeOrder) -> ResizeOrder:
    """Evaluates preview result and shows errors or warnings
    to user. If there are warnings, will ask user if should
    proceed or cancel resize

    Args:
        result (PreviewResult): Resize preview results

    Returns:
        ResizeOrder: Indicates if resize should proceed proceed
    """
    if not result.gral_errors and not result.has_warnings():
        return True
    
    if result.gral_errors:
        # TODO Show errors
        return False

    if result.invalid_images:
        # TODO Show invalid images
        pass

    if result.existent_images:
        # TODO Show existent images
        pass

    # TODO Show resume X Images will be transformed, X Iamges will be overriden
    # TODO Ask user for confirmation


def _make_destination_uri(src_file: str, dst_dir: str,
                          width: int, height: int):
    """Creates destination uri for provided image file

    Args:
        src_file (str): Path to source image file
        dst_dir (str): Destination directory path
        width (int): Width in pixels
        height (int): Height in pixels
    """
    filename = get_file_name(src_file, include_extension=False)
    file_ext = Path(src_file).suffix

    dst_file_name = '{}_{}x{}{}'.format(
        filename,
        width,
        height,
        file_ext
    )

    return os.path.join(
        dst_dir,
        dst_file_name
    )


def _make_destination_dir_uri(source_dir: str, width: int,
                              height: int):
    """Creates destination directory uri

    Args:
        source_dir (str): Path to source directory
        width (int): Width in pixels
        height (int): Height in pixels
    """
    dir_name = '{}x{}'.format(width, height)
    return os.path.join(source_dir, dir_name)
