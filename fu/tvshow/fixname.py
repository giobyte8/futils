import os

from dataclasses import dataclass
from rich.prompt import (
    Confirm,
    IntPrompt,
    Prompt
)
from rich.table import Table
from typing import List

from fu.common.errors import MissingRequiredDataError
from fu.utils.console import console
from fu.utils.path import (
    count_path_files,
    get_file_name,
    get_file_ext,
    is_dir,
    path_files
)

_tvshow_formats = ['.mkv', '.mp4', '.avi', '.wmv']

@dataclass
class TVShowChapter:
    src_file: str

    show_title: str
    season_number: str
    chapter_number: str
    chapter_title: str = None
    show_year: int = None
    resolution: str = None
    audio_lang: str = None
    comment: str = None

    file_ext: str = None

    def has_extra_info(self) -> bool:
        return self.chapter_title or \
            self.resolution or \
            self.audio_lang or \
            self.comment

    def is_valid(self) -> bool:
        return self.src_file and \
            os.path.isfile(self.src_file) and \
            self.show_title and \
            self.season_number and \
            self.chapter_number

    def make_file_name(self) -> str:
        """ Creates file name for this chapter using format:             \
            <Show title> (Show year) - S<Season number>E<Chapter number>\
            [ - <chapter title> <Resolution> <Audio lang> <Extra comment>].ext

        Returns:
            str: File name for this chapter
        """
        if not self.is_valid():
            raise MissingRequiredDataError()

        name = f'{ self.show_title } '

        if self.show_year:
            name += f'({ self.show_year }) '

        name += f'- S{ self.season_number }E{ self.chapter_number }'

        if self.has_extra_info():
            name += ' -'

            if self.chapter_title:
                name += f' { self.chapter_title }'

            if self.resolution:
                name += f' { self.resolution }'

            if self.audio_lang:
                name += f' { self.audio_lang } '

            if self.comment:
                name += f' { self.comment }'

        # Verify extension existence just in case
        if self.file_ext:
            name += self.file_ext

        return name

    def make_target_file_path(self) -> str:
        """Creates destination file path for this chapter

        Returns:
            str: Destination file path
        """
        if not self.is_valid():
            raise MissingRequiredDataError()

        file_name = self.make_file_name()
        dir_path = os.path.dirname(self.src_file)
        return os.path.join(dir_path, file_name)


class RenameOrder:
    """Represents an operation to rename multiple chapter files
    """

    def __init__(self, src_dir: str) -> None:
        """Initializes rename order

        Args:
            src_dir (str): Path to directory containing chapter \
                files to rename
        """
        self.src_dir = src_dir

        #: Chapters that can be renamed without issues
        self.chapters: List[TVShowChapter] = []

        #: chapters whose destination file already exists
        self.dst_existent_chapters: List[TVShowChapter] = []

        #: File names of skipped chapter files
        self.skipped_files: List[str] = []

        self.errors: List[str] = []
        self.warnings: List[str] = []

        #: Indicates if rename execution is approved by user
        self.execute = False

        #: Indicates if overwrite of destination files is approved
        self.overwrite = False

    def apply(self) -> None:
        """Applies rename operations based on user preferences
        """
        if not self.execute:
            return None

        for chapter in self.chapters:
            os.replace(
                chapter.src_file,
                chapter.make_target_file_path()
            )

        if self.dst_existent_chapters and self.overwrite:
            for chapter in self.dst_existent_chapters:
                os.replace(
                    chapter.src_file,
                    chapter.make_target_file_path()
                )

        console.print()
        console.print('Rename operation is complete')

    def evaluate_rename_order(self) -> None:
        """Show rename order to user (including warnings/errors)   \
            and ask for confirmation to proceed and execute rename \
            operations.

            If order has errors, it will be printed and execution  \
            will be set to false
        """
        if self.has_errors():
            for error in self.errors:
                console.print(error, style='error')
            self.execute = False
            return None

        self._print_preview()

        if self.has_warnings():
            for warn in self.warnings:
                console.print(warn, style='warning')

            console.print()
            console.print('0. Abort operation')
            console.print('1. Rename only safe files')
            console.print('2. Rename all and overwrite existent files')
            user_choice = Prompt.ask(
                'Enter your choice: ',
                choices=['0', '1', '2'],
                default='1'
            )

            if user_choice == 0:
                self.execute = False
            elif user_choice == 1:
                self.overwrite = False
                self.execute = True
            elif user_choice == 2:
                self.overwrite = True
                self.execute = True

        # Confirm operation execution
        else:
            self.execute = Confirm.ask('Confirm rename operation?')

    def has_errors(self) -> bool:
        if not self.chapters and not self.dst_existent_chapters:
            self.errors.append('No files to rename')

        return len(self.errors) > 0

    def has_warnings(self) -> bool:
        if self.dst_existent_chapters:
            self.warnings.append('Some tv show files will be overwriten')

        return len(self.warnings) > 0

    def scan_src_dir(self) -> None:
        """Scans provided directory for TV Show chapter files and ask user \
            for TV Show and chapters info. \

            Scanned files will be stored into chapters, dst_existent_chapters \
            and skipped_files lists.
        """
        console.print(f'Looking for TV Show files in: { self.src_dir }')

        global_tvshow_title = None
        global_season_number = None
        global_add_tvshow_year = False
        global_tvshow_year = None
        files_count = count_path_files(
            self.src_dir,
            extensions=_tvshow_formats
        )

        if files_count > 1:
            console.print(f'{ files_count } files were found in given path')

            same_show_files = Confirm.ask(
                'Does all files belongs to same TV Show?'
            )
            if same_show_files:
                global_tvshow_title = Prompt.ask('TV Show title: ')

            same_season_files = Confirm.ask(
                'Does all files belongs to same Season?'
            )
            if same_season_files:
                global_season_number = Prompt.ask(
                    'Season number (Two digits format)?'
                )

            # Ask for year if all files belongs to same tv show
            if same_show_files:
                global_add_tvshow_year = Confirm.ask(
                    'You want to add same TV Show release year to all found files?'
                )

                if global_add_tvshow_year:
                    global_tvshow_year = IntPrompt.ask(
                        'TV Show release year?',
                        default=0
                    )

        for ch_file in path_files(self.src_dir, extensions=_tvshow_formats):
            src_file_name = get_file_name(ch_file)

            # Confirm rename request
            console.print('\n File found: {}'.format(src_file_name))
            rename_approved = Confirm.ask('Rename file?')

            if rename_approved:
                chapter = self._ask_chapter_details(
                    ch_file,
                    global_tvshow_title,
                    global_season_number,
                    global_add_tvshow_year,
                    global_tvshow_year
                )
                chapter.file_ext = get_file_ext(ch_file)

                # If destination file already exists
                if os.path.isfile(chapter.make_target_file_path()):
                    self.dst_existent_chapters.append(chapter)

                # Chapter can be renamed with no issues
                else:
                    self.chapters.append(chapter)

            # Skipped file
            else:
                self.skipped_files.append(src_file_name)

    def _ask_chapter_details(
        self,
        src_file: str,
        global_show_title: str,
        global_season_number: str,
        global_add_tvshow_year: bool,
        global_tvshow_year: int
    ) -> TVShowChapter:
        title = global_show_title
        season_num = global_season_number

        # Prepare/ask required info
        if not global_show_title:
            title = Prompt.ask('TV Show title: ')
        if not global_season_number:
            season_num = Prompt.ask('Season number (Two digits): ')
        chapter_num = Prompt.ask('Episode number (Two digits): ')

        # Initial chapter instance
        chapter = TVShowChapter(
            src_file=src_file,
            show_title=title,
            season_number=season_num,
            chapter_number=chapter_num
        )

        # Setup/Ask for optional/extra info
        if global_add_tvshow_year:
            chapter.show_year = global_tvshow_year
        else:
            chapter.show_year = IntPrompt.ask(
                'Year (Hit enter for leave empty): ',
                default=0
            )
        chapter.chapter_title = Prompt.ask(
            'Episode title (Hit enter for leave empty): ',
            default=''
        )
        chapter.resolution = Prompt.ask(
            'Resolution (eg: 720p|1080p|4k) [Hit enter for leave empty]: ',
            default=''
        )
        chapter.audio_lang = Prompt.ask(
            'Language (eg: Eng|Lat|Dual) [Hit enter for leave empty]: ',
            default=''
        )
        chapter.comment = Prompt.ask(
            'Extra data (eg: HDR|Extended|3D) [Hit enter for leave empty]: ',
            default=''
        )

        return chapter

    def _print_preview(self) -> None:
        """Prints a table with details about this rename order
        """
        table = Table()
        table.add_column('Current file name', justify='right')
        table.add_column('New file name', justify='left')
        table.add_column('Status', justify='center')

        for chapter in self.chapters:
            table.add_row(
                get_file_name(chapter.src_file),
                chapter.make_file_name(),
                'Ok'
            )

        for chapter in self.dst_existent_chapters:
            table.add_row(
                '[yellow]{}'.format(get_file_name(chapter.src_file)),
                '[yellow]{}'.format(chapter.make_file_name()),
                '[yellow]Existent'
            )

        console.print()
        console.print(table)

def rename_tvshow_files(src_dir: str) -> None:
    """Will rename all tv show files found in provided directory asking user \
        for Show title, season number, episode number and other episode details

    Args:
        src_dir (str): Path to directory containing files to rename
    """
    if not is_dir(src_dir):
        console.print(
            'Provided dir does not exists. {}'.format(src_dir),
            style='error'
        )

    rename_order = RenameOrder(src_dir)
    rename_order.scan_src_dir()
    rename_order.evaluate_rename_order()

    if rename_order.execute:
        rename_order.apply()
