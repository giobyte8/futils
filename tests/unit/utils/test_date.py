import pytest

from fu.utils.date import InvalidFormatError, parse_date

def test_parse_date_full_date():
    patterns = [
        'DD MM YYYY',
        'DD-MM-YYYY',
        'DD.MM.YYYY',
        'XXMMDDYYYY',
        'XXDDMMYYYYXX*',
        'YYYYMMDD'
    ]
    date_strings = [
        '31 01 1993',
        '31-01-1993',
        '31.01.1993',
        'ZX01311993',
        'AB31011993AB zyxadf;',
        '19930131',
    ]
    
    date_tuple = ('1993', '01', '31') 
    for idx in range(0, len(patterns)):
        assert date_tuple == parse_date(date_strings[idx], patterns[idx])


def test_parse_date_month_day():
    patterns = ['XXXXXXXDD-MM*', 'XXXXX MM DD']
    date_strings = ['ABCDEFG31-01BCDEF1993', 'A1993 01 31']
    
    date_tuple = ('', '01', '31')

    for idx in range(0, len(patterns)):
        assert date_tuple == parse_date(date_strings[idx], patterns[idx])

def test_parse_date_month_year():
    pattern = 'XXMM-YYYY*'
    date_str = 'ZX01-1993LOREMIPSUM'
    assert ('1993', '01', '') == parse_date(date_str, pattern)

def test_parse_invalid_pattern():
    wrong_patterns = [
        'XXXXXXDDMMYYYY*', # Sizes does not match
        'XXX DWR LJI',     # Sizes does not match
        'AAAA',            # Invalid chars
        'XXX*XXDDMMYYYY',  # '*' not at last position
        'XXXDDDMMYYYY',    # 3 digits for day
        'XXXDDMMYYYYD',    # Non consecutive day digits
        'XXXDDMMMYYYY',    # 3 digits for month
        'XXXDDMMYYYYM',    # Non consecutive month digits
        'XXXDDMMYYYYY',    # 5 digits for year
        'XXXYYYYMMDDY',    # Non consecutive year digits
    ]

    date_strings = [
        'asdfr01102019',
        'ASD10102010',
        '1994',
        '111999L11112001',
        'ABC311011993',
        'ABC310119931',
        'ABC310111993',
        'ABC310119930',
        'ABC310119933',
        'ABC199301311'
    ]

    for idx in range(0, len(wrong_patterns)):
        with pytest.raises(InvalidFormatError):
            parse_date(date_strings[idx], wrong_patterns[idx])
