import pandas as pd
from pydantic import ValidationError

from . import constants
from .data_frame_separators import separate_drugs, separate_incomplete_data, separate_medical_devices
from .exceptions import MissingColumnsInDataFrameError
from .utils.date import standardize_date_format
from .utils.excel_file import (
    apply_style,
    convert_data_frame_to_workbook_of_openpyxl,
    insert_rows_with_file_errors_into_workbook,
)
from .utils.validation import get_indices_and_info_from_errors, insert_row_errors_info_into_df_by_index
from .validators import DataFrameValidator, validate_required_columns


def process_data_frame(df):
    """Обрабатывает данные."""
    remove_blank_rows_and_columns(df)
    primary_df_but_with_added_record_id_column = get_copy_of_df_with_added_record_id_column(df)
    try:
        validate_required_columns(
            data_frame=df,
            required_column_headers=constants.COLUMNS_MAPPING.keys(),
        )
    except MissingColumnsInDataFrameError as error:
        wb = convert_data_frame_to_workbook_of_openpyxl(df)
        insert_rows_with_file_errors_into_workbook(wb, error)
        apply_style(wb)
        return wb
    drop_not_required_columns(df)
    rename_columns(df)
    try:
        DataFrameValidator(data_frame=df.to_dict('records'))
    except ValidationError as errors:
        df, df_with_incomplete_data = separate_incomplete_data(df, errors)
        indices_of_rows_with_invalid_data = get_indices_and_info_from_errors(errors)
        insert_row_errors_info_into_df_by_index(df_with_incomplete_data, indices_of_rows_with_invalid_data)
    else:
        df_with_incomplete_data = pd.DataFrame()
    set_columns_order_based_on_columns_mapping(df)
    set_uniq_values_in_record_id_column(df)
    convert_str_columns_to_str_format(df)
    change_commas_to_dots_in_float_columns(df)
    convert_date_columns_to_datetime_format(df)
    convert_gender_column_to_boolean_format(df)
    fill_empty_cells_in_quantity_column(df)
    df, df_with_medical_devices = separate_medical_devices(df)
    df, df_with_drugs = separate_drugs(df)
    return {
        'df_with_services': df,
        'df_with_medical_devices': df_with_medical_devices,
        'df_with_drugs': df_with_drugs,
        'df_with_incomplete_data': df_with_incomplete_data,
        'primary_df_but_with_added_record_id_column': primary_df_but_with_added_record_id_column,
    }


def remove_blank_rows_and_columns(df: pd.DataFrame) -> None:
    """Удаляет полностью пустые строки из data frame'а."""
    df.dropna(axis=0, how='all', inplace=True)
    df = df[df.columns.dropna()]
    df.reset_index(drop=True, inplace=True)


def set_columns_order_based_on_columns_mapping(df: pd.DataFrame) -> None:
    """Устанавливает в data frame'е такой же порядок столбцов, как и в constants.COLUMNS_MAPPING."""
    column_headers_in_right_order = constants.COLUMNS_MAPPING.values()
    df = df[column_headers_in_right_order]


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


def convert_str_columns_to_str_format(df):
    """Приводит нужные колонки к строке."""
    for column in constants.STR_COLUMNS:
        df[column] = df[column].astype(str)


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
