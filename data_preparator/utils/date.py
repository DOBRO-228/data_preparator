from datetime import date, datetime

import numpy as np
from dateutil import parser as date_parser
from dateutil.parser import ParserError
from pandas import Timestamp


def standardize_date_format(date_with_time):
    """Приводит дату к одному виду."""
    if str(date_with_time) == 'nan':
        date_with_time = ''
    if isinstance(date_with_time, (Timestamp, datetime)):
        parsed_date = date_with_time.date()
    elif isinstance(date_with_time, date):
        parsed_date = date_with_time
    else:
        try:
            parsed_date = date_parser.parse(date_with_time, yearfirst=True, dayfirst=False).date()
        except ParserError:
            return np.nan
    return parsed_date.strftime('%d/%m/%Y')
