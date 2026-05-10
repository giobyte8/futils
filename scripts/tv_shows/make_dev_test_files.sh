#!/bin/bash
#
# Creates empty files to be used during testing and development
# of 'tv-show' command

# Get 'dev/tv_shows' path
SCRIPT_PATH="$( cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
ROOT_PATH="$(realpath "$SCRIPT_PATH/../..")"
DEV_DATA="$(realpath "$ROOT_PATH/dev/tv_shows")"

# Remove existing "DEV_DATA/*" files
rm -r "$DEV_DATA"/*

# Create empty show files
touch "$DEV_DATA/Rick and Morty (2013) - S01E01 - 1080p.mkv"
touch "$DEV_DATA/Rick and Morty S1 E2 Title 2 1080p.mkv"
touch "$DEV_DATA/Rick and Morty S1 E3 Title 3 1080p.mkv"

# Create empty files for no tv show tests
mkdir -p "$DEV_DATA/no_tv_show"
touch "$DEV_DATA/no_tv_show/file1.txt"
touch "$DEV_DATA/no_tv_show/file2.txt"
