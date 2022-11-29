from data_preparator.exceptions import MissingColumnsInDataFrameError


def test_missing_columns_in_data_frame_error_instance():
    missing_columns = ['3', 'hundred', 'bucks']
    errors = MissingColumnsInDataFrameError(missing_columns)
    assert errors.missing_columns == missing_columns
    assert errors.message == 'Required columns are missing in the Input Data: {0}'.format(
        ', '.join(missing_columns),
    )
