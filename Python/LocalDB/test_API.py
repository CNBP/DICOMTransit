import unittest

class UT_LocalDB_API(unittest.TestCase):

    def test_get_settings(self):
        from LocalDB.API import get_setting
        get_setting("LORISurl")
        return True