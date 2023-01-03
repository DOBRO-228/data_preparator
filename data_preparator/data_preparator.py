import pandas as pd
from pydantic import ValidationError

from . import constants
from .data_frame_separators import separate_df, separate_incomplete_data, separate_out_data
from .exceptions import MissingColumnsInDataFrameError
from .pandas.column_converters import (
    convert_date_columns_to_datetime_format,
    convert_float_columns_to_float_format,
    convert_gender_column_to_boolean_format,
    convert_int_columns_to_int_format,
    convert_str_columns_to_str_format,
)
from .pandas.column_manipulations import (
    add_record_id_column,
    change_column_values_according_to_mapping,
    enrich_with_nphies_codes,
    fill_empty_cells_in_quantity_column,
    rename_column_headers,
    set_columns_order_based_on_columns_mapping,
    standardize_nphies_code_column,
)
from .pandas.dataframe_cleaners import drop_not_required_columns, remove_blank_rows_and_columns
from .pandas.dataframe_manipulations import get_copy_of_df_with_added_record_id_column
from .utils.excel_file import (
    apply_style,
    convert_data_frame_to_workbook_of_openpyxl,
    insert_rows_with_file_errors_into_workbook,
)
from .validators import DataFrameValidator, validate_required_columns


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
        return wb
    drop_not_required_columns(df)
    rename_column_headers(df)
    convert_str_columns_to_str_format(df)
    standardize_nphies_code_column(df)
    change_column_values_according_to_mapping(
        df,
        column='PRODUCT_TYPE',
        mapping=constants.SERVICE_TYPE_MAPPING,
    )
    change_column_values_according_to_mapping(
        df,
        column='BENEFIT_TYPE',
        mapping=constants.BENEFIT_MAPPING,
    )
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
    convert_float_columns_to_float_format(df)
    convert_date_columns_to_datetime_format(df)
    convert_gender_column_to_boolean_format(df)
    fill_empty_cells_in_quantity_column(df)
    df_with_services, df_with_medical_devices, df_with_drugs = separate_df(df)
    return {
        'df_with_services': df_with_services,
        'df_with_medical_devices': df_with_medical_devices,
        'df_with_drugs': df_with_drugs,
        'df_with_incomplete_data': df_with_incomplete_data,
        'df_with_out_data': df_with_out_data,
        'primary_df_but_with_added_record_id_column': primary_df_but_with_added_record_id_column,
    }
