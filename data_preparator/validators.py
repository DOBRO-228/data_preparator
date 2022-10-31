"""Модуль валидаторов."""

from datetime import date, datetime
from typing import List, Optional, Union

import pandas as pd
from data_preparator.utils.strings import strip_and_set_lower_each_string_in_list
from dateutil import parser as date_parser
from dateutil.parser import ParserError
from pandas import Timestamp
from pydantic import BaseModel, Field, validator

from . import constants
from .exceptions import MissingColumnsInDataFrameError


class RowValidator(BaseModel):
    LPU_ID: str = Field(...)
    INSURED_ID: str = Field(...)
    INSURED_AGE_WHEN_SERVICED: Union[datetime, date, str] = Field(...)
    INSURED_IS_MALE: str = Field(...)
    SERVICE_NAME: str = Field(...)
    SERVICE_DATE: Union[datetime, date, str] = Field(...)
    PRODUCT_TYPE: Optional[str]
    SERVICE_QUANTITY: str = Field(...)
    SERVICE_AMOUNT: str = Field(...)
    NPHIES_CODE: Optional[str]
    MKB_CODE: str = Field(...)
    SECOND_MKB_CODE: Optional[str]
    TOOTH: Optional[str]
    BENEFIT_TYPE: str = Field(...)
    DOCTOR_NAME: Optional[str]

    @validator(*constants.NOT_EMPTY_REQUIRED_COLUMNS, pre=True)
    def check_cells_in_required_columns_are_not_empty(cls, value):
        if value == '' or pd.isna(value):
            raise ValueError('Это поле не может быть пустым.')
        return value

    @validator('NPHIES_CODE', pre=True)
    def product_type_and_nphies_not_empty_simultaneously(cls, value, values):
        product_type = values.get('PRODUCT_TYPE')
        if (value is None and product_type is None) or (str(value) == 'nan' and str(product_type) == 'nan'):
            raise ValueError("Один из параметров должен быть заполнен: 'service_type' или 'nphies_code'. Мы пытались найти 'nphies_code' по 'service_name', но у нас не получилось.")
        return value

    @validator('INSURED_AGE_WHEN_SERVICED', 'SERVICE_DATE', pre=True)
    def date_can_be_parsed_in_columns_with_dates(cls, value):
        if isinstance(value, (Timestamp, datetime, date)):
            return value
        error_message = "'{0}' Дата не распознаётся.".format(value)
        if not isinstance(value, str):
            raise ValueError(error_message)
        quantities_of_every_separator_in_date = [
            value.count(separator) for separator in constants.EXPECTED_SEPARATORS_IN_DATES
        ]
        if not any(quantity_of_separator >= 2 for quantity_of_separator in quantities_of_every_separator_in_date):
            raise ValueError(error_message)
        try:
            date_parser.parse(value, dayfirst=True).date()
        except ParserError:
            raise ValueError(error_message)
        return value

    @validator('INSURED_AGE_WHEN_SERVICED', 'SERVICE_DATE')
    def date_cant_be_in_the_future(cls, value):
        if isinstance(value, (Timestamp, datetime)):
            parsed_date = value.date()
        elif isinstance(value, date):
            parsed_date = value
        else:
            parsed_date = date_parser.parse(value, dayfirst=True).date()
        current_date = datetime.today().date()
        if parsed_date > current_date:
            raise ValueError(
                "Дата '{0}' распозналась как '{1}' (ГГГГ-ММ-ДД). Она из будущего.".format(
                    value,
                    parsed_date,
                ),
            )
        return value

    @validator('SERVICE_DATE')
    def birth_date_cant_be_more_than_service_date(cls, value, values):
        birth_date = values.get('INSURED_AGE_WHEN_SERVICED')
        if birth_date is None:
            return value
        if isinstance(birth_date, (Timestamp, datetime)):
            parsed_birth_date = birth_date.date()
        elif isinstance(birth_date, date):
            parsed_birth_date = birth_date
        else:
            parsed_birth_date = date_parser.parse(
                birth_date,
                dayfirst=True,
            ).date()
        if isinstance(value, (Timestamp, datetime)):
            parsed_service_date = value.date()
        elif isinstance(value, date):
            parsed_service_date = value
        else:
            parsed_service_date = date_parser.parse(
                value,
                dayfirst=True,
            ).date()
        if parsed_birth_date > parsed_service_date:
            message = "Распознанная дата рождения '{0}' больше чем распознанная дата оказания услуги {1}".format(
                parsed_birth_date,
                parsed_service_date,
            )
            raise ValueError(
                "Дата рождения: '{0}' (распозналась как '{1}' (ГГГГ-ММ-ДД)). Дата оказания услуги '{2}' (распозналась как '{3}' (ГГГГ-ММ-ДД)). {4}".format(
                    birth_date,
                    parsed_birth_date,
                    value,
                    parsed_service_date,
                    message,
                ),
            )
        return value


class DataFrameValidator(BaseModel):
    data_frame: List[RowValidator]


def validate_required_columns(data_frame: pd.DataFrame, required_column_headers: list) -> None:
    """Проверяет наличие обязательных колонок в data frame'е."""
    current_column_headers = data_frame.columns.values.tolist()
    current_column_headers = strip_and_set_lower_each_string_in_list(current_column_headers)
    required_column_headers = strip_and_set_lower_each_string_in_list(required_column_headers)
    missing_columns = list(set(required_column_headers) - set(current_column_headers))
    if missing_columns:
        raise MissingColumnsInDataFrameError(missing_columns)
