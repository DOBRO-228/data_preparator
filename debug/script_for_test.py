import types
from datetime import date, datetime

import numpy as np
import pandas as pd
from dateutil import parser as date_parser
from dateutil.parser import ParserError
from pandas import Timestamp

COLUMN_HEADERS_MAPPING = types.MappingProxyType(
    {
        'Provider ID': 'provider_id',
        'Member ID': 'member_id',
        'DoB': 'dob',
        'Gender': 'gender',
        'Service Name': 'service_name',
        'Service Date': 'service_date',
        'Service type': 'service_type',
        'Service quantity': 'service_quantity',
        'Service amount': 'service_amount',
        'NPHIES code': 'nphies_code',
        'ICD-10 code (principal)': 'icd10_code',
        'ICD-10 code (secondary/discharge/other)': 'icd10_code_secondary',
        'Tooth': 'tooth',
        'Benefit type': 'benefit_type',
        'Practitioner name': 'doctor_name',
    },
)

STR_COLUMNS = (
    'provider_id',
    'member_id',
    'service_name',
    'icd10_code',
    'icd10_code_secondary',
    'nphies_code',
    'service_type',
    'benefit_type',
    'doctor_name',
)
DATE_COLUMNS = (
    'dob',
    'service_date',
)
INT_COLUMNS = ('service_quantity', )
FLOAT_COLUMNS = ('service_amount', )
NAN_VALUES = (
    float('nan'), 'nan', 'Nan', 'NAN', 'NaN', 'None', 'Null', 'NULL', None, np.nan,
)


def convert_str_columns_to_str_format(df):
    """Приводит нужные колонки к строке."""
    for column in STR_COLUMNS:
        df[column] = df[column].astype(str)


def convert_int_columns_to_int_format(df):
    """Приводит нужные колонки к числовому формату."""
    for column in INT_COLUMNS:
        df[column] = df[column].astype(int)


def convert_float_columns_to_float_format(df):
    """Приводит нужные колонки к float формату."""
    for column in FLOAT_COLUMNS:
        df[column].replace(',', '.', regex=True, inplace=True)
        df[column] = df[column].astype(float)


def convert_gender_column_to_boolean_format(df):
    """Приводит к булевому значению колонку с полом пациента."""
    males = ['m', 'male', '1']
    df['gender'] = df['gender'].apply(
        lambda gender: True if gender.strip().lower() in males else False,
    )


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
            parsed_date = date_parser.parse(date_with_time, dayfirst=True).date()
        except ParserError:
            return np.nan
    return parsed_date.strftime('%d/%m/%Y')


def convert_date_columns_to_datetime_format(df):
    """Приводит к одному формату дат колонки с датами."""
    for column in DATE_COLUMNS:
        df[column] = df[column].apply(standardize_date_format)
        df[column] = pd.to_datetime(df[column], format='%d/%m/%Y', errors='coerce')


def strip_and_set_lower_each_string_in_list(strings: list) -> list:
    """Use .strip() and .lower() method on each string in list."""
    return [
        string.strip().lower()
        for string in strings
    ]


def excel_to_list_of_dicts(excel_path: str) -> list:
    df = pd.read_excel(excel_path)
    df.rename(
        columns=COLUMN_HEADERS_MAPPING,
        inplace=True,
    )
    convert_str_columns_to_str_format(df)
    convert_int_columns_to_int_format(df)
    convert_float_columns_to_float_format(df)
    convert_gender_column_to_boolean_format(df)
    for column in STR_COLUMNS:
        df[column] = df[column].astype(str)
    list_of_dict = df.to_dict(orient='records')
    for row_as_dict in list_of_dict:
        for parameter_name, parameter_value in row_as_dict.items():
            if str(parameter_value) == 'nan':
                row_as_dict[parameter_name] = None
    return list_of_dict


def main():
    """Запуск скрипта."""
    print(excel_to_list_of_dicts('debug/input/тест-кейс_структура.xlsx')[0].keys())


if __name__ == '__main__':
    main()
