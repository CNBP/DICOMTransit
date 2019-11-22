import unittest
from DICOMTransit.LocalDB_DataGator.API import get_setting


class UT_LocalDB_DataGator_API(unittest.TestCase):
    def test_get_settings(self):
        print(get_setting("LORISurl"))
        return True
