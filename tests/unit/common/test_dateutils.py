import pytest

from fu.common.dateutils import (
    DateTimeParseFormatError,
    DateTimeParseError,
    _validate_parse_format,
    _remove_extra_chars,
    _get_datetime_fields,
    parse_date
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

class TestRemoveExtraChars:
    def test_wildcard_at_start(self):
        raw_date = 'asdf2019-01-31'
        format = '*yyyy-MM-dd'
        assert '2019-01-31' == _remove_extra_chars(raw_date, format)

    def test_wildcard_at_end(self):
        raw_date = '2019-01-31;lkjhgfds'
        format = 'yyyy-MM-dd*'
        assert '2019-01-31' == _remove_extra_chars(raw_date, format)

    def test_no_wildcard(self):
        raw_date = 'lorem2019-01-31lorem'
        format = 'xxxxxyyyy-MM-ddxxxxx'
        assert raw_date == _remove_extra_chars(raw_date, format)

class TestGetDatetimeFields:
    def test_date(self):
        raw_date = 'lo2019-01-31'
        format = 'xxyyyy-MM-dd'

        dt_fields = _get_datetime_fields(raw_date, format)
        assert 'y' in dt_fields
        assert dt_fields['y'] == '2019'

        assert 'M' in dt_fields
        assert dt_fields['M'] == '01'

        assert 'd' in dt_fields
        assert dt_fields['d'] == '31'

    def test_date_and_time(self):
        raw_date = 'lo2019-01-31 05:23'
        format = 'xxyyyy-MM-dd hh:mm'

        dt_fields = _get_datetime_fields(raw_date, format)
        assert 'y' in dt_fields
        assert dt_fields['y'] == '2019'

        assert 'M' in dt_fields
        assert dt_fields['M'] == '01'

        assert 'd' in dt_fields
        assert dt_fields['d'] == '31'

        assert 'h' in dt_fields
        assert dt_fields['h'] == '05'

        assert 'm' in dt_fields
        assert dt_fields['m'] == '23'

class TestParseDate:
    def test_date_only(self):
        rd = '2022-10-16'
        d = parse_date(rd)

        assert 2022 == d.year
        assert 10 == d.month
        assert 16 == d.day
        assert 0 == d.hour
        assert 0 == d.minute
        assert 0 == d.second


    def test_date_only_no_dashes(self):
        rd = '20221016'
        d = parse_date(rd, 'yyyyMMdd')

        assert 2022 == d.year
        assert 10 == d.month
        assert 16 == d.day
        assert 0 == d.hour
        assert 0 == d.minute
        assert 0 == d.second


    def test_date_only_with_noise_1(self):
        rd = 'lorem20221016ipsum'
        d = parse_date(rd, '-----yyyyMMddxxxxx')

        assert 2022 == d.year
        assert 10 == d.month
        assert 16 == d.day
        assert 0 == d.hour
        assert 0 == d.minute
        assert 0 == d.second


    def test_date_only_with_noise_2(self):
        rd = 'lorem20221016ipsum'
        d = parse_date(rd, '*yyyyMMddxxxxx')

        assert 2022 == d.year
        assert 10 == d.month
        assert 16 == d.day
        assert 0 == d.hour
        assert 0 == d.minute
        assert 0 == d.second


    def test_date_only_with_noise_3(self):
        rd = '2022-10-16 Random text'
        d = parse_date(rd, 'yyyy-MM-dd*')

        assert 2022 == d.year
        assert 10 == d.month
        assert 16 == d.day
        assert 0 == d.hour
        assert 0 == d.minute
        assert 0 == d.second


    def test_datetime_with_noise(self):
        rd = '20032015 15:16:23(015).jpg'
        format = 'ddMMyyyy hh:mm:ss*'

        d = parse_date(rd, format)

        assert 2015 == d.year
        assert 3 == d.month
        assert 20 == d.day

        assert 15 == d.hour
        assert 16 == d.minute
        assert 23 == d.second


    def test_wrong_year_value(self):
        rd = 'XX22-10-16 Random text'

        with pytest.raises(DateTimeParseError):
            d = parse_date(rd, 'yyyy-MM-dd*')


    def test_wrong_month_value(self):
        rd = '2022-1X-16 Random text'

        with pytest.raises(DateTimeParseError):
            d = parse_date(rd, 'yyyy-MM-dd*')


    def test_wrong_day_value(self):
        rd = '2022-10-X6 Random text'

        with pytest.raises(DateTimeParseError):
            d = parse_date(rd, 'yyyy-MM-dd*')
