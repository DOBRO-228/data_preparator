"""Модуль с исключениями."""


class MissingColumnsInDataFrameError(ValueError):
    """Исключение возбуждается в функции, которая проверяет факт наличия всех обязательных столбцов в data frame'e.

    Attributes:
        missing_columns -- отсутствующие столбцы
        message -- объяснение ошибки
    """

    def __init__(self, missing_columns: list[str]):
        self.missing_columns = missing_columns
        self.message = 'Required columns are missing in the Input Data: {0}'.format(
            ', '.join(self.missing_columns),
        )
        super().__init__(self.message)
