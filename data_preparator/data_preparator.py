import re

import pandas as pd

from . import constants
from .data_frame_separators import (
    separate_drugs,
    separate_medical_devices,
    separate_rows_with_empty_cells_in_required_columns,
    separate_rows_with_invalid_birth_date,
)
from .utils.date import standardize_date_format
from .validators import DataFrameValidator, validate_required_columns


def process_data_frame(df):
    """Обрабатывает данные."""
    remove_blank_rows(df)
    primary_df_but_with_added_record_id_column = get_copy_of_df_with_added_record_id_column(df)
    validate_required_columns(df)
    drop_not_required_columns(df)
    rename_columns(df)
    DataFrameValidator(data_frame=df.to_dict('records'))
    set_columns_order_based_on_columns_mapping(df)
    set_uniq_values_in_record_id_column(df)
    convert_mkb_columns_to_str(df)
    convert_nphies_code_and_service_name_to_str(df)
    change_commas_to_dots_in_float_columns(df)
    convert_date_columns_to_datetime_format(df)
    df, df_with_empty_values = separate_rows_with_empty_cells_in_required_columns(df)
    df, df_where_birth_date_is_more_than_service_date = separate_rows_with_invalid_birth_date(df)
    remove_zeros_from_left_side_of_nphies_codes(df)
    convert_gender_column_to_boolean_format(df)
    fill_empty_cells_in_quantity_column(df)
    df, df_with_medical_devices = separate_medical_devices(df)
    df, df_with_drugs = separate_drugs(df)
    df_with_incomplete_data = pd.concat([
        df_with_empty_values,
        df_where_birth_date_is_more_than_service_date,
    ])
    return {
        'prepared_df': df,
        'df_with_medical_devices': df_with_medical_devices,
        'df_with_drugs': df_with_drugs,
        'df_with_incomplete_data': df_with_incomplete_data,
        'primary_df_but_with_added_record_id_column': primary_df_but_with_added_record_id_column,
    }


def remove_blank_rows(df: pd.DataFrame) -> None:
    """Удаляет полностью пустые строки из data frame'а."""
    df.dropna(axis=0, how='all', inplace=True)
    df.reset_index(inplace=True)


def set_columns_order_based_on_columns_mapping(df: pd.DataFrame) -> None:
    """Устанавливает в data frame'е такой же порядок столбцов, как и в constants.COLUMNS_MAPPING."""
    column_headers_in_right_order = constants.COLUMNS_MAPPING.values()
    df = df[column_headers_in_right_order]


def remove_zeros_from_left_side_of_nphies_codes(df):
    """Убирает нули с левой стороны НФИС кода."""
    df['NPHIES_CODE'] = df['NPHIES_CODE'].apply(
        lambda code: re.sub('^0*', '', code),
    )


def get_copy_of_df_with_added_record_id_column(df):
    """Отдаёт копию оригинального дата фрейм, в который добавлена только колонка RECORD_ID с уникальными значениями."""
    df_for_results = df.copy()
    df_for_results['RECORD_ID'] = df_for_results['SN']
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


def convert_mkb_columns_to_str(df):
    """Приводит к строке колонки с МКБ кодами."""
    for mkb_column in constants.MKB_COLUMNS:
        df[mkb_column] = df[mkb_column].astype(str)


def convert_nphies_code_and_service_name_to_str(df):
    """Приводит к строке колонки с НФИС кодом и Наименованием услуги."""
    columns_to_convert = ('NPHIES_CODE', 'SERVICE_NAME')
    for column_name in columns_to_convert:
        df[column_name] = df[column_name].astype(str)


def change_commas_to_dots_in_float_columns(df):
    """Меняет запятые на точки в колонках с форматом float."""
    for column in constants.FLOAT_COLUMNS:
        df[column].replace(',', '.', regex=True, inplace=True)
        df[column] = df[column].astype(float)


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
