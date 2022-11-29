import pandas as pd
import pytest
from data_preparator.data_preparator import (
    convert_str_columns_to_str_format,
    remove_blank_rows_and_columns,
    rename_columns,
)
from data_preparator.utils.strings import remove_zeros_from_the_beginning

try:
    from app.pipiline.utils.base import get_cached_mapping
except ImportError:
    DRUG_NOMENCLATURE = pd.read_excel('auxiliary_files/Номенклатура_лекарств.xlsx')
else:
    DRUG_NOMENCLATURE = get_cached_mapping('data_preparator_drug_nomenclature')


@pytest.fixture
def create_and_prepare_df():
    df = pd.read_excel('tests/fixtures/files_for_fixtures/df.xlsx')
    remove_blank_rows_and_columns(df)
    rename_columns(df)
    convert_str_columns_to_str_format(df)
    return df


@pytest.fixture
def get_nphies_codes_without_zeros_from_nomenclature():
    nphies_codes_from_nomenclature = DRUG_NOMENCLATURE['CODE'].values.tolist()
    return [
        remove_zeros_from_the_beginning(nphies_code)
        for nphies_code in nphies_codes_from_nomenclature
    ]
