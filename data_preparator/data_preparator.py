import numpy as np
import pandas as pd
from data_preparator import constants

prepared_data_frames = []


def prepare_data(df):
    drop_not_required_columns(df)
    rename_columns(df)
    set_uniq_values_in_record_id_column(df)
    df, df_with_empty_values = separate_rows_with_empty_cells_in_required_columns(df)
    change_commas_to_dots_in_float_columns(df)
    convert_date_columns_to_datetime_format(df)
    convert_gender_column_to_boolean_format(df)
    fill_empty_cells_in_quantity_column(df)
    prepared_data_frames.append({
        'df': df,
        'df_with_empty_values': df_with_empty_values,
    })


def set_uniq_values_in_record_id_column(df):
    if not df['RECORD_ID'].is_unique:
        df['RECORD_ID'] = range(1, len(df.index) + 1)


def drop_not_required_columns(df):
    current_columns = df.columns.values.tolist()
    columns_to_drop = list(set(current_columns) - set(constants.COLUMNS_MAPPING.keys()))
    df.drop(columns_to_drop, axis='columns', inplace=True)


def rename_columns(df):
    df.rename(
        columns=constants.COLUMNS_MAPPING,
        inplace=True,
    )


def change_date_format(date):
    if date == '?':
        return np.nan
    date = str(date)
    if '/' in date:
        return date
    date_parts = date.split()[0].split('-')
    return f'{date_parts[1]}/{date_parts[2]}/{date_parts[0]}'


def convert_date_columns_to_datetime_format(df):
    for column in constants.COLUMNS_WITH_DATES:
        df[column] = df[column].apply(change_date_format)
        df[column] = pd.to_datetime(df[column], format='%d/%m/%Y', errors='coerce')


def extract_service_name_from_service_description(service_description):
    service_description_without_symbols = service_description.str.replace('_x000D_', '')
    service_name = service_description_without_symbols.str.lower().str.split('\n', expand=True)[1]
    return service_name.str.strip('" ')


def change_commas_to_dots_in_float_columns(df):
    for column in constants.FLOAT_COLUMNS:
        df[column].replace(',', '.', regex=True, inplace=True)
        df[column] = df[column].astype(float)


def convert_gender_column_to_boolean_format(df):
    males = ['M', 'm', 'Male', 'male']
    df['INSURED_IS_MALE'] = df['INSURED_IS_MALE'].apply(
        lambda gender: True if gender in males else False,
    )


def fill_empty_cells_in_quantity_column(df):
    df['SERVICE_QUANTITY'] = df['SERVICE_QUANTITY'].fillna(1)
    df['SERVICE_QUANTITY'] = df['SERVICE_QUANTITY'].apply(
        lambda quantity: 1 if quantity in constants.NAN_VALUES or quantity < 1 else quantity,
    )


def separate_rows_with_empty_cells_in_required_columns(df):
    df_with_empty_or_not_empty_required_cells = df.loc[
        :,
        constants.REQUIRED_NOT_EMPTY_COLUMNS,
    ].isnull().any(axis='columns')
    indices_of_rows_without_empty_required_cells = df.index[df_with_empty_or_not_empty_required_cells].tolist()
    df_with_empty_values_in_required_columns = df.loc[indices_of_rows_without_empty_required_cells]
    df = df.loc[~df.index.isin(indices_of_rows_without_empty_required_cells)]
    return df, df_with_empty_values_in_required_columns
