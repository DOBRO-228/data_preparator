import os
import re
from typing import Tuple

import pandas as pd
from pydantic import ValidationError

from .utils.validation import get_indices_and_info_from_errors

package_dir = os.path.abspath(os.path.dirname(__file__))


def separate_drugs(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    path_to_file = os.path.join(
        package_dir,
        'auxiliary_files/Номенклатура_лекарств.xlsx',
    )
    drugs = pd.read_excel(path_to_file)
    drugs['CODE'] = drugs['CODE'].apply(
        lambda code: re.sub('^0*', '', code),
    )
    codes_of_drugs = drugs['CODE'].values.tolist()

    indices_of_rows_with_drugs = []
    for row_index in df.index:

        nphies_code_in_row = df.loc[row_index, 'NPHIES_CODE']
        product_type_in_row = df.loc[row_index, 'PRODUCT_TYPE']

        if nphies_code_in_row in codes_of_drugs:
            indices_of_rows_with_drugs.append(row_index)

        elif product_type_in_row == 'MEDS':
            indices_of_rows_with_drugs.append(row_index)

    df_with_drugs = df[df.index.isin(indices_of_rows_with_drugs)]
    df = df.loc[~df.index.isin(indices_of_rows_with_drugs)]
    return df, df_with_drugs


def separate_devices(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    df['NPHIES_CODE_WITHOUT_DASHES'] = df['NPHIES_CODE']
    df['NPHIES_CODE_WITHOUT_DASHES'] = df['NPHIES_CODE_WITHOUT_DASHES'].apply(
        lambda nphies_code: nphies_code.replace('-', ''),
    )

    indices_of_rows_with_devices = []
    for row_index in df.index:

        nphies_code_without_dashes_in_row = df.loc[row_index, 'NPHIES_CODE_WITHOUT_DASHES']
        product_type_in_row = df.loc[row_index, 'PRODUCT_TYPE']

        if len(nphies_code_without_dashes_in_row) == 5:
            indices_of_rows_with_devices.append(row_index)

        elif product_type_in_row == 'DEVICE':
            indices_of_rows_with_devices.append(row_index)

    df.drop('NPHIES_CODE_WITHOUT_DASHES', axis='columns', inplace=True)
    df_with_devices = df[df.index.isin(indices_of_rows_with_devices)]
    df = df.loc[~df.index.isin(indices_of_rows_with_devices)]
    return df, df_with_devices


def separate_incomplete_data(df: pd.DataFrame, errors: ValidationError) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Отделяет строки с невалидными данными в отдельный дата фрейм."""
    indices_of_rows_with_invalid_data = get_indices_and_info_from_errors(errors)
    df_with_incomplete_data = df.loc[indices_of_rows_with_invalid_data.keys()]
    df = df.loc[~df.index.isin(indices_of_rows_with_invalid_data.keys())]
    return df, df_with_incomplete_data
