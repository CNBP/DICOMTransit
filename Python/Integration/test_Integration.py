from LORIS.query import LORIS_query
from LocalDB.create_CNBP import LocalDB_createCNBP
from LocalDB.schema import CNBP_blueprint

from LocalDB.query import LocalDB_query
from Integration.Intermediate_LORIS_LocalDB import findTimePointUpdateDatabase
import unittest

class UT_IntegrationTest(unittest.TestCase):

    @staticmethod
    def test_updateLocalTimepoint():
        import os
        database_path = "Test.sqlite"
        DCCID = 768766
        table_name = CNBP_blueprint.table_name

        # Remove database if previously existed.
        if os.path.exists(database_path):
            os.remove(database_path)

        # Create Database
        LocalDB_createCNBP.database(database_path)

        # Get login token:
        success, token = LORIS_query.login()

        # Create the entry with the right PSCID with proper DCCID on dev.cnbp.ca
        LocalDB_query.create_entry(database_path, table_name, CNBP_blueprint.keyfield, "8987888")

        # Update above entry with the right mock PSCID.
        LocalDB_query.update_entry(database_path, table_name, CNBP_blueprint.keyfield, "8987888", "DCCID", DCCID, )

        # Now, the big guy.
        success, reason = findTimePointUpdateDatabase(token, DCCID, database_path, table_name)

        # Clean up database.
        os.remove(database_path)

        assert success