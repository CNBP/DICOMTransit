from ..LORIS_helper import number_extraction

def test_number_extraction():
    Prefix = "V"
    numbers = [1, 2, 3, 9, 10, 11, 12, 100, 101, 102]

    global timepoints
    timepoints = []

    for number in numbers:
        timepoints.append(Prefix + str(number))

    DualList = zip(numbers, timepoints)

    for tuple in DualList:
        assert str(tuple[0]) == number_extraction(tuple[1])[0]

if __name__ == '__main__':
    test_number_extraction()