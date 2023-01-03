import re

import pandas as pd

from .. import constants
from ..utils.mappings import get_service_name_to_nphies_code_mapping
from ..utils.strings import remove_extra_whitespaces

NPHIES_CODE = 'NPHIES_CODE'
SERVICE_QUANTITY = 'SERVICE_QUANTITY'


def standardize_nphies_code_column(df: pd.DataFrame) -> None:
    """
    Удаляет точку и нули с конца.

    Иногда при создании дата фрейма НФИС код, например, 228 парсится как строка 228.0
    """
    df['NPHIES_CODE'] = [
        re.sub(r'\.[0-9]*$', '', nphies_code)
        for nphies_code in df['NPHIES_CODE']
    ]


def enrich_with_nphies_codes(df: pd.DataFrame):
    """Обогащает колонку 'NPHIES_CODE'."""
    service_name_to_nphies_code_mapping = get_service_name_to_nphies_code_mapping()

    lowered_service_names_from_df = [
        service_name.strip().lower()
        for service_name in df['SERVICE_NAME']
    ]
    df_service_names_without_extra_whitespaces = [
        remove_extra_whitespaces(service_name)
        for service_name in lowered_service_names_from_df
    ]
    service_names_and_nphies_codes_from_df = zip(
        df_service_names_without_extra_whitespaces,
        df[NPHIES_CODE],
    )

    df[NPHIES_CODE] = [
        service_name_to_nphies_code_mapping[lowered_service_name_and_nphies_code[0]]
        if (
            lowered_service_name_and_nphies_code[0] in service_name_to_nphies_code_mapping.keys()
        ) and (
            str(lowered_service_name_and_nphies_code[1]) in constants.NAN_VALUES
        )
        else lowered_service_name_and_nphies_code[1]
        for lowered_service_name_and_nphies_code in list(service_names_and_nphies_codes_from_df)
    ]


def set_columns_order_based_on_columns_mapping(df: pd.DataFrame) -> None:
    """Устанавливает в data frame'е такой же порядок столбцов, как и в constants.COLUMNS_MAPPING."""
    column_headers_in_right_order = constants.COLUMNS_MAPPING.values()
    df = df[column_headers_in_right_order]


def rename_column_headers(df):
    """Переименовывает колонки."""
    df.columns = df.columns.str.lower()
    df.rename(
        columns=constants.COLUMNS_MAPPING,
        inplace=True,
    )


def add_record_id_column(df):
    """Создаёт колонку RECORD_ID с уникальным идентификатором строки внутри."""
    df['RECORD_ID'] = range(1, len(df.index) + 1)
    cols = df.columns.tolist()
    cols.insert(0, cols.pop(cols.index('RECORD_ID')))
    return df.reindex(columns=cols, copy=False)


def fill_empty_cells_in_quantity_column(df):
    """Заполняет пустые ячейки или ячейки с отрицательным значением колонки количества услуг."""
    df[SERVICE_QUANTITY] = df[SERVICE_QUANTITY].fillna(1)
    df[SERVICE_QUANTITY] = df[SERVICE_QUANTITY].apply(
        lambda quantity: 1 if quantity in constants.NAN_VALUES or quantity < 1 else quantity,
    )


def change_column_values_according_to_mapping(df: pd.DataFrame, column: str, mapping: dict) -> None:
    """Изменяет значения в переданной колонке согласно переданному маппингу."""
    df[column] = df[column].str.strip().str.upper()
    df[column] = df[column].replace(mapping)
