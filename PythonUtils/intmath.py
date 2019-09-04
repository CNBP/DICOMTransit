def int_incrementor(input_string: str):
    """
    In some cases, you are pvodided a string that is a number and you need to adjust the number while preserve the string format.
        e.g. 0010, expecting 0011. Not hard to do but super annoying to handle elegantly each time.
    :param str:
    :return:
    """

    if input_string.isalpha() or input_string.isspace():
        raise ValueError("Input does not only contain numbers")

    numerical_length = len(input_string)
    is_numerical = input_string.isnumeric()
    is_digit = input_string.isdigit()

    if is_digit and is_digit:
        number = int(input_string)
        incremented_number = number + 1
        incremented_number_string = str(incremented_number)
        if len(input_string) == len(incremented_number_string):
            return incremented_number_string.zfill(numerical_length)
        else:
            raise ValueError(
                "Incrementor increased the value beyond original string length!"
            )

    raise ValueError("Unhandled input conditions to int_incrementor")


if __name__ == "__main__":
    assert int_incrementor("0301") == "0302"
    assert int_incrementor("9999")
    assert int_incrementor("1244.05")
    assert int_incrementor("asdf.24")
    assert int_incrementor("asdf.24")
