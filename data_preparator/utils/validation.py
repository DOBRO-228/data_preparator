import pandas as pd
from pydantic import ValidationError

from ..constants import COLUMNS_MAPPING


def get_indices_and_info_from_errors(errors: ValidationError) -> dict:
    """Забирает индексы строк и информацию об ошибках.

        Отдаёт ответ вида: {
            индекс_строки: [первая_ошибка, вторая_ошибка, ...],
            индекс_строки: [первая_ошибка, вторая_ошибка, ...],
        }
    """
    indices_of_rows_with_invalid_data = {}
    for error in errors.errors():
        row_index_with_error = error['loc'][1]
        column_name_with_error = error['loc'][2]
        error_message = error['msg']
        if row_index_with_error not in indices_of_rows_with_invalid_data:
            indices_of_rows_with_invalid_data[row_index_with_error] = [{column_name_with_error: error_message}]
        else:
            indices_of_rows_with_invalid_data[row_index_with_error].append({column_name_with_error: error_message})
    return indices_of_rows_with_invalid_data


def insert_row_errors_info_into_df_by_index(df: pd.DataFrame, row_indexes_and_errors_info: dict) -> None:
    df['ERRORS'] = ''
    reversed_columns_mapping = {
        output_column_header: input_column_header
        for input_column_header, output_column_header in COLUMNS_MAPPING.items()
    }
    for row_index, errors_in_row in row_indexes_and_errors_info.items():
        for error in errors_in_row:
            cell_with_row_errors = df.loc[row_index, 'ERRORS']
            error = {
                reversed_columns_mapping[column_with_error]: error_message
                for column_with_error, error_message in error.items()
            }
            if cell_with_row_errors == '':
                df.at[row_index, 'ERRORS'] = [error]
            else:
                df.at[row_index, 'ERRORS'] += [error]
