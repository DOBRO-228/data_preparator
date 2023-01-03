from .column_manipulations import add_record_id_column


def get_copy_of_df_with_added_record_id_column(df):
    """Отдаёт копию оригинального дата фрейм, в который добавлена только колонка RECORD_ID с уникальными значениями."""
    df_for_results = df.copy()
    return add_record_id_column(df_for_results)
