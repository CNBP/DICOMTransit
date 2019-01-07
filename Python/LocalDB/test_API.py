import unittest

class UT_LocalDB_API(unittest.TestCase):

    @staticmethod
    def test_get_settings():
        from LocalDB.API import get_setting
        get_setting("LORISurl")
        return True