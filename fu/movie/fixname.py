import os

from dataclasses import (
    dataclass,
    field
)
from rich.prompt import (
    Confirm,
    IntPrompt,
    Prompt
)
from rich.table import Table

from fu.utils.console import console
from fu.utils.path import (
    get_file_name,
    get_file_ext,
    is_dir,
    path_files
)


_movie_formats = ['.mkv', '.mp4', '.avi', '.wmv']

@dataclass
class MovieFile:
    src_file: str

    title: str
    year: int
    resolution: str = None
    audio_lang: str = None
    extra_comment: str = None
    
    file_ext: str = None

    def make_file_name(self) -> str:
        """Creates file name for this movie using format:  \
            <Title> (<Year>) - [Resolution] [Audio language].<ext>

        Returns:
            str: File name for this movie
        """
        if not self.is_valid():
            raise MissingRequiredDataError()

        name = '{} ({})'.format(self.title, self.year)

        if self.resolution:
            name += ' - {}'.format(self.resolution)

        if self.audio_lang:
            name += '{} {}'.format(
                ('' if self.resolution else ' -'),
                self.audio_lang
            )

        if self.extra_comment:
            name += '{} {}'.format(
                ('' if self.resolution or self.audio_lang else ' -'),
                self.extra_comment
            )

        # Verify extension existence
        if self.file_ext:
            name += '.{}'.format(self.file_ext)

        return name

    def make_target_file_path(self) -> str:
        """Creates destination file path for this movie

        Returns:
            str: Destination file path
        """
        if not self.is_valid():
            raise MissingRequiredDataError()

        file_name = self.make_file_name()
        dir_path = os.path.dirname(self.src_file)

        return os.path.join(dir_path, file_name)

    def is_valid(self) -> bool:
        return self.src_file \
                and os.path.isfile(self.src_file) \
                and self.title \
                and self.year


class RenameOrder:
    src_dir: str

    movies: list = []
    dst_existent_movies: list = []
    skipped_files: list = []

    errors: list = []
    warnings: list = []

    execute: bool = False
    overwrite: bool = False

    def __init__(self, src_dir: str) -> None:
        """Initalizes order object

        Args:
            src_dir (str): Path to directory containing movies to \
                rename
        """
        self.src_dir = src_dir

    def scan_src_dir(self) -> None:
        """Scans provided directory for movie files and ask user for  \
            movie info.

        Args:
            interactive (bool, optional): [description]. Defaults to False.
        """
        # TODO Migrate functionality from outer method
        # TODO Migrate all remaining outer methods into class
        pass

    def has_errors(self) -> bool:
        if not self.movies and not self.dst_existent_movies:
            self.warnings.append('No files to rename')
        
        return len(self.errors) > 0

    def has_warnings(self) -> bool:
        if self.dst_existent_movies:
            self.warnings.append('Some movie files will be overwriten')
        
        return len(self.warnings) > 0


class MissingRequiredDataError(Exception):
    """Error indicates there are not enough info \
        for renaming movie file

    Args:
        Exception (Exception): Python base exception
    """
    pass


def rename_movies(src_dir: str) -> None:
    """Will rename all movie files in provided directory asking user \
        for title, year, res, audio lang and extra comment

    Args:
        src_dir (str): Path to directory containing files to rename
    """
    if not is_dir(src_dir):
        console.print(
            'Provided dir does not exists. {}'.format(src_dir),
            style='error'
        )

    rename_order = _prepare_rename_order(src_dir)
    _evaluate_rename_order(rename_order)

    if rename_order.execute:
        pass
        # Apply rename operations


def _evaluate_rename_order(order: RenameOrder) -> None:
    """Shows rename order to user (And possible warnings/errors) \
        and ask for confirmation to proceed and execute rename   \
        operations.

        If order has errors, it will be printed and operation    \
        will be cancelled.

    Args:
        order (RenameOrder): Order to display to user
    """
    if order.has_errors():
        for error in order.errors:
            console.print(error, style='error')
        order.execute = False
        return order

    _print_preview(order)

    if order.has_warnings():
        for warn in order.warnings:
            console.print(warn, style='warning')

        console.print('0. Abort operation')
        console.print('1. Rename only safe files')
        console.print('2. Rename all and overwrite existent files')
        user_choice = Prompt.ask(
            'Enter your choice: ',
            choices=['0', '1', '2'],
            default='1'
        )

        if user_choice == 0:
            order.execute = False
        elif user_choice == 1:
            order.overwrite = False
            order.execute = True
        elif user_choice == 2:
            order.overwrite = True
            order.execute = True
    
    # Confirm operation execution
    else:
        order.execute = Confirm.ask('Confirm rename operation?')


def _print_preview(order: RenameOrder) -> None:
    """Prints a table with all files to be renamed

    Args:
        order (RenameOrder): Rename operation
    """
    table = Table()
    table.add_column('Current name', justify='center')
    table.add_column('New name', justify='center')
    table.add_column('Status', justify='center')

    for movie in order.movies:
        table.add_row(
            get_file_name(movie.src_file),
            movie.make_file_name(),
            'Ok'
        )

    for movie in order.dst_existent_movies:
        table.add_row(
            '[yellow]{}'.format(get_file_name(movie.src_file)),
            '[yellow]{}'.format(movie.make_file_name()),
            '[yellow]Existent'
        )
    
    console.print()
    console.print(table)


def _prepare_rename_order(src_dir: str) -> RenameOrder:
    """Scans provided directory for movie files and ask user for  \
        movie info. Creates a rename order. Rename is not applied.

    Args:
        src_dir (str): Path to directory containing movies to rename

    Returns:
        RenameOrder: Rename operation order
    """
    console.print('Looking for movie files at: {}'.format(src_dir))
    rename_order = RenameOrder()

    for movie_file in path_files(src_dir, extensions=_movie_formats):
        src_file_name = get_file_name(movie_file)

        # Confirm rename request
        console.print('\n File found: {}'.format(src_file_name))
        rename_approved = Confirm.ask('Rename file?')

        if rename_approved:
            movie = _ask_movie_details(src_file_name)
            movie.file_ext = get_file_ext(src_file_name)
            movie.src_file = movie_file

            # Destination file already exists
            if os.path.isfile(movie.make_target_file_path()):
                rename_order.dst_existent_movies.append(movie)

            # Movie can be renamed without issues
            else:
                rename_order.movies.append(movie)
        else:
            rename_order.skipped_files.append(src_file_name)
    
    return rename_order
    

def _ask_movie_details(filename: str) -> MovieFile:
    movie = MovieFile()

    movie.title = Prompt.ask('Movie title: ')
    movie.year = IntPrompt.ask('Year: ')
    movie.resolution = Prompt.ask(
        '[Resolution (eg: 720p|1080p|4k)]: ',
        default=''
    )
    movie.lang = Prompt.ask(
        '[Language (eg: Eng|Lat|Dual)]: ',
        default=''
    )
    movie.extra = Prompt.ask(
        '[Extra data (eg: HDR|Extended|3D)]: ',
        default=''
    )

    return movie



