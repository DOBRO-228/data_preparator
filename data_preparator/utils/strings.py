def strip_and_set_lower_each_string_in_list(strings: list) -> list:
    """Use .strip() and .lower() method on each string in list."""
    return [
        string.strip().lower()
        for string in strings
    ]
