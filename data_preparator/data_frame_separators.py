import re

import pandas as pd
from data_preparator import constants


def separate_rows_with_empty_cells_in_required_columns(df):
    """Отделяет строки с пустыми ячейками в обязательных колонках в отдельный дата фрейм."""
    df_with_empty_and_not_empty_required_cells = df.loc[
        :, constants.NOT_EMPTY_REQUIRED_COLUMNS,
    ].isna().any(axis='columns')
    df_with_empty_and_not_empty_required_simultaneously_cells = df.loc[
        :, constants.NOT_EMPTY_REQUIRED_COLUMNS_SIMULTANEOUSLY,
    ].isna().all(axis='columns')
    indices_of_rows_with_empty_required_columns = df.index[df_with_empty_and_not_empty_required_cells].tolist()
    indices_of_rows_with_empty_required_columns.extend(
        df.index[df_with_empty_and_not_empty_required_simultaneously_cells].tolist(),
    )
    df_with_empty_values_in_required_columns = df.loc[indices_of_rows_with_empty_required_columns]
    df = df.loc[~df.index.isin(indices_of_rows_with_empty_required_columns)]
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


def separate_rows_with_invalid_birth_date(df):
    df_where_birth_date_is_more_than_service_date = df.loc[df['INSURED_AGE_WHEN_SERVICED'] > df['SERVICE_DATE']]
    indices_of_rows_with_invalid_data = df_where_birth_date_is_more_than_service_date.index.values.tolist()
    df = df.loc[~df.index.isin(indices_of_rows_with_invalid_data)]
    return df, df_where_birth_date_is_more_than_service_date
