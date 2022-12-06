import re


def strip_and_set_lower_each_string_in_list(strings: list) -> list:
    """Use .strip() and .lower() method on each string in list."""
    return [
        string.strip().lower()
        for string in strings
    ]


def remove_zeros_from_the_beginning(cell_value: str) -> str:  # Noqa: WPS118
    """Удаляет нули, которые расположены в начале переданной строки."""
    return re.sub('^0*', '', cell_value)


def remove_extra_whitespaces(string: str) -> str:
    """Заменяет много пробелов на один."""
    return re.sub('\s+', ' ', string)
