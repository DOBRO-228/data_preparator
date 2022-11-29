import pandas as pd
import pytest
from data_preparator.data_preparator import (
    add_record_id_column,
    convert_str_columns_to_str_format,
    remove_blank_rows_and_columns,
    rename_columns,
)
from data_preparator.validators import DataFrameValidator
from pydantic import ValidationError


@pytest.fixture
def create_pydantic_errors_instance():
    df_with_errors = pd.read_excel('tests/fixtures/files_for_fixtures/validation_errors.xlsx')
    remove_blank_rows_and_columns(df_with_errors)
    df_with_errors = add_record_id_column(df_with_errors)
    df_with_errors.columns = df_with_errors.columns.str.strip()
    rename_columns(df_with_errors)
    convert_str_columns_to_str_format(df_with_errors)
    try:
        DataFrameValidator(data_frame=df_with_errors.to_dict('records'))
    except ValidationError as errors:
        return errors
   

@pytest.fixture
def create_and_prepare_df_with_invalid_data():
    df_with_invalid_data = pd.read_excel('tests/fixtures/files_for_fixtures/validation_errors.xlsx')
    remove_blank_rows_and_columns(df_with_invalid_data)
    df_with_invalid_data = add_record_id_column(df_with_invalid_data)
    df_with_invalid_data.columns = df_with_invalid_data.columns.str.strip()
    rename_columns(df_with_invalid_data)
    convert_str_columns_to_str_format(df_with_invalid_data)
    return df_with_invalid_data
