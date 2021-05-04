import pytest
import os
import shutil
import tempfile
import uuid

from pathlib import Path
from unittest import mock

from fu.movie.fixname import (
    MissingRequiredDataError, MovieFile, RenameOrder
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

        name = '{} ({}){}'.format(title, year, ext)
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

class TestRenameOrder:
    def test_has_errors_no_errors(self, tmp_dir, tmp_file):
        movie = MovieFile(tmp_file.name, 'Gladiator', 1999)
        movie2 = MovieFile(tmp_file.name, 'Interstellar', 2018)

        rename_order = RenameOrder(src_dir=tmp_dir)
        rename_order.movies.append(movie)
        rename_order.dst_existent_movies.append(movie2)

        assert not rename_order.has_errors()

    def test_has_errors(self, tmp_dir):
        rename_order = RenameOrder(src_dir=tmp_dir)
        assert rename_order.has_errors()

    def test_has_warnings_no_warnings(self, tmp_dir):
        rename_order = RenameOrder(src_dir=tmp_dir)
        assert not rename_order.has_warnings()
    
    def test_has_warnings(self, tmp_dir, tmp_file):
        movie = MovieFile(tmp_file.name, 'Gladiator', 1999)
        
        rename_order = RenameOrder(src_dir=tmp_dir)
        rename_order.dst_existent_movies.append(movie)

        assert rename_order.has_warnings()

    @mock.patch('fu.movie.fixname.os.replace')
    def test_apply_non_approved(self, mock_replace, tmp_dir, tmp_file):
        movie = MovieFile(tmp_file.name, 'Gladiator', 1999)

        rename_order = RenameOrder(src_dir=tmp_dir)
        rename_order.movies.append(movie)

        # Assert execute returns none
        assert rename_order.apply() is None

        # Assert no rename operation was executed
        mock_replace.assert_not_called()
    
    @mock.patch('fu.movie.fixname.os.replace')
    def test_apply_not_overwrite(self, mock_replace, tmp_dir, tmp_file):
        gladiator = MovieFile(tmp_file.name, 'Gladiator', 1999)
        interstellar = MovieFile(tmp_file.name, 'Interstellar', 2018)

        rename_order = RenameOrder(src_dir=tmp_dir)
        rename_order.movies.append(gladiator)
        rename_order.dst_existent_movies.append(interstellar)
        rename_order.execute = True

        rename_order.apply()
    
        # Assert only interstellar was renamed
        mock_replace.assert_called_once_with(
            tmp_file.name,
            gladiator.make_target_file_path()
        )
    
    @mock.patch('fu.movie.fixname.os.replace')
    def test_apply_overwrite(self, mock_replace, tmp_dir, tmp_file):
        gladiator = MovieFile(tmp_file.name, 'Gladiator', 1999)
        interstellar = MovieFile(tmp_file.name, 'Interstellar', 2018)

        rename_order = RenameOrder(src_dir=tmp_dir)
        rename_order.movies.append(gladiator)
        rename_order.dst_existent_movies.append(interstellar)
        rename_order.overwrite = True
        rename_order.execute = True

        rename_order.apply()
        print(rename_order.movies)
        print(rename_order.dst_existent_movies)

        # Expected calls
        calls = [
            mock.call(
                tmp_file.name,
                gladiator.make_target_file_path()
            ),
            mock.call(
                tmp_file.name,
                interstellar.make_target_file_path()
            )
        ]
    
        # Assert both movies were renamed
        mock_replace.assert_has_calls(calls, any_order=False)

    @mock.patch('fu.utils.path.get_file_name')
    @mock.patch('fu.movie.fixname.console.print')
    def test_scan_src_dir_empty_dir(
        self,
        mock_cprint,
        mock_get_file_name,
        tmp_dir
    ):
        order = RenameOrder(src_dir=tmp_dir)
        order.scan_src_dir()

        mock_cprint.assert_called_once_with(
            'Looking for movie files at: {}'.format(tmp_dir)
        )
        mock_get_file_name.assert_not_called()

    @mock.patch('fu.movie.fixname.RenameOrder._ask_movie_details')
    @mock.patch('fu.movie.fixname.Confirm.ask')
    @mock.patch('fu.movie.fixname.console.print')
    def test_scan_src_single_movie_unapproved(
        self,
        mock_cprint,
        mock_ask,
        mock_ask_movie_details,
        tmp_dir
    ):
        # Create a fake movie file
        filepath = os.path.join(tmp_dir, 'Gladiator.mkv')
        open(filepath, 'a').close()

        # Prepare mock return value
        mock_ask.return_value = False

        # Run scan on src dir
        order = RenameOrder(src_dir=tmp_dir)
        order.scan_src_dir()

        assert not order.movies
        assert len(order.skipped_files) == 1
        assert mock_cprint.call_count == 2
        mock_ask.assert_called_once_with('Rename file?')
        mock_ask_movie_details.assert_not_called()

    @mock.patch('fu.movie.fixname.RenameOrder._ask_movie_details')
    @mock.patch('fu.movie.fixname.Confirm.ask')
    @mock.patch('fu.movie.fixname.console.print')
    def test_scan_src_single_movie_approved(
        self,
        mock_cprint,
        mock_ask,
        mock_ask_movie_details,
        tmp_dir
    ):
        # Create a fake movie file
        filepath = os.path.join(tmp_dir, 'Gladiator.mkv')
        open(filepath, 'a').close()
        
        #
        # Prepare mocks return values

        gladiator = MovieFile(
            title='Gladiator',
            year=2000,
            src_file=filepath
        )

        mock_ask_movie_details.return_value = gladiator
        mock_ask.return_value = True

        # Run scan on src dir
        order = RenameOrder(src_dir=tmp_dir)
        order.scan_src_dir()

        assert not order.skipped_files
        assert not order.dst_existent_movies
        assert len(order.movies) == 1
        assert order.movies[0] == gladiator

        assert mock_cprint.call_count == 2
        mock_ask.assert_called_once_with('Rename file?')
        mock_ask_movie_details.assert_called_once_with('Gladiator.mkv')

    @mock.patch('fu.movie.fixname.RenameOrder._ask_movie_details')
    @mock.patch('fu.movie.fixname.Confirm.ask')
    @mock.patch('fu.movie.fixname.console.print')
    def test_scan_src_existent_movie(
        self,
        mock_cprint,
        mock_ask,
        mock_ask_movie_details,
        tmp_dir
    ):
        # Create a fake movie file
        filepath = os.path.join(tmp_dir, 'Gladiator (2000).mkv')
        open(filepath, 'a').close()
        
        #
        # Prepare mocks return values

        gladiator = MovieFile(
            title='Gladiator',
            year=2000,
            src_file=filepath
        )

        mock_ask_movie_details.return_value = gladiator
        mock_ask.return_value = True

        # Run scan on src dir
        order = RenameOrder(src_dir=tmp_dir)
        order.scan_src_dir()

        assert not order.skipped_files
        assert not order.movies
        assert len(order.dst_existent_movies) == 1
        assert order.dst_existent_movies[0] == gladiator

        assert mock_cprint.call_count == 2
        mock_ask.assert_called_once_with('Rename file?')
        mock_ask_movie_details.assert_called_once_with('Gladiator (2000).mkv')