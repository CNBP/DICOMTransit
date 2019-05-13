from pathlib import Path
import logging
import os
import sys
import unittest
from LocalDB.create_CNBP import LocalDB_createCNBP
from LocalDB.create import LocalDB_create
from LocalDB.query import LocalDB_query
from LocalDB.schema import CNBP_blueprint

logger = logging.getLogger()


class UT_LocalDBCreate(unittest.TestCase):
    def test_LocalDBCreate(self):

        PathString = "Test.sqlite"
        # if SQL already exist, quit script.
        SQLPath = Path(PathString)

        # check if path is a fiel and exist.
        if SQLPath.is_file():
            logger.warning(
                "Test SQLite database file already exist. Gonna mess with it!"
            )
            """'Delete current database! During testing only"""
            os.remove(PathString)

        table_name = (
            "whatchacallitid_table"
        )  # All CNBP database should have this table name.
        KeyFieldString = "whatchacalitkeyfield"

        # must pappend DBKEY creaed as the indexer column.
        NewColumns = [
            "whasdfasdfasdffsdf",
            "123345sdb",
            "CNvaasa31NID",
            "CNFUasdfNID",
            "Ha1234sh1",
            "Hasha2",
            "adsfas",
        ]
        NewColumnsTypes = ["TEXT", "BLOB", "REAL", "TEXT", "TEXT", "BLOB", "TEXT"]

        NewColumnSpec = zip(NewColumns, NewColumnsTypes)
        NewColumnSpecList = list(NewColumnSpec)

        # Create the database
        assert LocalDB_create.database(
            PathString, table_name, KeyFieldString, NewColumnSpecList
        )

        table_header = LocalDB_query.check_header(PathString, table_name)

        # Remove database before assertion that potentially fail.
        os.remove(PathString)

        NewColumns = [
            KeyFieldString,
            "whasdfasdfasdffsdf",
            "123345sdb",
            "CNvaasa31NID",
            "CNFUasdfNID",
            "Ha1234sh1",
            "Hasha2",
            "adsfas",
        ]
        NewColumnsTypes = [
            "INTEGER",
            "TEXT",
            "BLOB",
            "REAL",
            "TEXT",
            "TEXT",
            "BLOB",
            "TEXT",
        ]

        for index in range(0, len(NewColumns)):
            print(table_header[index][1])
            assert table_header[index][1] == NewColumns[index]
            print(table_header[index][2])
            assert table_header[index][2] == NewColumnsTypes[index]

        return True

    def test_LocalDBCreate_CNBP(self):

        PathString = "TestCNBP.sqlite"
        # if SQL already exist, quit script.
        SQLPath = Path(PathString)

        # check if path is a fiela nd exist.
        if SQLPath.is_file():
            logger.warning(
                "Test SQLite database file already exist. Gonna mess with it!"
            )
            """'Delete current database! During testing only"""
            os.remove(PathString)

        # Create the database
        assert LocalDB_createCNBP.database(PathString)

        tableName = (
            CNBP_blueprint.table_name
        )  # All CNBP database should have this table name.

        fetchallResult = LocalDB_query.check_header(PathString, tableName)

        # remove test database
        os.remove(PathString)

        # must pappend DBKEY creaed as the indexer column.

        for index in range(0, len(CNBP_blueprint.schema)):
            print(fetchallResult[index][1])
            assert fetchallResult[index][1] == CNBP_blueprint.schema[index]
            print(fetchallResult[index][2])
            assert fetchallResult[index][2] == CNBP_blueprint.schema_types[index]
        return True
