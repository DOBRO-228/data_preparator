import os
import re
from typing import Tuple

import pandas as pd
from pydantic import ValidationError

from .utils.validation import get_indices_and_info_from_errors

package_dir = os.path.abspath(os.path.dirname(__file__))


def separate_drugs(df):
    """Отделяет лекарства в отдельный дата фрейм."""
    df_with_drugs = pd.read_excel(
        os.path.join(package_dir, 'auxiliary_files/Номенклатура_лекарств.xlsx'),
    )
    df_with_drugs['CODE'] = df_with_drugs['CODE'].apply(
        lambda code: re.sub('^0*', '', code),
    )
    codes_of_drugs = df_with_drugs['CODE'].values.tolist()
    df_with_drugs = df[df['NPHIES_CODE'].isin(codes_of_drugs)]
    indices_of_rows_with_drugs = df_with_drugs.index.values.tolist()
    df = df.loc[~df.index.isin(indices_of_rows_with_drugs)]
    return df, df_with_drugs


def separate_medical_devices(df):
    """Отделяет медицинские девайсы в отдельный дата фрейм."""
    df['NPHIES_CODE_WITHOUT_DASHES'] = df['NPHIES_CODE']
    df['NPHIES_CODE_WITHOUT_DASHES'] = df['NPHIES_CODE_WITHOUT_DASHES'].apply(
        lambda nphies_code: nphies_code.replace('-', ''),
    )
    df_with_medical_devices = df[(df.NPHIES_CODE_WITHOUT_DASHES.str.len() == 5)]
    indices_of_rows_with_medical_devices = df_with_medical_devices.index.values.tolist()
    df = df.loc[~df.index.isin(indices_of_rows_with_medical_devices)]
    df.drop('NPHIES_CODE_WITHOUT_DASHES', axis='columns', inplace=True)
    df_with_medical_devices.drop('NPHIES_CODE_WITHOUT_DASHES', axis='columns', inplace=True)
    return df, df_with_medical_devices


def separate_incomplete_data(df: pd.DataFrame, errors: ValidationError) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Отделяет строки с невалидными данными в отдельный дата фрейм."""
    indices_of_rows_with_invalid_data = get_indices_and_info_from_errors(errors)
    df_with_incomplete_data = df.loc[indices_of_rows_with_invalid_data.keys()]
    df = df.loc[~df.index.isin(indices_of_rows_with_invalid_data.keys())]
    return df, df_with_incomplete_data
