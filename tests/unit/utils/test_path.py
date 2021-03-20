from futils.utils.path import (
    get_file_name
)

def test_file_name():
    file = 'some/path/file.zip'
    name = get_file_name(file)

    assert name == 'file.zip'

def test_fie_name_no_ext():
    file = 'some/path/file.zip'
    name = get_file_name(file, False)

    assert name == 'file'

def test_file_name_without_ext():
    file = 'some/path/file'
    name = get_file_name(file)

    assert name == 'file'

def test_file_name_multiple_dots():
    file = 'some/path/file.tar.gz'
    name = get_file_name(file, False)

    assert name == 'file.tar'