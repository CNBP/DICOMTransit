import unittest
from DICOMTransit.LocalDB.API import get_StudyUIDs, append_StudyUID, set_StudyUID


class UT_LocalDB_API(unittest.TestCase):
    def test_get_StudyID(self):

        StudyUID = get_StudyUIDs(3208878)
        return True

    def test_append_StudyID(self):
        append_StudyUID(3208878, "random_string")
        return True
