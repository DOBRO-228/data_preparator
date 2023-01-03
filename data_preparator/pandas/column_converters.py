import pandas as pd

from .. import constants
from ..utils.date import standardize_date_format


def convert_str_columns_to_str_format(df: pd.DataFrame) -> None:
    """Приводит нужные колонки к строке."""
    for column in constants.STR_COLUMNS:
        df[column] = df[column].astype(str)
        df[column] = df[column].str.replace('^(None|nan)$', '', regex=True)


def convert_int_columns_to_int_format(df):
    """Приводит нужные колонки к числовому формату."""
    for column in constants.INT_COLUMNS:
        df[column] = df[column].astype(int)


def convert_float_columns_to_float_format(df):
    """Приводит нужные колонки к float формату."""
    for column in constants.FLOAT_COLUMNS:
        df[column].replace(',', '.', regex=True, inplace=True)
        df[column] = df[column].astype(float)


def convert_date_columns_to_datetime_format(df):
    """Приводит к одному формату дат колонки с датами."""
    for column in constants.COLUMNS_WITH_DATES:
        df[column] = df[column].apply(standardize_date_format)
        df[column] = pd.to_datetime(df[column], format='%d/%m/%Y', errors='coerce')


def convert_gender_column_to_boolean_format(df: pd.DataFrame) -> None:
    """Приводит к булевому значению колонку с полом пациента."""
    df['INSURED_IS_MALE'] = [
        gender_convert_function(gender)
        for gender in df['INSURED_IS_MALE']
    ]


def gender_convert_function(gender: str) -> bool:
    """Конвертирует пол пациента в булево значение."""
    female_values = ['F', 'f', 'Female', 'female']
    return gender in female_values
