
class InvalidPathError(Exception):
    pass

class DirectoryAlreadyExistsError(Exception):
    pass

class MissingRequiredDataError(Exception):
    """Error indicates user did not enter enough info \
        for required operation

    Args:
        Exception (Exception): Python base exception
    """
    pass