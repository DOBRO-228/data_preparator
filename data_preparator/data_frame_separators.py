import re

import pandas as pd
from data_preparator import constants


def separate_rows_with_empty_cells_in_required_columns(df):
    """Отделяет строки с пустыми ячейками в обязательных колонках в отдельный дата фрейм."""
    df_with_empty_or_not_empty_required_cells = df.loc[
        :,
        constants.REQUIRED_NOT_EMPTY_COLUMNS,
    ].isnull().any(axis='columns')
    indices_of_rows_without_empty_required_cells = df.index[df_with_empty_or_not_empty_required_cells].tolist()
    df_with_empty_values_in_required_columns = df.loc[indices_of_rows_without_empty_required_cells]
    df = df.loc[~df.index.isin(indices_of_rows_without_empty_required_cells)]
    return df, df_with_empty_values_in_required_columns


def separate_drugs(df):
    """Отделяет лекарства в отдельный дата фрейм."""
    df_with_drugs = pd.read_excel('auxiliary_files/Номенклатура_лекарств.xlsx')
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
