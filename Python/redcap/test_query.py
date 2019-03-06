# ----------------------------------------------------------------------------------------------------------------------
#  Imports
# ----------------------------------------------------------------------------------------------------------------------

import unittest


# ----------------------------------------------------------------------------------------------------------------------
#  UT_REDCapQuery
# ----------------------------------------------------------------------------------------------------------------------

class UT_REDCapQuery(unittest.TestCase):

    @staticmethod
    def test_load_metadata():
        from redcap.transaction import RedcapTransaction
        from redcap.query import load_metadata
        transact = RedcapTransaction()
        load_metadata(transact)


if __name__ == "__main__":

    UT_REDCapQuery.test_load_metadata()
