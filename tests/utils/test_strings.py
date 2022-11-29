from data_preparator.utils.strings import remove_zeros_from_the_beginning, strip_and_set_lower_each_string_in_list


def test_strip_and_set_lower_each_string_in_list():
    """Use .strip() and .lower() method on each string in list."""
    list_to_strip_and_set_low = ['  228  ', 'SaLaM', ' sALAm 228 YAHAa ']
    expected_list = ['228', 'salam', 'salam 228 yahaa']
    assert strip_and_set_lower_each_string_in_list(list_to_strip_and_set_low) == expected_list


def test_remove_zeros_from_the_beginning():
    """Удаляет нули, которые расположены в начале переданной строки."""
    string_to_remove_zeros_from_beginning = '0000000228'
    expected_string = '228'
    assert remove_zeros_from_the_beginning(string_to_remove_zeros_from_beginning) == expected_string
