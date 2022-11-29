import pandas as pd
import pytest
from data_preparator.data_frame_separators import separate_drugs, separate_devices
from data_preparator.utils.strings import remove_zeros_from_the_beginning


# @pytest.mark.usefixtures('create_and_prepare_df', 'get_nphies_codes_without_zeros_from_nomenclature')
# def test_separate_drugs(create_and_prepare_df, get_nphies_codes_without_zeros_from_nomenclature):
#     main_df, df_with_drugs = separate_drugs(create_and_prepare_df)
#     filtered_df_with_drugs = df_with_drugs.loc[(
#         df_with_drugs['PRODUCT_TYPE'] == 'MEDS'
#     ) | (
#         df_with_drugs['NPHIES_CODE'].isin(get_nphies_codes_without_zeros_from_nomenclature)
#     )]
#     assert df_with_drugs.compare(filtered_df_with_drugs).empty
#     for index_of_row_with_drug in df_with_drugs.index.values.tolist():
#         assert index_of_row_with_drug not in main_df.index.values.tolist()


# @pytest.mark.usefixtures('create_and_prepare_df', 'get_nphies_codes_without_zeros_from_nomenclature')
# def test_separate_devices(create_and_prepare_df, get_nphies_codes_without_zeros_from_nomenclature):
#     main_df, df_with_devices = separate_devices(create_and_prepare_df)
#     filtered_df_with_devices = df_with_devices.loc[(
#         df_with_devices['PRODUCT_TYPE'] == 'DEVICE'
#     ) | (
#         df_with_devices['NPHIES_CODE'].apply(
#             lambda nphies_code: nphies_code.replace('-', ''),
#         ).str.len() == 5
#     )]
#     assert df_with_devices.compare(filtered_df_with_devices).empty
#     for index_of_row_with_drug in df_with_devices.index.values.tolist():
#         assert index_of_row_with_drug not in main_df.index.values.tolist()


@pytest.mark.usefixtures('create_and_prepare_df', 'get_nphies_codes_without_zeros_from_nomenclature')
def test_separate_incomplete(create_and_prepare_df, get_nphies_codes_without_zeros_from_nomenclature):
    main_df, df_with_devices = separate_devices(create_and_prepare_df)
    filtered_df_with_devices = df_with_devices.loc[(
        df_with_devices['PRODUCT_TYPE'] == 'DEVICE'
    ) | (
        df_with_devices['NPHIES_CODE'].apply(
            lambda nphies_code: nphies_code.replace('-', ''),
        ).str.len() == 5
    )]
    assert df_with_devices.compare(filtered_df_with_devices).empty
    for index_of_row_with_drug in df_with_devices.index.values.tolist():
        assert index_of_row_with_drug not in main_df.index.values.tolist()
