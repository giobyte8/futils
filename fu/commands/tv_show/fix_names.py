import os
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from rich.prompt import (
    Confirm,
    IntPrompt,
    Prompt
)
from rich.table import Table
from typing import List

from fu.common.errors import InvalidPathError, MissingRequiredDataError
from fu.utils.console import console
from fu.utils.path import (
    get_file_name,
    get_file_ext,
    is_dir,
    path_files
)
from ..base_command import Command


_TV_SHOW_FILE_EXTENSIONS = ['.mkv', '.mp4', '.avi', '.wmv']


@dataclass
class Episode:
    src_file: str

    show_title: str
    season_number: str
    chapter_number: str

    show_year: str = None
    chapter_title: str = None
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
        """ Creates file name for this chapter using format:                    \
            <Show title> (Show year) - S<Season number>E<Chapter number>       \
            [ - <chapter title> <Resolution> <Audio lang> <Extra comment>].ext

        Returns:
            str: File name for this chapter
        """
        if not self.is_valid():
            raise MissingRequiredDataError()

        name = f'{ self.show_title } '

        if self.show_year:
            name += f'({ self.show_year }) '

        name += self.__prefix_sequential('- S', self.season_number)
        name += self.__prefix_sequential('E', self.chapter_number)

        if self.has_extra_info():
            name += ' -'

            if self.chapter_title:
                name += f' { self.chapter_title }'

            if self.resolution:
                name += f' { self.resolution }'

            if self.audio_lang:
                name += f' { self.audio_lang }'

            if self.comment:
                name += f' { self.comment }'

        # Verify extension existence just in case
        if self.file_ext:
            name += self.file_ext

        return name

    def __prefix_sequential(self, prefix: str, value: str) -> str:
        try:
            num = int(value)
            if num < 10:
                return f'{ prefix }0{ num }'
            else:
                return f'{ prefix }{ num }'
        except:
            return f'{ prefix }{ value }'

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


class CmdExecMode(Enum):
    ABORT = 0
    OVERRIDE_FORBIDDEN = 1
    APPLY_ALL = 2


class SharedAttrValueMode(Enum):
    """A TV Show is usually composed of several episodes/files,
    this enum is used to represent user preference regarding if
    several files should share same value for specific attributes
    or not.

    e.g. All files in a directory might belong to same season
    """
    SHARED = 1
    EACH_FILE_DIFF = 2
    LEAVE_EMPTY = 3


@dataclass
class EpisodeAttribute:

    """Attribute name/desc as will be displayed to end \
    user (e.g. year, season number, resolution)
    """
    desc: str

    """Indicates whether an empty value is allowed or not
    """
    empty_allowed: bool = True

    shared_value_mode: SharedAttrValueMode = None
    shared_value = None


class AttrValueResolver(ABC):

    @abstractmethod
    def resolve(self, attr: EpisodeAttribute) -> str:
        pass


class InteractiveAttrValueResolver(AttrValueResolver):

    def resolve(self, attr: EpisodeAttribute) -> str:
        if not attr.shared_value_mode:
            attr.shared_value_mode = self.__shared_value_mode(attr)

        if attr.shared_value_mode == SharedAttrValueMode.SHARED:
            if not attr.shared_value:
                attr.shared_value = self.__value(attr)

            return attr.shared_value

        if attr.shared_value_mode == SharedAttrValueMode.EACH_FILE_DIFF:
            return self.__value(attr)

        if attr.shared_value_mode == SharedAttrValueMode.LEAVE_EMPTY:
            return None

    def __shared_value_mode(
        self,
        attr: EpisodeAttribute
    ) -> SharedAttrValueMode:
        """Determines how to resolve value for an attribute that might
        be shared across all found files

        Args:
            attr (EpisodeAttribute): Target episode attribute

        Returns:
            SharedAttrValueMode: Shared value mode
        """
        choices = [
            str(SharedAttrValueMode.SHARED.value),
            str(SharedAttrValueMode.EACH_FILE_DIFF.value)
        ]

        if attr.empty_allowed:
            choices.append(str(SharedAttrValueMode.LEAVE_EMPTY.value))

        console.print(f'\nHow you want to handle { attr.desc }?')
        console.print(' 1. Same value for all files')
        console.print(' 2. Different value for each file')
        if attr.empty_allowed:
            console.print(' 3. Leave empty for all files')

        user_option = IntPrompt.ask(
            'Enter your choice',
            choices=choices,
            default=1
        )

        return SharedAttrValueMode(user_option)

    def __value(self, attr: EpisodeAttribute) -> str:
        return Prompt.ask(attr.desc.capitalize())


class FixNamesCmd(Command):
    """Command to rename one or multiple files in a given directory"""

    #: Episodes that can be renamed without issues
    episodes: List[Episode] = []

    #: episodes whose destination file already exists
    dst_existent_episodes: List[Episode] = []

    #: File names of skipped episodes
    skipped_files: List[str] = []

    exec_mode: CmdExecMode


    def __init__(self, src_dir: str):
        """Initializes rename command

        Args:
            src_dir (str): Path to directory containing chapter \
                files to rename
        """
        super().__init__('fix-names')
        self.src_dir = src_dir

    def execute(self):
        if not self.episodes and not self.dst_existent_episodes:
            self.logger.info('No files to rename')
            return None

        # TODO Validate if two or more episodes will have same target name

        if self.exec_mode == CmdExecMode.ABORT:
            return None

        elif self.exec_mode in [
            CmdExecMode.OVERRIDE_FORBIDDEN,
            CmdExecMode.APPLY_ALL
        ]:
            # Rename safe episodes
            for episode in self.episodes:
                os.replace(
                    episode.src_file,
                    episode.make_target_file_path()
                )

            # Rename files in conflict
            if self.exec_mode == CmdExecMode.APPLY_ALL:
                for episode in self.dst_existent_episodes:
                    os.replace(
                        episode.src_file,
                        episode.make_target_file_path()
                    )

            self.logger.info('Rename operations are complete')


    def _preview(self) -> None:
        """Prints a nice preview of each found file and its target name"""
        table = Table()
        table.add_column('Current file name', justify='right')
        table.add_column('New file name', justify='left')
        table.add_column('Status', justify='center')

        for episode in self.episodes:
            table.add_row(
                get_file_name(episode.src_file),
                episode.make_file_name(),
                'Ok'
            )

        for episode in self.dst_existent_episodes:
            table.add_row(
                '[yellow]{}'.format(get_file_name(episode.src_file)),
                '[yellow]{}'.format(episode.make_file_name()),
                '[yellow]Existent'
            )

        console.print()
        console.print(table)


class CmdOptionResolver(ABC):

    @abstractmethod
    def skip_file(self, file_name: str) -> bool:
        """Determines if a given found file should be skipeed or renamed

        Args:
            file_name (str): Path of found file

        Returns:
            bool: If True, then the file should be skipped from being renamed
        """

    @abstractmethod
    def exec_mode(self, cmd: FixNamesCmd) -> CmdExecMode:
        """Based on results of dir scan, determines how to proceed with \
            renaming. (e.g. Abort, Override allowed, Proceed without renaming)

        Returns:
            ExecMode: Execution mode
        """


class InteractiveCmdOptionResolver(CmdOptionResolver):

    def skip_file(self, file_name: str) -> bool:
        console.print(f'\nFile found: { file_name }')
        rename_file = Confirm.ask('Rename file?')
        return not rename_file

    def exec_mode(self, cmd: FixNamesCmd) -> CmdExecMode:
        if cmd.dst_existent_episodes:
            cmd.logger.warning('Some TV Show files will be overwriten')
            console.print('\nHow you want to proceed?')
            console.print(' 0. Abort operation')
            console.print(' 1. Rename safe files only (Skip conflicting files)')
            console.print(' 2. Rename all files (Overwrite existent files')
            user_choice = Prompt.ask(
                'Enter your choice: ',
                choices=['0', '1', '2'],
                default='1'
            )

            if user_choice == 0:
                return CmdExecMode.ABORT
            elif user_choice == 1:
                return CmdExecMode.OVERRIDE_FORBIDDEN
            elif user_choice == 2:
                return CmdExecMode.APPLY_ALL
        else:
            approved = Confirm.ask('Confirm rename operation?')
            if approved:
                return CmdExecMode.APPLY_ALL if approved else CmdExecMode.ABORT


class FixNamesCmdBuilder():
    title_attr = EpisodeAttribute('show title', False)
    season_attr = EpisodeAttribute('season number', False)
    year_attr = EpisodeAttribute('release year')
    resolution_attr = EpisodeAttribute('resolution (e.g. 1080p, 4k HDR)')
    audio_lang_attr = EpisodeAttribute('audio language (e.g. Eng, Lat, Dual)')
    comment_attr = EpisodeAttribute('extra filename info')

    episode_number_attr = EpisodeAttribute(
        'episode number',
        False,
        SharedAttrValueMode.EACH_FILE_DIFF
    )

    episode_title_attr = EpisodeAttribute(
        'episode title',
        True
    )

    @staticmethod
    def from_src_dir(src_dir: str) -> FixNamesCmd:
        return FixNamesCmdBuilder(src_dir)\
            .__scan_dir()\
            .build()

    def __init__(self,
        src_dir: str,
        opt_resolver: CmdOptionResolver = InteractiveCmdOptionResolver(),
        attr_value_resolver: AttrValueResolver = InteractiveAttrValueResolver()
    ):
        self.src_dir = src_dir
        self.opt_resolver = opt_resolver
        self.attr_value_resolver = attr_value_resolver

        self.__command = FixNamesCmd(self.src_dir)
        self.__logger = self.__command.logger

    def build(self) -> FixNamesCmd:

        # No episodes to rename
        if not self.__command.episodes and \
                not self.__command.dst_existent_episodes:
            self.__command.exec_mode = CmdExecMode.ABORT
            return self.__command

        self.__command._preview()
        self.__command.exec_mode = self.opt_resolver.exec_mode(self.__command)

        return self.__command

    def __scan_dir(self) -> 'FixNamesCmdBuilder':
        """Scans 'src_dir' looking for TV Show files and will resolve episode
        metadata.

        Found files and episodes info will be stored in command
        under construction
        """
        if not is_dir(self.src_dir):
            self.__logger.error(
                f'Provided dir does not exists. { self.src_dir }'
            )
            raise InvalidPathError()

        for ch_file in path_files(
            self.src_dir,
            extensions=_TV_SHOW_FILE_EXTENSIONS
        ):
            src_file_name = get_file_name(ch_file)

            if self.opt_resolver.skip_file(src_file_name):
                self.__command.skipped_files.append(src_file_name)
                continue

            title = self.attr_value_resolver.resolve(self.title_attr)
            season = self.attr_value_resolver.resolve(self.season_attr)
            year = self.attr_value_resolver.resolve(self.year_attr)

            episode_number = self\
                .attr_value_resolver\
                .resolve(self.episode_number_attr)

            episode_title = self\
                .attr_value_resolver\
                .resolve(self.episode_title_attr)

            resolution = self.attr_value_resolver.resolve(self.resolution_attr)
            audio_lang = self.attr_value_resolver.resolve(self.audio_lang_attr)
            comment = self.attr_value_resolver.resolve(self.comment_attr)

            episode = Episode(
                ch_file,
                title,
                season,
                episode_number,
                year,
                episode_title,
                resolution,
                audio_lang,
                comment,
                get_file_ext(ch_file)
            )

            # If destination file already exists
            if os.path.isfile(episode.make_target_file_path()):
                self.__command.dst_existent_episodes.append(episode)

            # File can be renamed with no issues
            else:
                self.__command.episodes.append(episode)

        return self
