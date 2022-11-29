import pytest
from data_preparator.constants import COLUMNS_MAPPING
from data_preparator.utils.validation import (
    get_indices_and_info_from_errors,
    insert_row_errors_info_into_df_by_index,
)


@pytest.mark.usefixtures('create_pydantic_errors_instance')
def test_get_indices_and_info_from_errors(create_pydantic_errors_instance):
    indexes_and_errors_of_rows_with_invalid_data = get_indices_and_info_from_errors(create_pydantic_errors_instance)
    expected_errors = {
        0: [
            {'dob': 'Mandatory field, cannot be empty.'},
            {'gender': 'Mandatory field, cannot be empty.'},
        ],
        1: [
            {'service_name': 'Mandatory field, cannot be empty.'},
            {'service_date': "'20/07/2022-228' Invalid Date."},
            {'icd10_code': 'Mandatory field, cannot be empty.'},
        ],
    }
    assert indexes_and_errors_of_rows_with_invalid_data == expected_errors


@pytest.mark.usefixtures('create_and_prepare_df_with_invalid_data', 'create_pydantic_errors_instance')
def test_insert_row_errors_info_into_df_by_index(create_and_prepare_df_with_invalid_data, create_pydantic_errors_instance):
    df_with_invalid_data = create_and_prepare_df_with_invalid_data
    indexes_and_errors_of_rows_with_invalid_data = get_indices_and_info_from_errors(create_pydantic_errors_instance)
    insert_row_errors_info_into_df_by_index(df_with_invalid_data, indexes_and_errors_of_rows_with_invalid_data)

    for row_index, errors_in_row in indexes_and_errors_of_rows_with_invalid_data.items():
        assert df_with_invalid_data.loc[row_index, 'ERRORS'] == errors_in_row


@pytest.mark.usefixtures('create_pydantic_errors_instance')
def test_rename_columns_to_their_original_names(create_pydantic_errors_instance):
    indexes_and_errors_of_rows_with_invalid_data = get_indices_and_info_from_errors(create_pydantic_errors_instance)
    for _, row_errors in indexes_and_errors_of_rows_with_invalid_data.items():
        for column_name_and_error_message in row_errors:
            assert all(
                column_name in COLUMNS_MAPPING.keys()
                for column_name in column_name_and_error_message.keys()
            )
