import pandas as pd
from data_preparator import constants

prepared_data_frames = []


def prepare_data(df):
    """Предобрабатывает дата фрейм."""
    drop_not_required_columns(df)
    rename_columns(df)
    set_uniq_values_in_record_id_column(df)
    change_commas_to_dots_in_float_columns(df)
    convert_date_columns_to_datetime_format(df)
    convert_gender_column_to_boolean_format(df)
    fill_empty_cells_in_quantity_column(df)
    df, df_with_empty_values = separate_rows_with_empty_cells_in_required_columns(df)
    return {
        'df': df,
        'df_with_empty_values': df_with_empty_values,
    }


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


def separate_rows_with_empty_cells_in_required_columns(df):
    """Заполняет пустые ячейки или ячейки с отрицательным значением колонки количества услуг."""
    df_with_empty_or_not_empty_required_cells = df.loc[
        :,
        constants.REQUIRED_NOT_EMPTY_COLUMNS,
    ].isnull().any(axis='columns')
    indices_of_rows_without_empty_required_cells = df.index[df_with_empty_or_not_empty_required_cells].tolist()
    df_with_empty_values_in_required_columns = df.loc[indices_of_rows_without_empty_required_cells]
    df = df.loc[~df.index.isin(indices_of_rows_without_empty_required_cells)]
    return df, df_with_empty_values_in_required_columns


def change_commas_to_dots_in_float_columns(df):
    """Меняет запятые на точки в колонках с форматом float."""
    for column in constants.FLOAT_COLUMNS:
        df[column].replace(',', '.', regex=True, inplace=True)
        df[column] = df[column].astype(float)


def convert_date_columns_to_datetime_format(df):
    """Приводит к одному формату дат колонки с датами."""
    for column in constants.COLUMNS_WITH_DATES:
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
