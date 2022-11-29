from datetime import date, datetime

import numpy as np
from data_preparator.utils.date import standardize_date_format
from pandas import Timestamp


def test_standardize_date_format_of_date_as_str():
    """Test of standardize_date_format() function."""

    date_as_str = '2000-01-20'
    assert standardize_date_format(date_as_str) == '20/01/2000'

    date_as_str = '20/01/2000'
    assert standardize_date_format(date_as_str) == '20/01/2000'


def test_standardize_date_format_of_invalid_date():
    """Test of standardize_date_format() function."""

    assert np.isnan(
        standardize_date_format(np.nan),
    )

    invalid_date = '228/01/2000'
    assert np.isnan(
        standardize_date_format(invalid_date),
    )

    invalid_date = '28-10'
    assert np.isnan(
        standardize_date_format(invalid_date),
    )


def test_standardize_date_format_of_date_formats():
    """Test of standardize_date_format() function."""

    timestamp = Timestamp(year=2000, month=12, day=30, hour=8)
    assert standardize_date_format(timestamp) == timestamp.date().strftime('%d/%m/%Y')

    date_with_time = datetime.now()
    assert standardize_date_format(date_with_time) == date_with_time.date().strftime('%d/%m/%Y')

    only_date = date(2000, 12, 30)
    assert standardize_date_format(only_date) == only_date.strftime('%d/%m/%Y')
