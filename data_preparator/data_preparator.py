import re

import pandas as pd
from pydantic import ValidationError

from . import constants
from .data_frame_separators import separate_devices, separate_drugs, separate_incomplete_data, separate_out_data
from .exceptions import MissingColumnsInDataFrameError
from .utils.date import standardize_date_format
from .utils.excel_file import (
    apply_style,
    convert_data_frame_to_workbook_of_openpyxl,
    insert_rows_with_file_errors_into_workbook,
)
from .utils.strings import strip_and_set_lower_each_string_in_list
from .validators import DataFrameValidator, validate_required_columns

try:
    from app.pipiline.utils.base import get_cached_mapping
except ImportError:
    SERVICE_NAME_TO_NPHIES_CODE_MAPPING = pd.read_excel(
        'auxiliary_files/Маппинг_название услуги_к_нфис_коду.xlsx',
    )
else:
    SERVICE_NAME_TO_NPHIES_CODE_MAPPING = get_cached_mapping('service_name_to_nphies_code_mapping')


NPHIES_CODE = 'NPHIES_CODE'
SERVICE_QUANTITY = 'SERVICE_QUANTITY'


def process_data_frame(df: pd.DataFrame):
    """Обрабатывает данные."""
    remove_blank_rows_and_columns(df)
    primary_df_but_with_added_record_id_column = get_copy_of_df_with_added_record_id_column(df)
    df = add_record_id_column(df)
    df.columns = df.columns.str.strip()
    try:
        validate_required_columns(
            data_frame=df,
            required_column_headers=constants.COLUMNS_MAPPING.keys(),
        )
    except MissingColumnsInDataFrameError as error:
        wb = convert_data_frame_to_workbook_of_openpyxl(df)
        insert_rows_with_file_errors_into_workbook(wb, error)
        apply_style(wb)
        wb.save('debug/debug_output/missing_columns.xlsx')
        return wb
    drop_not_required_columns(df)
    rename_columns(df)
    change_service_type_val_according_to_mapping(df)
    change_benefit_type_val_according_to_mapping(df)
    df, df_with_out_data = separate_out_data(df)
    df.reset_index(drop=True, inplace=True)
    enrich_with_nphies_codes(df)
    try:
        DataFrameValidator(data_frame=df.to_dict('records'))
    except ValidationError as errors:
        df, df_with_incomplete_data = separate_incomplete_data(df, errors)
    else:
        df_with_incomplete_data = pd.DataFrame()
    set_columns_order_based_on_columns_mapping(df)
    convert_int_columns_to_int_format(df)
    convert_str_columns_to_str_format(df)
    convert_float_columns_to_float_format(df)
    convert_date_columns_to_datetime_format(df)
    convert_gender_column_to_boolean_format(df)
    fill_empty_cells_in_quantity_column(df)
    df, df_with_medical_devices = separate_devices(df)
    df, df_with_drugs = separate_drugs(df)
    return {
        'df_with_services': df,
        'df_with_medical_devices': df_with_medical_devices,
        'df_with_drugs': df_with_drugs,
        'df_with_incomplete_data': df_with_incomplete_data,
        'df_with_out_data': df_with_out_data,
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
    return add_record_id_column(df_for_results)


def drop_not_required_columns(df):
    """Удаляет ненужные колонки."""
    current_columns = df.columns.values.tolist()
    striped_and_lower_current_column_headers = strip_and_set_lower_each_string_in_list(current_columns)
    required_columns = strip_and_set_lower_each_string_in_list(constants.COLUMNS_MAPPING.keys())
    required_columns.append('record_id')
    lower_header_columns_to_drop = list(
        set(striped_and_lower_current_column_headers) - set(required_columns),
    )
    columns_to_drop = [
        header
        for header in current_columns
        if header.strip().lower() in lower_header_columns_to_drop
    ]
    df.drop(columns_to_drop, axis='columns', inplace=True)


def rename_columns(df):
    """Переименовывает колонки."""
    df.rename(
        columns=constants.COLUMNS_MAPPING,
        inplace=True,
    )


def add_record_id_column(df):
    """Создаёт колонку RECORD_ID с уникальным идентификатором строки внутри."""
    df['RECORD_ID'] = range(1, len(df.index) + 1)
    cols = df.columns.tolist()
    cols.insert(0, cols.pop(cols.index('RECORD_ID')))
    return df.reindex(columns=cols, copy=False)


def convert_str_columns_to_str_format(df):
    """Приводит нужные колонки к строке."""
    for column in constants.STR_COLUMNS:
        df[column] = df[column].astype(str)
        if column == 'NPHIES_CODE':
            # Удаляет точку и нули с конца.
            # Иногда при создании дата фрейма НФИС код 228 парсится как строка 228.0.
            df[column] = [
                re.sub(r'\.[0-9]*$', '', nphies_code)
                for nphies_code in df[column]
            ]


def convert_int_columns_to_int_format(df):
    """Приводит нужные колонки к числовому формату."""
    for column in constants.INT_COLUMNS:
        df[column] = df[column].astype(int)


def convert_float_columns_to_float_format(df):
    """Приводит нужные колонки к float формату."""
    for column in constants.FLOAT_COLUMNS:
        df[column].replace(',', '.', regex=True, inplace=True)
        df[column] = df[column].astype(float)


def convert_date_columns_to_datetime_format(df):
    """Приводит к одному формату дат колонки с датами."""
    for column in constants.COLUMNS_WITH_DATES:
        df[column] = df[column].apply(standardize_date_format)
        df[column] = pd.to_datetime(df[column], format='%d/%m/%Y', errors='coerce')


def fill_empty_cells_in_quantity_column(df):
    """Заполняет пустые ячейки или ячейки с отрицательным значением колонки количества услуг."""
    df[SERVICE_QUANTITY] = df[SERVICE_QUANTITY].fillna(1)
    df[SERVICE_QUANTITY] = df[SERVICE_QUANTITY].apply(
        lambda quantity: 1 if quantity in constants.NAN_VALUES or quantity < 1 else quantity,
    )


def change_service_type_val_according_to_mapping(df: pd.DataFrame) -> None:
    """Изменяет некоторые значения в колонке 'SERVICE_TYPE_MAPPING' согласно маппингу."""
    df['PRODUCT_TYPE'] = df['PRODUCT_TYPE'].str.strip().str.upper().replace(constants.SERVICE_TYPE_MAPPING)


def change_benefit_type_val_according_to_mapping(df: pd.DataFrame) -> None:
    """Изменяет некоторые значения в колонке 'BENEFIT_TYPE' согласно маппингу."""
    df['BENEFIT_TYPE'] = df['BENEFIT_TYPE'].str.strip().str.upper().replace(constants.BENEFIT_MAPPING)


def enrich_with_nphies_codes(df: pd.DataFrame):
    mapping_as_dict_with_lowered_service_names = SERVICE_NAME_TO_NPHIES_CODE_MAPPING.set_index('SERVICE_NAME').to_dict()[NPHIES_CODE]
    mapping_as_dict_with_lowered_service_names = {
        str(service_name).strip().lower(): str(nphies_code).strip()
        for service_name, nphies_code in mapping_as_dict_with_lowered_service_names.items()
    }

    df_lowered_services_names = [
        service_name.strip().lower()
        for service_name in df['SERVICE_NAME']
    ]
    lowered_service_names_and_nphies_codes = zip(df_lowered_services_names, df[NPHIES_CODE])

    nan_values = {'', 'nan'}

    df[NPHIES_CODE] = [
        mapping_as_dict_with_lowered_service_names[lowered_service_name_and_nphies_code[0]]
        if (
            lowered_service_name_and_nphies_code[0] in mapping_as_dict_with_lowered_service_names.keys()
        ) and (
            str(lowered_service_name_and_nphies_code[1]) in nan_values
        )
        else lowered_service_name_and_nphies_code[1]
        for lowered_service_name_and_nphies_code in list(lowered_service_names_and_nphies_codes)
    ]


def gender_convert_function(gender: str) -> bool:
    """Конвертирует пол пациента в булево значение."""
    female_values = ['F', 'f', 'Female', 'female']
    if gender in female_values:  # Noqa: WPS531
        return False
    return True


def convert_gender_column_to_boolean_format(df: pd.DataFrame) -> None:
    """Приводит к булевому значению колонку с полом пациента."""
    df['INSURED_IS_MALE'] = [
        gender_convert_function(gender)
        for gender in df['INSURED_IS_MALE']
    ]
