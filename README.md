# futils

A CLI tool to automate repetitive tasks during management of documents and
media files

## Usage

```bash
fu [OPTIONS] COMMAND [ARGS]...
```

### Available commands

* `config` View, initialize, or edit application configuration.
* `imgresize` Resize images to smaller resolutions applying same effect as
  'cover' css, useful for wallpapers and background images management.
* `index`: Creates a text file listing all files at given path in ascending
   order. Only direct children files.
* `index-removed`: Creates a text file listing all files that are present in
   a given index but doesn't exists in specified path anymore.
* `iterate` Iterates files in a path and opens it in default application,
   useful for review pictures or multiple docs in a folder.
* `iteratefrom` Iterates each line of given file as a path and will open
   it in default system program.
* `rm-indexed` Permanently removes all files listed in a given index.

#### Sub-apps

* `exif` EXIF-related commands (e.g. `fu exif ls`).
* `movie` Movie file commands:
  * `fix-name` Assists in renaming movie files into a scanner-friendly format:
    `<Title> (Year) - <Resolution> <Audio Lang> <Extra>.<ext>`. Great for Plex 😉
* `tv-show` TV show file commands:
  * `fix-names` Assists in renaming TV show episode files into a format like
    `<Show title> (Year) - S<Season>E<Episode> - <Title> <Resolution>.<ext>`.

### Usage details for each subcommand

Use `--help` option to get details about each arguments, option and usage
for each command

```bash
# Show help for 'imgresize' command
fu imgresize --help
```

Output for above command:
```bash
Usage: fu imgresize [OPTIONS] [SRC_DIR]

  Resize images to smaller resolution applying same effect as css 'cover'

Arguments:
  [SRC_DIR]  Directory containing images to resize  [default: ./]

Options:
  -w, --width INTEGER   Desired width in pixels  [default: 1920]
  -h, --height INTEGER  Desired height in pixels  [default: 1080]
  -d, --dst-dir TEXT    Destination directory for resized images
  --help                Show this message and exit.
```

## Install

### Using pip

```bash
pip install futils
```

> futils depends on python 3, in some systems you may want to use `pip3` to
> install programs into python 3 environment

## Development

Check [Development section](./DEVELOPMENT.md)
