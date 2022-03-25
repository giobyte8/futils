# futils

A CLI tool to automate repetitive tasks during management of documents and
media files

## Included programs

* `imgresize` Resize images to smaller resolutions applying same effect as
  'cover' css, useful for wallpapers and background images management
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

## Usage

To get details about arguments and usage of each command, use the `help` subprogram

```bash
fu imgresize --help
```

## Install

### Using pip

```bash
pip install futils
```

> futils depends on python 3, in some systems you would want to use 'pip3' to install programs into python 3 environment

## Development

Check [Development section](./DEVELOPMENT.md)
