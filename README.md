# futils

A CLI tool to automate repetitive tasks during management of documents and
media files

## Usage

```bash
fu [OPTIONS] COMMAND [ARGS]...
```

### Available commands

* `imgresize` Resize images to smaller resolutions applying same effect as
  'cover' css, useful for wallpapers and background images management
* `index`: Creates a text file listing all files at given path in ascending
   order. Only direct children files.
* `index-removed`: Creates a text file listing all files that are present in
   a given index but doesn't exists in specified path anymore.
* `iterate` Iterates files in a path and opens it in default application,
   useful for review pictures or multiple docs in a folder
* `iteratefrom` Iterates each line of given file as a path and will open
   it in default system program.
* `moviefixname` Assists in the process of renaming movie files into a
   format like `<Title> (Year) - <Resolution> - <Audio Lang> <Extra>.<ext>`.
   Use this for your plex library 😉
* `tvshowfixnames` Assists in the process of renaming multiple TV show files
   into a format like `<TV Show title> - S<Season number>E<Episode number>`.
   Similar to `moviefixname` but for TV show episodes files.

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
