from typing import Tuple

import pandas as pd
from pydantic import ValidationError

from . import constants
from .utils.separation import separate_dataframe_by_indexes, separate_dataframe_by_product_type
from .utils.strings import remove_zeros_from_the_beginning
from .utils.validation import get_indices_and_info_from_errors, insert_row_errors_info_into_df_by_index

try:
    from app.pipiline.utils.base import get_cached_mapping
except ImportError:
    DRUG_NOMENCLATURE = pd.read_excel('auxiliary_files/Номенклатура_лекарств.xlsx')
    SERVICES_FROM_FILE = pd.read_excel('auxiliary_files/services_nphies_codes.xlsx')
else:
    DRUG_NOMENCLATURE = get_cached_mapping('data_preparator_drug_nomenclature')
    SERVICES_FROM_FILE = get_cached_mapping('data_preparator_services_nphies_codes')


NPHIES_CODE = 'NPHIES_CODE'


def separate_df(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Разделяет dataframe на услуги, девайсы и лекарства."""
    df, df_with_services_by_nphies_codes = separate_services_by_nphies_codes(df)
    df, df_with_medical_devices_by_nphies_codes = separate_devices_by_nphies_codes(df)
    df, df_with_drugs_by_nphies_codes = separate_drugs_by_nphies_codes(df)

    df, df_with_medical_devices_by_product_type = separate_dataframe_by_product_type(df, 'DEVICES')
    df, df_with_drugs_by_product_type = separate_dataframe_by_product_type(df, 'MEDS')

    df_with_services = pd.concat((df, df_with_services_by_nphies_codes))
    df_with_medical_devices = pd.concat(
        (df_with_medical_devices_by_nphies_codes, df_with_medical_devices_by_product_type),
    )
    df_with_drugs = pd.concat((df_with_drugs_by_nphies_codes, df_with_drugs_by_product_type))
    df_with_services.sort_index(inplace=True)
    df_with_medical_devices.sort_index(inplace=True)
    df_with_drugs.sort_index(inplace=True)
    return df_with_services, df_with_medical_devices, df_with_drugs


def separate_services_by_nphies_codes(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Отделяет от data frame'а по НФИС кодам строки с услугами."""
    nphies_codes_from_file_with_services = SERVICES_FROM_FILE[NPHIES_CODE].values.tolist()
    indexes_of_rows_with_services = [
        row_index
        for row_index, nphies_code in zip(df.index, df[NPHIES_CODE])
        if nphies_code in nphies_codes_from_file_with_services
    ]
    return separate_dataframe_by_indexes(df, indexes_of_rows_with_services)


def separate_drugs_by_nphies_codes(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Отделяет от data frame'а по НФИС кодам строки с лекарствами."""
    nphies_codes_of_drugs_in_nomenclature = DRUG_NOMENCLATURE['CODE'].values.tolist()
    nphies_codes_of_drugs_in_nomenclature = [
        remove_zeros_from_the_beginning(nphies_code)
        for nphies_code in nphies_codes_of_drugs_in_nomenclature
    ]

    nphies_codes_without_zeros = [
        remove_zeros_from_the_beginning(nphies_code.strip())
        for nphies_code in df[NPHIES_CODE]
    ]

    indexes_of_rows_with_drugs = [
        row_index
        for row_index, nphies_code in zip(df.index, nphies_codes_without_zeros)
        if nphies_code in nphies_codes_of_drugs_in_nomenclature
    ]

    df, df_with_drugs = separate_dataframe_by_indexes(df, indexes_of_rows_with_drugs)
    df_with_drugs[NPHIES_CODE] = [
        remove_zeros_from_the_beginning(nphies_code.strip())
        for nphies_code in df_with_drugs[NPHIES_CODE]
    ]
    return df, df_with_drugs


def separate_devices_by_nphies_codes(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Отделяет строки с device'ами по длине НФИС кода в отдельный дата фрейм."""
    nphies_code_without_dashes = [
        nphies_code.replace('-', '')
        for nphies_code in df[NPHIES_CODE]
    ]

    indexes_of_rows_with_devices = [
        row_index
        for row_index, nphies_code in zip(df.index, nphies_code_without_dashes)
        if len(nphies_code) == 5
    ]

    return separate_dataframe_by_indexes(df, indexes_of_rows_with_devices)


def separate_drugs_by_product_type(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Отделяет от data frame'а по типу услуги строки с лекарствами."""
    indexes_of_rows_with_drugs = [
        row_index
        for row_index, product_type in zip(df.index, df['PRODUCT_TYPE'])
        if product_type == 'MEDS'
    ]

    df, df_with_drugs = separate_dataframe_by_indexes(df, indexes_of_rows_with_drugs)
    df_with_drugs[NPHIES_CODE] = [
        remove_zeros_from_the_beginning(nphies_code.strip())
        for nphies_code in df_with_drugs[NPHIES_CODE]
    ]
    return df, df_with_drugs


def separate_devices_by_product_type(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Отделяет строки с device'ами по типу в отдельный дата фрейм."""
    indexes_of_rows_with_devices = [
        row_index
        for row_index, product_type in zip(df.index, df['PRODUCT_TYPE'])
        if product_type == 'DEVICE'
    ]

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
    """Отделяет OUT DATA строки в отдельный дата фрейм."""
    df_with_out_data = df.loc[df['BENEFIT_TYPE'].isin(constants.BENEFIT_TYPES_OF_OUT_DATA_ROWS)]
    return separate_dataframe_by_indexes(df, df_with_out_data.index)
