from LORIS.timepoint import LORIS_timepoint
import unittest

class UT_LORISTimepoint(unittest.TestCase):

    @staticmethod
    def test_visit_number_extraction():
        Prefix = "V"
        numbers = [1, 2, 3, 9]

        global timepoints
        timepoints = []

        for number in numbers:
            timepoints.append(Prefix + str(number))

        DualList = zip(numbers, timepoints)

        for tupleItem in DualList:
            assert str(tupleItem[0]) == LORIS_timepoint.visit_number_extraction(tupleItem[1])[0]

        # todo: 10+ visit number WILL FAIL!