"""Модуль валидаторов."""

from datetime import datetime
from typing import List

import pandas as pd
from data_preparator.exceptions import MissingColumnsInDataFrameError
from data_preparator.utils.date import swap_day_with_month
from dateutil import parser as date_parser
from dateutil.parser import ParserError
from pydantic import BaseModel, Field, validator

from . import constants


class RowValidator(BaseModel):
    RECORD_ID: str
    LPU_ID: str
    INSURED_ID: str
    INSURED_AGE_WHEN_SERVICED: str = Field(...)
    INSURED_IS_MALE: str = Field(...)
    NPHIES_CODE: str
    PRODUCT_TYPE: str
    SERVICE_NAME: str
    SERVICE_DATE: str = Field(...)
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
    def service_name_and_nphies_not_empty_simultaneously(cls, value, values, **kwargs):
        if value == 'nan' and values.get('NPHIES_CODE') == 'nan':
            raise ValueError("Один из параметров должен быть заполнен: 'SERVICE_NAME' или 'NPHIES_CODE'.")
        return value

    @validator('INSURED_AGE_WHEN_SERVICED', 'SERVICE_DATE')
    def date_can_be_parsed_in_columns_with_dates(cls, value, values, **kwargs):
        try:
            parsed_date = date_parser.parse(value, dayfirst=True).date()
        except ParserError:
            raise ValueError('Дата не распознаётся.')
        current_date = datetime.today().date()
        amount_of_months_in_one_year = 12
        if parsed_date > current_date:
            if parsed_date.day <= amount_of_months_in_one_year:
                if swap_day_with_month(parsed_date) > current_date:
                    raise ValueError('Дата из будущего.')
                return value
            raise ValueError('Дата из будущего.')
        return value

    @validator('SERVICE_DATE')
    def service_date_cant_be_less_than_birth_date(cls, value, values):
        birth_date = date_parser.parse(
            value,
            dayfirst=True,
        ).date()
        service_date = date_parser.parse(
            values.get('INSURED_AGE_WHEN_SERVICED'),
            dayfirst=True,
        ).date()
        if birth_date > service_date:
            raise ValueError('Дата оказания услуги меньше чем дата рождения.')
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
