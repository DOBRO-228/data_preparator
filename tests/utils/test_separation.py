import pytest
from data_preparator.utils.separation import (
    get_row_index_if_it_belongs_to_device,
    get_row_index_if_it_belongs_to_drug,
    separate_dataframe_by_indexes,
)


@pytest.mark.usefixtures('create_and_prepare_df')
def test_separate_dataframe_by_indexes(create_and_prepare_df):
    separated_by_indexes = [2, 5, 3]
    main_id, separated_df = separate_dataframe_by_indexes(
        create_and_prepare_df,
        separated_by_indexes,
    )
    assert all([
        index not in main_id.index
        for index in separated_by_indexes
    ])
    assert separated_df.index.values.tolist() == separated_by_indexes


def test_get_row_index_if_it_belongs_to_device():
    assert get_row_index_if_it_belongs_to_device(
        '22822',
        'SRVS',
        2,
    ) == 2
    assert get_row_index_if_it_belongs_to_device(
        '1488-228',
        'DEVICE',
        2,
    ) == 2
    assert get_row_index_if_it_belongs_to_device(
        '22822',
        'DEVICE',
        2,
    ) == 2
    assert get_row_index_if_it_belongs_to_device(
        '1488-228',
        'MEDS',
        2,
    ) == None


def test_get_row_index_if_it_belongs_to_drug():
    assert get_row_index_if_it_belongs_to_drug(
        '6285074000864',
        'SRVS',
        3,
    ) == 3
    assert get_row_index_if_it_belongs_to_drug(
        '22822',
        'MEDS',
        3,
    ) == 3
    assert get_row_index_if_it_belongs_to_drug(
        '6285074000864',
        'MEDS',
        3,
    ) == 3
    assert get_row_index_if_it_belongs_to_drug(
        '1488-228',
        'SRVS',
        3,
    ) == None


