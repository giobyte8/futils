import argparse
import os
import sys

parser = argparse.ArgumentParser()
parser.add_argument(
    'path',
    type=str,
    help='Path containing files to rename'
)

args = parser.parse_args()
target_path = args.path

## Validate path existence
if not os.path.exists(target_path) or not os.path.isdir(target_path):
    print('Provied path seems to be invalid: {}'.format(target_path))
    sys.exit('Verify that provided path is a valid directory')

## Get all files from dir and iterate
target_files = [f for f in os.listdir(target_path) if os.path.isfile(os.path.join(target_path, f))]

print('Starting with rename of {} files'.format(len(target_files)))

for file in target_files:
    print('\n> {}'.format(file))
    movieName = input('Enter movie name: ')
    year = input('Enter movie release year: ')
    extra = input('Enter any extra suffix [1080p Dual]: ')

    extension = os.path.splitext(file)[1]
    new_name = '{} ({})'.format(movieName, year)
    if extra:
        new_name = '{} - {}'.format(new_name, extra)
    else:
        new_name = '{} - {}'.format(new_name, '1080p Dual')


    new_name = new_name + extension
    print('> Renaming')
    print('From: {}'.format(file))
    print('To: {}'.format(new_name))

    os.rename(
        os.path.join(target_path, file),
        os.path.join(target_path, new_name)
    )
