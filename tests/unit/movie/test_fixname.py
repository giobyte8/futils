import pytest
import os
import shutil
import tempfile
import uuid

from pathlib import Path

from fu.movie.fixname import (
    MissingRequiredDataError, MovieFile
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

@pytest.fixture
def tmp_file():
    """Creates a temporary file
    """
    tmp_file = tempfile.NamedTemporaryFile()

    yield tmp_file

    # Cleanup after usage
    tmp_file.close()


class TestMovieFile:
    def test_make_file_name(self, tmp_file):
        title = 'Interstellar'
        year  = 2018
        movie = MovieFile(
            title=title,
            year=year,
            src_file=tmp_file.name
        )

        name = '{} ({})'.format(title, year)
        assert name == movie.make_file_name()

    def test_make_file_name_no_valid(self):
        with pytest.raises(MissingRequiredDataError):
            movie = MovieFile(
                title='Interstellar',
                year=2018,
                src_file=None
            )
        
            movie.make_file_name()
    
    def test_make_file_name_res(self, tmp_file):
        title = 'Interstellar'
        year  = 2018
        res = '4k'
        
        movie = MovieFile(
            title=title,
            year=year,
            src_file=tmp_file.name
        )
        movie.resolution = res

        name = '{} ({}) - {}'.format(title, year, res)
        assert name == movie.make_file_name()

    def test_make_file_name_audio(self, tmp_file):
        title = 'Interstellar'
        year  = 2018
        audio = 'Eng'
        
        movie = MovieFile(
            title=title,
            year=year,
            src_file=tmp_file.name
        )
        movie.audio_lang = audio

        name = '{} ({}) - {}'.format(title, year, audio)
        assert name == movie.make_file_name()

    def test_make_file_name_comment(self, tmp_file):
        title = 'Interstellar'
        year  = 2018
        comment = '3D'
        
        movie = MovieFile(
            title=title,
            year=year,
            src_file=tmp_file.name
        )
        movie.extra_comment = comment

        name = '{} ({}) - {}'.format(title, year, comment)
        assert name == movie.make_file_name()

    def test_make_file_name_ext(self, tmp_file):
        title = 'Interstellar'
        year  = 2018
        ext = '.mkv'
        
        movie = MovieFile(
            title=title,
            year=year,
            src_file=tmp_file.name
        )
        movie.file_ext = ext

        name = '{} ({}).{}'.format(title, year, ext)
        assert name == movie.make_file_name()

    def test_make_file_name_res_audio(self, tmp_file):
        title = 'Interstellar'
        year  = 2018
        res = '1080p'
        audio = 'Dual'
        
        movie = MovieFile(
            title=title,
            year=year,
            src_file=tmp_file.name
        )
        movie.resolution = res
        movie.audio_lang = audio

        name = '{} ({}) - {} {}'.format(title, year, res, audio)
        assert name == movie.make_file_name()

    def test_make_file_name_res_audio_comment(self, tmp_file):
        title = 'Interstellar'
        year  = 2018
        res = '1080p'
        audio = 'Dual'
        comment = 'Extended'
        
        movie = MovieFile(
            title=title,
            year=year,
            src_file=tmp_file.name
        )
        movie.resolution = res
        movie.audio_lang = audio
        movie.extra_comment = comment

        name = '{} ({}) - {} {} {}'.format(
            title,
            year,
            res,
            audio,
            comment
        )
        assert name == movie.make_file_name()


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
        movie = MovieFile(
            title="The Fight Club",
            year=1999,
            src_file='/no/existent/path'
        )

        assert not movie.is_valid()

    def test_is_valid_no_title(self, tmp_dir):
        movie = MovieFile(
            title=None,
            year=1999,
            src_file=tmp_dir
        )

        assert not movie.is_valid()

    def test_is_valid_no_year(self, tmp_dir):
        movie = MovieFile(
            title="The Fight Club",
            year=None,
            src_file=tmp_dir
        )

        assert not movie.is_valid()

    def test_is_valid(self):
        with tempfile.NamedTemporaryFile() as mfile:
            movie = MovieFile(
                title="The Fight Club",
                year=1999,
                src_file=mfile.name
            )

            assert movie.is_valid()
