from LORIS.helper import LORIS_helper

def test_number_extraction():
    Prefix = "V"
    numbers = [1, 2, 3, 9, 10, 11, 12, 100, 101, 102]

    global timepoints
    timepoints = []

    for number in numbers:
        timepoints.append(Prefix + str(number))

    DualList = zip(numbers, timepoints)

    for tupleItem in DualList:
        assert str(tupleItem[0]) == LORIS_helper.number_extraction(tupleItem[1])[0]

if __name__ == '__main__':
    test_number_extraction()