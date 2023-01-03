
import pandas as pd

from .. import constants
from ..utils.strings import strip_and_set_lower_each_string_in_list


def remove_blank_rows_and_columns(df: pd.DataFrame) -> None:
    """Удаляет полностью пустые строки из data frame'а."""
    df.dropna(axis=0, how='all', inplace=True)
    df = df[df.columns.dropna()]
    df.reset_index(drop=True, inplace=True)


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
