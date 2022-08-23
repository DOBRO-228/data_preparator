from datetime import datetime

import numpy as np
from dateutil import parser as date_parser
from dateutil.parser import ParserError


def swap_day_with_month(date):
    """Меняет местами день с месяцем в объекте datetime.date."""
    day = date.day
    month = date.month
    date = date.replace(day=month)
    return date.replace(month=day)


def standardize_date_format(date_with_time):
    """Приводит дату к одному виду."""
    date_with_time = str(date_with_time)
    try:
        parsed_date = date_parser.parse(date_with_time, dayfirst=True).date()
    except ParserError:
        return np.nan
    current_date = datetime.today().date()
    amount_of_months_in_one_year = 12
    if parsed_date.day <= amount_of_months_in_one_year and parsed_date > current_date:
        parsed_date = swap_day_with_month(parsed_date)
    return parsed_date.strftime('%d/%m/%Y')
