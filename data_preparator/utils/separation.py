from typing import Tuple

import pandas as pd


def separate_dataframe_by_indexes(
    main_df: pd.DataFrame,
    indexes_by_which_to_separate: list,
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Отделяет от переданного dataframe'а строки переданных индексов в отдельный dataframe."""
    separated_df = main_df.loc[indexes_by_which_to_separate]
    main_df = main_df.loc[~main_df.index.isin(indexes_by_which_to_separate)]
    return main_df, separated_df


def get_row_index_if_it_belongs_to_device(
    nphies_code_without_dashes: str,
    product_type: str,
    index: int,
) -> int:
    """Возвращает переданный индекс строки, если строка принадлежит device'у."""
    if len(nphies_code_without_dashes) == 5:
        return index

    elif product_type == 'DEVICE':
        return index


def get_row_index_if_it_belongs_to_drug(
    nphies_code_without_zeros_at_the_beginning: str,
    product_type: str,
    index: int,
    nphies_codes_of_drugs_in_nomenclature,
) -> int:
    """Возвращает переданный индекс строки, если строка принадлежит лекарству."""
    if nphies_code_without_zeros_at_the_beginning in nphies_codes_of_drugs_in_nomenclature:
        return index
    elif product_type == 'MEDS':
        return index
