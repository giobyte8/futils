import pytest
import tempfile

from unittest import mock
from unittest.mock import call

from fu.common.errors import InvalidPathError
from fu.iterate_files import iterate_from_file

@pytest.fixture
def tmp_file():
    """Creates a temporary file
    """
    tmp_file = tempfile.NamedTemporaryFile()
    tmp_file.write(b"test/path/1\n")
    tmp_file.write(b"test/path/2\n")
    tmp_file.seek(0)

    yield tmp_file

    # Cleanup after usage
    tmp_file.close()

def test_iterate_from_file_invalid_path():
    filepath = '/invalid/path/to/file'

    with pytest.raises(InvalidPathError):
        iterate_from_file(filepath)

@mock.patch('fu.iterate_files.typer.launch')
@mock.patch('fu.iterate_files.Confirm.ask')
def test_iterate_from_file_default_step(mock_ask, mock_launch, tmp_file):
    mock_ask.return_value = True

    iterate_from_file(tmp_file.name)

    expected_launch_calls = [
        call('test/path/1'),
        call('test/path/2')
    ]

    assert mock_ask.called_once()
    mock_launch.assert_has_calls(expected_launch_calls)

@mock.patch('fu.iterate_files.typer.launch')
@mock.patch('fu.iterate_files.Confirm.ask')
def test_iterate_from_file_step_same_as_paths_count(
    mock_ask,
    mock_launch,
    tmp_file
):
    mock_ask.return_value = True

    iterate_from_file(tmp_file.name, step=2)

    expected_launch_calls = [
        call('test/path/1'),
        call('test/path/2')
    ]

    assert not mock_ask.called
    mock_launch.assert_has_calls(expected_launch_calls)
