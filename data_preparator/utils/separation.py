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


def separate_dataframe_by_product_type(
    main_df: pd.DataFrame,
    product_type_by_which_to_separate: str,
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Отделяет от переданного dataframe'а строки с переданным типом услуги в отдельный dataframe."""
    separated_df = main_df.loc[main_df['PRODUCT_TYPE'] == product_type_by_which_to_separate]
    main_df = main_df.loc[~main_df.index.isin(separated_df.index)]
    return main_df, separated_df
