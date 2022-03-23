import pytest
import os
import shutil
import tempfile
import uuid

from pathlib import Path
from unittest import mock

from fu.common.errors import MissingRequiredDataError
from fu.tvshow.fixname import TVShowChapter, RenameOrder


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


class TestTVShowChapter:
    def test_make_file_name(self, tmp_file):
        show = 'Chernobyl'
        season = 1
        chapter = 6

        tvShowCh = TVShowChapter(
            src_file=tmp_file.name,
            show_title=show,
            season_number=season,
            chapter_number=chapter
        )

        chapter_name = f'{ show } - S0{ season }E0{ chapter }'
        assert chapter_name == tvShowCh.make_file_name()

    def test_make_file_name_invalid(self):
        with pytest.raises(MissingRequiredDataError):
            tvShowChapter = TVShowChapter(
                show_title='Random',
                season_number=5432,
                chapter_number=45,
                src_file=None
            )

            tvShowChapter.make_file_name()

    def test_make_file_name_year(self, tmp_file):
        show = 'Chernobyl'
        season = 12
        chapter = 15
        year = 2019

        tvShowCh = TVShowChapter(
            src_file=tmp_file.name,
            show_title=show,
            season_number=season,
            chapter_number=chapter,
            show_year=year
        )

        chapter_name = f'{ show } ({ year }) - S{ season }E{ chapter }'
        assert chapter_name == tvShowCh.make_file_name()

    def test_make_file_name_ch_title(self, tmp_file):
        show = 'Chernobyl'
        season = 1
        chapter = 6
        ch_title = 'Test title'

        tvShowCh = TVShowChapter(
            src_file=tmp_file.name,
            show_title=show,
            season_number=season,
            chapter_number=chapter,
            chapter_title=ch_title
        )

        chapter_name = f'{ show } - S0{ season }E0{ chapter } - { ch_title }'
        assert chapter_name == tvShowCh.make_file_name()

    def test_make_file_name_ch_year_title_res(self, tmp_file):
        show = 'Chernobyl'
        season = 11
        chapter = 16
        ch_title = 'Test title'
        year = 2019
        resolution = '4K HDR'

        tvShowCh = TVShowChapter(
            src_file=tmp_file.name,
            show_title=show,
            season_number=season,
            chapter_number=chapter,
            chapter_title=ch_title,
            show_year=year,
            resolution=resolution
        )

        chapter_name = (
            f'{ show } ({ year }) - S{ season }E{ chapter } - '
            f'{ ch_title } { resolution }'
        )
        assert chapter_name == tvShowCh.make_file_name()

    def test_is_valid_no_src_file(self):
        tvShowCh = TVShowChapter(
            src_file=None,
            show_title='Random',
            season_number=12,
            chapter_number=12
        )

        assert not tvShowCh.is_valid()

    def test_is_valid_invalid_src_file(self):
        tvShowCh = TVShowChapter(
            src_file='/invalid/path/file.mp4',
            show_title='Random',
            season_number=12,
            chapter_number=12
        )

        assert not tvShowCh.is_valid()

    def test_is_valid_no_show_title(self, tmp_file):
        tvShowCh = TVShowChapter(
            src_file=tmp_file.name,
            show_title=None,
            season_number=12,
            chapter_number=12
        )

        assert not tvShowCh.is_valid()

    def test_is_valid_no_season(self, tmp_file):
        tvShowCh = TVShowChapter(
            src_file=tmp_file.name,
            show_title='Random',
            season_number=None,
            chapter_number=12
        )

        assert not tvShowCh.is_valid()

    def test_is_valid_no_chapter_number(self, tmp_file):
        tvShowCh = TVShowChapter(
            src_file=tmp_file.name,
            show_title='Random',
            season_number=12,
            chapter_number=None
        )

        assert not tvShowCh.is_valid()

    def test_is_valid(self, tmp_file):
        tvShowCh = TVShowChapter(
            src_file=tmp_file.name,
            show_title='Random',
            season_number=12,
            chapter_number=12
        )

        assert tvShowCh.is_valid()

class TestRenameOrder:
    def test_has_errors_no_errors(self, tmp_dir, tmp_file):
        chapter = TVShowChapter(
            src_file=tmp_file.name,
            show_title='Test title',
            season_number=12,
            chapter_number=12
        )
        chapter2 = TVShowChapter(
            src_file=tmp_file.name,
            show_title='Test title 2',
            season_number=12,
            chapter_number=12
        )

        rename_order = RenameOrder(src_dir=tmp_dir)
        rename_order.chapters.extend([chapter, chapter2])

        assert not rename_order.has_errors()

    def test_has_errors(self, tmp_dir):
        rename_order = RenameOrder(src_dir=tmp_dir)
        assert rename_order.has_errors()

    def test_has_warnings_no_warnings(self, tmp_dir):
        rename_order = RenameOrder(src_dir=tmp_dir)
        assert not rename_order.has_warnings()

    def test_has_warnings(self, tmp_dir, tmp_file):
        chapter = TVShowChapter(
            src_file=tmp_file.name,
            show_title='Test title',
            season_number=12,
            chapter_number=12
        )

        rename_order = RenameOrder(src_dir=tmp_dir)
        rename_order.dst_existent_chapters.append(chapter)

        assert rename_order.has_warnings()

    @mock.patch('fu.tvshow.fixname.os.replace')
    def test_apply_non_approved(self, mock_replace, tmp_dir, tmp_file):
        chapter = TVShowChapter(
            src_file=tmp_file.name,
            show_title='Test title',
            season_number=12,
            chapter_number=12
        )

        rename_order = RenameOrder(src_dir=tmp_dir)
        rename_order.chapters.append(chapter)

        # Assert execute returns none
        assert rename_order.apply() is None

        # Assert no rename operation was executed
        mock_replace.assert_not_called()

    @mock.patch('fu.tvshow.fixname.os.replace')
    def test_apply_not_overwrite(self, mock_replace, tmp_dir, tmp_file):
        chapter = TVShowChapter(
            src_file=tmp_file.name,
            show_title='Test title',
            season_number=3,
            chapter_number=12
        )
        chapter2 = TVShowChapter(
            src_file=tmp_file.name,
            show_title='Test title 2',
            season_number=3,
            chapter_number=13
        )

        rename_order = RenameOrder(src_dir=tmp_dir)
        rename_order.chapters.append(chapter)
        rename_order.dst_existent_chapters.append(chapter2)
        rename_order.execute = True

        rename_order.apply()

        # Assert only safe chapter was renamed
        mock_replace.assert_called_once_with(
            tmp_file.name,
            chapter.make_target_file_path()
        )

    @mock.patch('fu.tvshow.fixname.os.replace')
    def test_apply_overwrite(self, mock_replace, tmp_dir, tmp_file):
        chapter = TVShowChapter(
            src_file=tmp_file.name,
            show_title='Test title',
            season_number=1,
            chapter_number=12
        )
        chapter2 = TVShowChapter(
            src_file=tmp_file.name,
            show_title='Test title 2',
            season_number=1,
            chapter_number=13
        )

        rename_order = RenameOrder(src_dir=tmp_dir)
        rename_order.chapters.append(chapter)
        rename_order.dst_existent_chapters.append(chapter2)
        rename_order.overwrite = True
        rename_order.execute = True

        rename_order.apply()

        # Expected calls
        calls = [
            mock.call(
                tmp_file.name,
                chapter.make_target_file_path()
            ),
            mock.call(
                tmp_file.name,
                chapter2.make_target_file_path()
            )
        ]

        # Assert both files were renamed
        mock_replace.assert_has_calls(calls, any_order=False)

    @mock.patch('fu.utils.path.get_file_name')
    @mock.patch('fu.tvshow.fixname.console.print')
    def test_scan_src_dir_empty_dir(
        self,
        mock_cprint,
        mock_get_file_name,
        tmp_dir
    ):
        order = RenameOrder(src_dir=tmp_dir)
        order.scan_src_dir()

        mock_cprint.assert_called_once_with(
            f'Looking for TV Show files in: { tmp_dir }'
        )
        mock_get_file_name.assert_not_called()

    @mock.patch('fu.tvshow.fixname.RenameOrder._ask_chapter_details')
    @mock.patch('fu.tvshow.fixname.Confirm.ask')
    @mock.patch('fu.tvshow.fixname.console.print')
    def test_scan_src_single_chapter_unapproved(
        self,
        mock_cprint,
        mock_ask,
        mock_ask_chapter_details,
        tmp_dir
    ):
        # Create a fake chapter file
        filepath = os.path.join(tmp_dir, 'Mandalorian1.mkv')
        open(filepath, 'a').close()

        # Prepare mock return value
        mock_ask.return_value = False

        # Run scan on src dir
        order = RenameOrder(src_dir=tmp_dir)
        order.scan_src_dir()

        assert not order.chapters
        assert len(order.skipped_files) == 1
        assert mock_cprint.call_count == 2
        mock_ask.assert_called_once_with('Rename file?')
        mock_ask_chapter_details.assert_not_called()

    @mock.patch('fu.tvshow.fixname.RenameOrder._ask_chapter_details')
    @mock.patch('fu.tvshow.fixname.Confirm.ask')
    @mock.patch('fu.tvshow.fixname.console.print')
    def test_scan_src_single_chapter_approved(
        self,
        mock_cprint,
        mock_ask,
        mock_ask_chapter_details,
        tmp_dir
    ):
        # Create a fake chapter file
        filepath = os.path.join(tmp_dir, 'Mandalorian1.mkv')
        open(filepath, 'a').close()

        #
        # Prepare mocks return values

        chapter = TVShowChapter(
            src_file=filepath,
            show_title='Test title',
            season_number=1,
            chapter_number=1
        )

        mock_ask_chapter_details.return_value = chapter
        mock_ask.return_value = True

        # Run scan on src dir
        order = RenameOrder(src_dir=tmp_dir)
        order.scan_src_dir()

        assert not order.skipped_files
        assert not order.dst_existent_chapters
        assert len(order.chapters) == 1
        assert order.chapters[0] == chapter

        assert mock_cprint.call_count == 2
        mock_ask.assert_called_once_with('Rename file?')
        mock_ask_chapter_details.assert_called_once()

    @mock.patch('fu.tvshow.fixname.RenameOrder._ask_chapter_details')
    @mock.patch('fu.tvshow.fixname.Confirm.ask')
    @mock.patch('fu.tvshow.fixname.console.print')
    def test_scan_src_existent_chapter(
        self,
        mock_cprint,
        mock_ask,
        mock_ask_chapter_details,
        tmp_dir
    ):
        # Create a fake chapter file
        filepath = os.path.join(tmp_dir, 'The Mandalorian - S01E01.mkv')
        open(filepath, 'a').close()

        #
        # Prepare mocks return values

        chapter = TVShowChapter(
            src_file=filepath,
            show_title='The Mandalorian',
            season_number=1,
            chapter_number=1
        )

        mock_ask_chapter_details.return_value = chapter
        mock_ask.return_value = True

        # Run scan on src dir
        order = RenameOrder(src_dir=tmp_dir)
        order.scan_src_dir()

        assert not order.skipped_files
        assert not order.chapters
        assert len(order.dst_existent_chapters) == 1
        assert order.dst_existent_chapters[0] == chapter

        assert mock_cprint.call_count == 2
        mock_ask.assert_called_once_with('Rename file?')
        mock_ask_chapter_details.assert_called_once()
