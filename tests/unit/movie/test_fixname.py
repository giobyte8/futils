import pytest
import os
import shutil
import tempfile
import uuid

from pathlib import Path

from fu.movie.fixname import (
    MovieFile
)


@pytest.fixture
def tmp_dir():
    """Creates a temporary unique directory
    """
    tmp_dir = os.path.join(tempfile.gettempdir(), str(uuid.uuid4()))
    Path(tmp_dir).mkdir(parents=True, exist_ok=True)

    yield tmp_dir

    # Cleanup after usage
    shutil.rmtree(tmp_dir)


class TestMovieFile:
    def test_file_name(self):
        pass

    def test_file_name_no_valid(self):
        pass

    def test_is_valid_no_path(self):
        movie = MovieFile(
            title="The Fight Club",
            year=1999,
            src_file=None
        )

        assert not movie.is_valid()

    def test_is_valid_dir_path(self, tmp_dir):
        movie = MovieFile(
            title="The Fight Club",
            year=1999,
            src_file=tmp_dir
        )

        assert not movie.is_valid()

    def test_is_valid_non_existent_path(self):
        pass

    def test_is_valid_no_title(self):
        pass

    def test_is_valid_no_year(self):
        pass

    def test_is_valid(self):
        pass
