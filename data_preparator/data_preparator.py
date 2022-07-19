import numpy as np
import pandas as pd
from . import constants
from .data_frame_separators import (
    separate_drugs,
    separate_medical_devices,
    separate_rows_with_empty_cells_in_required_columns,
)

preprocessed_data_frames = []


def process_data_frame(df):
    """Обрабатывает данные."""
    df_for_results = get_df_for_results(df)

    drop_not_required_columns(df)
    rename_columns(df)
    set_uniq_values_in_record_id_column(df)
    convert_nphies_code_to_str(df)
    convert_date_columns_to_datetime_format(df)
    change_commas_to_dots_in_float_columns(df)
    convert_gender_column_to_boolean_format(df)
    fill_empty_cells_in_quantity_column(df)
    df, df_with_empty_values = separate_rows_with_empty_cells_in_required_columns(df)
    df, df_with_medical_devices = separate_medical_devices(df)
    df, df_with_drugs = separate_drugs(df)
    preprocessed_data_frames.append({
        'df': df,
        'df_with_medical_devices': df_with_medical_devices,
        'df_with_drugs': df_with_drugs,
        'df_with_empty_values': df_with_empty_values,
    })
    return df, df_with_medical_devices, df_with_drugs, df_for_results


def get_df_for_results(df):
    """Отдаёт дата фрейм, в котором сделана только колонка RECORD_ID."""
    df_for_results = df.copy()
    df_for_results.rename(
        columns={'SN': 'RECORD_ID'},
        inplace=True,
    )
    set_uniq_values_in_record_id_column(df_for_results)
    return df_for_results


def drop_not_required_columns(df):
    """Удаляет ненужные колонки."""
    current_columns = df.columns.values.tolist()
    columns_to_drop = list(set(current_columns) - set(constants.COLUMNS_MAPPING.keys()))
    df.drop(columns_to_drop, axis='columns', inplace=True)


def rename_columns(df):
    """Переименовывает колонки."""
    df.rename(
        columns=constants.COLUMNS_MAPPING,
        inplace=True,
    )


def set_uniq_values_in_record_id_column(df):
    """Делает каждое значение в колонке RECORD_ID уникальным.

    Если в колонке есть неуникальные значения, то перезаписывает все
    значения колонки в цифры от нуля до длины дата фрейма + 1
    """
    if not df['RECORD_ID'].is_unique:
        df['RECORD_ID'] = range(1, len(df.index) + 1)


def convert_nphies_code_to_str(df):
    df['NPHIES_CODE'] = df['NPHIES_CODE'].astype(str)


def change_commas_to_dots_in_float_columns(df):
    """Меняет запятые на точки в колонках с форматом float."""
    for column in constants.FLOAT_COLUMNS:
        df[column].replace(',', '.', regex=True, inplace=True)
        df[column] = df[column].astype(float)


def standardize_date_format(date_with_time):
    """Приводит дату к одному виду."""
    if date_with_time == '?':
        return np.nan
    date_with_time = str(date_with_time)
    if '/' in date_with_time:
        return date_with_time
    date, _ = date_with_time.split(' ')
    year, month, day = date.split('-')
    return '{day}/{month}/{year}'.format(day=day, month=month, year=year)


def convert_date_columns_to_datetime_format(df):
    """Приводит к одному формату дат колонки с датами."""
    for column in constants.COLUMNS_WITH_DATES:
        df[column] = df[column].apply(standardize_date_format)
        df[column] = pd.to_datetime(df[column], format='%d/%m/%Y', errors='coerce')


def convert_gender_column_to_boolean_format(df):
    """Приводит к булевому значению колонку с полом пациента."""
    males = ['M', 'm', 'Male', 'male']
    df['INSURED_IS_MALE'] = df['INSURED_IS_MALE'].apply(
        lambda gender: True if gender in males else False,
    )


def fill_empty_cells_in_quantity_column(df):
    """Заполняет пустые ячейки или ячейки с отрицательным значением колонки количества услуг."""
    df['SERVICE_QUANTITY'] = df['SERVICE_QUANTITY'].fillna(1)
    df['SERVICE_QUANTITY'] = df['SERVICE_QUANTITY'].apply(
        lambda quantity: 1 if quantity in constants.NAN_VALUES or quantity < 1 else quantity,
    )
