"""Модуль валидаторов."""

from datetime import date, datetime
from typing import List, Union

import pandas as pd
from dateutil import parser as date_parser
from dateutil.parser import ParserError
from pandas import Timestamp
from pydantic import BaseModel, Field, validator

from . import constants
from .exceptions import MissingColumnsInDataFrameError


class RowValidator(BaseModel):
    RECORD_ID: str
    LPU_ID: str
    INSURED_ID: str
    INSURED_AGE_WHEN_SERVICED: Union[datetime, date, str] = Field(...)
    INSURED_IS_MALE: str = Field(...)
    NPHIES_CODE: str
    PRODUCT_TYPE: str
    SERVICE_NAME: str
    SERVICE_DATE: Union[datetime, date, str] = Field(...)
    SERVICE_QUANTITY: str
    SERVICE_PROVIDER_CODE: str
    MKB_CODE: str
    SECOND_MKB_CODE: str
    DISCHARGE_MKB_CODE: str
    OTHER_MKB_CODE: str
    POLICY_NUMBER: str = Field(...)
    SPECIALITY_DESCRIPTION: str
    SERVICE_AMOUNT: str

    @validator(*constants.NOT_EMPTY_REQUIRED_COLUMNS, pre=True)
    def check_cells_in_required_columns_are_not_empty(cls, value):
        if value == '' or pd.isna(value):
            raise ValueError('Это поле не может быть пустым.')
        return value

    @validator('SERVICE_NAME', pre=True)
    def service_name_and_nphies_not_empty_simultaneously(cls, value, values):
        nphies_code = values.get('NPHIES_CODE')
        if str(value) == 'nan' and str(nphies_code) == 'nan':
            raise ValueError("Один из параметров должен быть заполнен: 'SERVICE_NAME' или 'NPHIES_CODE'.")
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
    missing_columns = list(set(required_column_headers) - set(current_column_headers))
    if missing_columns:
        raise MissingColumnsInDataFrameError(missing_columns)
