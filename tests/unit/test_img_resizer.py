import pytest
import os
import shutil
import tempfile
import uuid

from PIL import Image
from pathlib import Path
from unittest import mock

import futils

from futils.img_resizer import (
    TargetSizeError,
    ResizeOrder,
    resize_images,
    _resize,
    _preview_resize,
    _make_destination_uri,
    _make_destination_dir_uri
)


@pytest.fixture
def tmp_dir():
    """Creates a temporary unique directory
    """
    tmp_dir = os.path.join(tempfile.gettempdir(), _unique_str())
    Path(tmp_dir).mkdir(parents=True, exist_ok=True)

    yield tmp_dir

    # Cleanup after usage
    shutil.rmtree(tmp_dir)


def _create_fake_images(dst_dir, width, height, n) -> list:
    """Creates n number of images in /tmp dir
    of indicated dimensions

    Args:
        dst_dir (str): Dir where images will be saved
        width (int): Images width in pixels
        height (int): Images height in pixels
        n (int): Number of fake images to create

    Returns:
        list: A list of images absolute paths
    """
    img_files = []

    for i in range(0, n):
        img_file = os.path.join(
            dst_dir,
            '{}.jpg'.format(_unique_str())
        )

        img = Image.new('RGB', (width, height), color='black')
        img.save(img_file)

        img_files.append(img_file)

    return img_files


def _unique_str():
    """Creates a random unique string (UUID4) that
    can be used as name for temp directories/files

    Returns:
        str: UUID4 String
    """
    return str(uuid.uuid4())


class TestResizeImages:
    def mock_eval_preview_result_abort(self, preview_result):
            preview_result.execute = False

    def mock_resize_img_do_nothing(src_file, w, h, dst_dir):
        return src_file

    def test_resize_images_wrong_width(self):
        with pytest.raises(TargetSizeError):
            resize_images(None, 319, 1080)

    def test_resize_images_wrong_height(self):
        with pytest.raises(TargetSizeError):
            resize_images(None, 1920, 479)

    @mock.patch('futils.img_resizer._resize')
    def test_resize_images_aborted_by_user(self, mock_resize, tmp_dir):
        with mock.patch.object(
            futils.img_resizer,
            '_evaluate_preview_result',
            new=self.mock_eval_preview_result_abort
        ):
            resize_result = resize_images(
                tmp_dir,
                1920,
                1080
            )

        assert not resize_result
        mock_resize.assert_not_called()


class TestResize:
    def test_resize_wrong_width(self):
        with pytest.raises(TargetSizeError):
            _resize(None, 300, 1080, None)
    
    def test_resize_wrong_height(self):
        with pytest.raises(TargetSizeError):
            _resize(None, 1920, 479, None)

    def test_resize(self, tmp_dir):
        tgt_width = 1920
        tgt_height= 1080

        images = _create_fake_images(tmp_dir, 4000, 4000, 1)
        resized_img = _resize(images[0], tgt_width, tgt_height, tmp_dir)

        with Image.open(resized_img) as img:
            img_w, img_h = img.size

            assert img_w == tgt_width
            assert img_h == tgt_height


class TestPreviewResize:
    def test_preview_resize_gral_err_width(self):
        resize_order = _preview_resize(ResizeOrder('/tmp', 300, 4000))
        assert resize_order.gral_errors
        assert len(resize_order.gral_errors) == 1

    def test_preview_resize_gral_err_height(self):
        resize_order = _preview_resize(ResizeOrder('/tmp', 3000, 400))
        assert resize_order.gral_errors
        assert len(resize_order.gral_errors) == 1

    def test_preview_resize_gral_err_size(self):
        resize_order = _preview_resize(ResizeOrder('/tmp', 300, 400))
        assert resize_order.gral_errors
        assert len(resize_order.gral_errors) == 2

    def test_preview_resize_no_images(self, tmp_dir):
        resize_order = _preview_resize(ResizeOrder(tmp_dir, 1920, 1080))
        
        assert not resize_order.ok_images
        assert len(resize_order.gral_errors) == 1

    def test_preview_resize_no_valid_width_images(self, tmp_dir):
        _create_fake_images(tmp_dir, 800, 2000, 2)      # Invalid
        resize_order = _preview_resize(ResizeOrder(tmp_dir, 1920, 1080))
        
        assert not resize_order.ok_images
        assert len(resize_order.gral_errors) == 1

    def test_preview_resize_no_valid_height_images(self, tmp_dir):
        _create_fake_images(tmp_dir, 2000, 600, 2)      # Invalid
        resize_order = _preview_resize(ResizeOrder(tmp_dir, 1920, 1080))
        
        assert not resize_order.ok_images
        assert len(resize_order.gral_errors) == 1

    def test_preview_resize_2_invalid_2_valid(self, tmp_dir):
        _create_fake_images(tmp_dir, 800, 600, 2)    # Invalid
        _create_fake_images(tmp_dir, 2000, 2000, 2)  # Valid

        resize_order = _preview_resize(ResizeOrder(tmp_dir, 1920, 1080))
        
        assert len(resize_order.ok_images) == 2
        assert len(resize_order.invalid_images) == 2

    def test_preview_10_valid(self, tmp_dir):
        _create_fake_images(tmp_dir, 2000, 2000, 10)
        resize_order = _preview_resize(ResizeOrder(tmp_dir, 1920, 1080))

        assert len(resize_order.ok_images) == 10
        assert not resize_order.gral_errors
        assert not resize_order.invalid_images
        assert not resize_order.existent_images


class TestMakeDestinationUri:
    def test_make_destination_uri_rel(self):
        src_file = 'Light.png'
        dst_dir = '/media/nobody/w/static'

        dst = _make_destination_uri(
            src_file,
            dst_dir,
            1920,
            1080
        )

        assert dst == '{}/Light_1920x1080.png'.format(dst_dir)

    def test_make_destination_uri_abs(self):
        src_file = '/media/nobody/w/static/Light.png'
        dst_dir = '/media/nobody/w/static/1920x1080'

        dst = _make_destination_uri(
            src_file,
            dst_dir,
            1920,
            1080
        )

        assert dst == '{}/Light_1920x1080.png'.format(dst_dir)

    def test_make_destination_uri_spaces(self):
        src_file = '/media/no body/w/static/Light.png'
        dst_dir = '/media/no body/w/static/1920x1080'

        dst = _make_destination_uri(
            src_file,
            dst_dir,
            1920,
            1080
        )

        assert dst == '{}/Light_1920x1080.png'.format(dst_dir)


class TestMakeDestinationDirUri:
    def test_make_destination_dir_uri_rel(self):
        source = '.'
        destination = _make_destination_dir_uri(
            source,
            1024,
            768
        )

        assert destination == './1024x768'

    def test_make_destination_dir_uri_abs(self):
        source = '/media/nobody/Wallpapers/Landscape'
        destination = _make_destination_dir_uri(
            source,
            1920,
            1080
        )

        assert destination == '{}/1920x1080'.format(source)

    def test_make_destination_dir_uri_spaces(self):
        source = '/media/no body/Great Wallpapers/Macro'
        destination = _make_destination_dir_uri(
            source,
            1920,
            1080
        )

        assert destination == '{}/1920x1080'.format(source)

