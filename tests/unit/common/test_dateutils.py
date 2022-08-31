import pytest

from fu.common.dateutils import (
    DateTimeParseFormatError,
    _validate_parse_format
)


class TestValidateParseFormat:
    def test_invalid_frequencies(self):
        wrong_formats = [
            'yyyyy-MM-dd',
            'yy-MM-dd',
            'yyyy MM dd hh:mm:sss',
            'yyyy MM dd hh:mm:sss',
            'yyyy Mm dd hh:mm:sss',
            '*MM ddd hh:mm:ss*'
            '**MM dd hh:mm:ss'
        ]

        for format in wrong_formats:
            with pytest.raises(DateTimeParseFormatError):
                _validate_parse_format(format)

    def test_valid_formats(self):
        formats = [
            '* yyyyMMddhhmmss',
            'MM-dd hh:mm:ss',
            'yyyy-MM-dd',
            'ddMMyyyy-hh:mm:ss'
        ]

        for format in formats:
            try:
                _validate_parse_format(format)
            except DateTimeParseFormatError:
                pytest.fail('Unexpected datetime format validation error')
