from typing import Tuple

import pandas as pd
from pydantic import ValidationError

from . import constants
from .utils.separation import (
    get_row_index_if_it_belongs_to_device,
    get_row_index_if_it_belongs_to_drug,
    separate_dataframe_by_indexes,
)
from .utils.strings import remove_zeros_from_the_beginning
from .utils.validation import get_indices_and_info_from_errors, insert_row_errors_info_into_df_by_index

try:
    from app.pipiline.utils.base import get_cached_mapping
except ImportError:
    DRUG_NOMENCLATURE = pd.read_excel('auxiliary_files/Номенклатура_лекарств.xlsx')
else:
    DRUG_NOMENCLATURE = get_cached_mapping('data_preparator_drug_nomenclature')


NPHIES_CODE_WITHOUT_DASHES = 'NPHIES_CODE_WITHOUT_DASHES'


def separate_drugs(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Отделяет от data frame'а строки с лекарствами."""
    nphies_codes_of_drugs_in_nomenclature = DRUG_NOMENCLATURE['CODE'].values.tolist()
    nphies_codes_of_drugs_in_nomenclature = [
        remove_zeros_from_the_beginning(nphies_code)
        for nphies_code in nphies_codes_of_drugs_in_nomenclature
    ]

    nphies_codes_and_product_types_and_indexes = zip(
        df['NPHIES_CODE'],
        df['PRODUCT_TYPE'],
        df.index,
    )

    indexes_of_rows_with_drugs = [
        get_row_index_if_it_belongs_to_drug(
            nphies_code,
            product_type,
            row_index,
            nphies_codes_of_drugs_in_nomenclature,
        )
        for nphies_code, product_type, row_index in nphies_codes_and_product_types_and_indexes
    ]
    indexes_of_rows_with_drugs = [
        index
        for index in indexes_of_rows_with_drugs
        if index is not None
    ]

    return separate_dataframe_by_indexes(df, indexes_of_rows_with_drugs)


def separate_devices(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Отделяет строки с device'ами в отдельный дата фрейм."""
    df[NPHIES_CODE_WITHOUT_DASHES] = df['NPHIES_CODE']
    df[NPHIES_CODE_WITHOUT_DASHES] = df[NPHIES_CODE_WITHOUT_DASHES].apply(
        lambda nphies_code: nphies_code.replace('-', ''),
    )

    nphies_codes_and_product_types_and_indexes = zip(
        df[NPHIES_CODE_WITHOUT_DASHES],
        df['PRODUCT_TYPE'],
        df.index,
    )

    indexes_of_rows_with_devices = [
        get_row_index_if_it_belongs_to_device(
            nphies_code,
            product_type,
            row_index,
        )
        for nphies_code, product_type, row_index in nphies_codes_and_product_types_and_indexes
    ]
    indexes_of_rows_with_devices = [
        index
        for index in indexes_of_rows_with_devices
        if index is not None
    ]

    df.drop(NPHIES_CODE_WITHOUT_DASHES, axis='columns', inplace=True)
    return separate_dataframe_by_indexes(df, indexes_of_rows_with_devices)


def separate_incomplete_data(
    df: pd.DataFrame,
    errors: ValidationError,
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Отделяет строки с невалидными данными в отдельный дата фрейм и наполняет их описанием ошибок."""
    indexes_and_errors_info = get_indices_and_info_from_errors(errors)
    df, df_with_incomplete_data = separate_dataframe_by_indexes(
        df,
        indexes_and_errors_info.keys(),
    )
    insert_row_errors_info_into_df_by_index(df_with_incomplete_data, indexes_and_errors_info)
    return df, df_with_incomplete_data


def separate_out_data(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Отделяет строки с невалидными данными в отдельный дата фрейм."""
    df_with_out_data = df.loc[df['BENEFIT_TYPE'].isin(constants.BENEFIT_TYPES_OF_OUT_DATA_ROWS)]
    return separate_dataframe_by_indexes(df, df_with_out_data.index)
