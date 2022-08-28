
_parse_format_chars = [
    'y', # Year
    'M', # Month
    'd', # Date
    'h', # Hour
    'm', # Minute
    's', # Second
    '*'
]


class DateTimeParseFormatError(Exception):
    pass


def parse_date(raw_date: str, parse_format = "yyyy-mm-dd"):
    pass


def _validate_parse_format(format: str) -> None:
    """Validates that given date format is valid for parsing strings as dates \
        or raises an InvalidDateParseFormatError exception

    Args:
        format (str): Datetime format to validate

    Raises:
        InvalidDateParseTimeFormatError: If given format is invalid
    """
    frequencies: dict = {}
    last_char: str = None

    for c in format:
        if c in ['y', 'M', 'd', 'h', 'm', 's']:

            # Increase frequency count for char
            freq = (frequencies.get(c) + 1) if c in frequencies else 1
            frequencies[c] = freq

            if freq > 1 and last_char != c:
                raise DateTimeParseFormatError(
                    f'Datetime formats with several "{ c }" chars ' \
                    'must have them contiguous'
                )
        last_char = c

    # Validate char frequencies per field
    for c, freq in frequencies.items():
        if c == '*':
            if freq > 1:
                raise DateTimeParseFormatError(
                    'Only one "*" is allowed in date time format'
                )

            if not format.startswith('*') and not format.endswith('*'):
                raise DateTimeParseFormatError(
                    '"*" char is only allowed at begining or ending of format'
                )

        elif c in ['M', 'd', 'h', 'm', 's'] and freq > 2:
            raise DateTimeParseFormatError(
                f'No more than two "{ c }" are allowed in datetime format'
            )

        elif c == 'y' and freq != 4:
            raise DateTimeParseFormatError(
                f'Four "y" digits are necessary for year parsing in format'
            )
