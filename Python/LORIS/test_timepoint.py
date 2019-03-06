from LORIS.timepoint import LORIS_timepoint
import unittest

class UT_LORISTimepoint(unittest.TestCase):

    def test_visit_number_extraction(self):
        Prefix = "V"
        numbers = [1, 2, 3, 9]

        timepoints = []

        for number in numbers:
            timepoints.append(Prefix + str(number))

        DualList = zip(numbers, timepoints)

        for tupleItem in DualList:
            assert str(tupleItem[0]) == LORIS_timepoint.visit_number_extraction(tupleItem[1])[0]

        # todo: 10+ timepoint number WILL FAIL!