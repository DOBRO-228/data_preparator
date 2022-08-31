"""Модуль валидаторов."""

from datetime import date, datetime
from typing import List, Union

import pandas as pd
from data_preparator.exceptions import MissingColumnsInDataFrameError
from dateutil import parser as date_parser
from dateutil.parser import ParserError
from pandas import Timestamp
from pydantic import BaseModel, Field, validator

from . import constants


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

    @validator('SERVICE_NAME')
    def service_name_and_nphies_not_empty_simultaneously(cls, value, values):
        if value == 'nan' and values.get('NPHIES_CODE') == 'nan':
            raise ValueError("Один из параметров должен быть заполнен: 'SERVICE_NAME' или 'NPHIES_CODE'.")
        return value

    @validator('INSURED_AGE_WHEN_SERVICED', 'SERVICE_DATE')
    def date_can_be_parsed_in_columns_with_dates(cls, value):
        if isinstance(value, (Timestamp, datetime, date)):
            return value
        amounts_of_every_separator_in_date = [
            value.count(separator) for separator in constants.EXPECTED_SEPARATORS_IN_DATES
        ]
        if not any(amount_of_separator >= 2 for amount_of_separator in amounts_of_every_separator_in_date):
            raise ValueError("'{0}' Дата не распознаётся.".format(value))
        try:
            date_parser.parse(value, dayfirst=True).date()
        except ParserError:
            raise ValueError("'{0}' Дата не распознаётся.".format(value))
        return value

    @validator('INSURED_AGE_WHEN_SERVICED', 'SERVICE_DATE')
    def date_cant_be_in_the_future(cls, value):
        if value is None:
            raise ValueError("Валидация 'Дата не может быть в будущем' не может быть проведена, так как поле не прошло предыдущие валидации.")
        if isinstance(value, (Timestamp, datetime)):
            parsed_date = value.date()
        elif isinstance(value, date):
            parsed_date = value
        else:
            parsed_date = date_parser.parse(value, dayfirst=True).date()
        current_date = datetime.today().date()
        if parsed_date > current_date:
            raise ValueError(
                "Изначальная дата '{0}'. Она распозналась как '{1}' (ГГГГ-ММ-ДД). Она из будущего.".format(
                    value,
                    parsed_date,
                ),
            )
        return value

    @validator('SERVICE_DATE')
    def birth_date_cant_be_more_than_service_date(cls, value, values):
        birth_date = values.get('INSURED_AGE_WHEN_SERVICED')
        if birth_date is None:
            raise ValueError("Валидация 'Дата рождения не может быть больше даты оказания услуги' не может быть проведена, так как какое-то из этих 2-ух полей не прошло предыдущие валидации.")
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


def validate_required_columns(df: pd.DataFrame) -> None:
    """Проверяет наличие обязательных колонок в data frame'е."""
    current_column_headers = df.columns.values.tolist()
    required_column_headers = constants.COLUMNS_MAPPING.keys()
    missing_columns = list(set(required_column_headers) - set(current_column_headers))
    if missing_columns:
        raise MissingColumnsInDataFrameError(missing_columns)
