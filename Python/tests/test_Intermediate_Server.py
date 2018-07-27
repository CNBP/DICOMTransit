from LORIS.query import login
from LocalDB.create_CNBP import create_localDB_CNBP
from LocalDB.schema import *
from LocalDB.query import create_entry, update_entry
from Intermediate_LORIS_LocalDB import findTimePointUpdateDatabase


def test_updateLocalTimepoint():
    import os
    database_path = "Test.sqlite"
    DCCID = 642461
    table_name = CNBP_schema_table_name

    # Remove database if previously existed.
    if os.path.exists(database_path):
        os.remove(database_path)

    # Create Database
    create_localDB_CNBP(database_path)

    # Get login token:
    success, token = login()

    # Create the entry with the right PSCID with proper DCCID on dev.cnbp.ca
    create_entry(database_path, table_name, CNBP_schema_keyfield, 9999999999)

    # Update above entry with the right mock PSCID.
    update_entry(database_path, table_name, CNBP_schema_keyfield, 9999999999, "DCCID", DCCID, )

    # Now, the big guy.
    success, reason = findTimePointUpdateDatabase(token, DCCID, database_path, table_name)

    # Clean up database.
    os.remove(database_path)

    assert success