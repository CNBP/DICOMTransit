from ..LORIS_timepoint import visit_number_extraction

def test_visit_number_extraction():
    Prefix = "V"
    numbers = [1, 2, 3, 9]

    global timepoints
    timepoints = []

    for number in numbers:
        timepoints.append(Prefix + str(number))

    DualList = zip(numbers, timepoints)

    for tuple in DualList:
        assert str(tuple[0]) == visit_number_extraction(tuple[1])[0]

    # todo: 10+ visit number WILL FAIL!