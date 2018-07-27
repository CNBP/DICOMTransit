from pathlib import Path
import logging
import os
import sys
from LocalDB.create_CNBP import LocalDBCreate, create_localDB_CNBP
from LocalDB.query import check_header
from LocalDB.schema import *


logging.basicConfig(stream=sys.stdout, level=logging.INFO)

def test_LocalDBCreate():
    logger = logging.getLogger('UT_LocalDBCreate')
    PathString = "Test.sqlite"
    # if SQL already exist, quit script.
    SQLPath = Path(PathString)

    # check if path is a fiel and exist.
    if SQLPath.is_file():
        logger.info('Test SQLite database file already exist. Gonna mess with it!')
        ''''Delete current database! During testing only'''
        os.remove(PathString)

    table_name = 'whatchacallitid_table'  # All CNBP database should have this table name.
    KeyFieldString = 'whatchacalitkeyfield'

    # must pappend DBKEY creaed as the indexer column.
    NewColumns = ['whasdfasdfasdffsdf', '123345sdb', 'CNvaasa31NID', 'CNFUasdfNID', 'Ha1234sh1', 'Hasha2', 'adsfas']
    NewColumnsTypes = ['TEXT', 'BLOB', 'REAL', 'TEXT', 'TEXT', 'BLOB', 'TEXT']

    NewColumnSpec = zip(NewColumns, NewColumnsTypes)
    NewColumnSpecList = list(NewColumnSpec)

    # Create the database
    assert LocalDBCreate(PathString, table_name, KeyFieldString, NewColumnSpecList)



    table_header = check_header(PathString, table_name)

    # Remove database before assertion that potentially fail.
    os.remove(PathString)

    NewColumns = [KeyFieldString, 'whasdfasdfasdffsdf', '123345sdb', 'CNvaasa31NID', 'CNFUasdfNID', 'Ha1234sh1',
                  'Hasha2', 'adsfas']
    NewColumnsTypes = ['INTEGER', 'TEXT', 'BLOB', 'REAL', 'TEXT', 'TEXT', 'BLOB', 'TEXT']

    for index in range(0, len(NewColumns)):
        print(table_header[index][1])
        assert table_header[index][1] == NewColumns[index]
        print(table_header[index][2])
        assert table_header[index][2] == NewColumnsTypes[index]

    return True

def test_LocalDBCreate_CNBP():
    logger = logging.getLogger('UT_LocalDBCreate_CNBP')
    PathString = "TestCNBP.sqlite"
    # if SQL already exist, quit script.
    SQLPath = Path(PathString)

    # check if path is a fiela nd exist.
    if SQLPath.is_file():
        logger.info('Test SQLite database file already exist. Gonna mess with it!')
        ''''Delete current database! During testing only'''
        os.remove(PathString)

    # Create the database
    assert create_localDB_CNBP(PathString)


    tableName = CNBP_schema_table_name #All CNBP database should have this table name.

    fetchallResult = check_header(PathString, tableName)

    # remove test database
    os.remove(PathString)

    # must pappend DBKEY creaed as the indexer column.
    newColumns, newColumnsTypes = concatenatedSchema()

    for index in range(0, len(newColumns)):
        print(fetchallResult[index][1])
        assert fetchallResult[index][1] == newColumns[index]
        print(fetchallResult[index][2])
        assert fetchallResult[index][2] == newColumnsTypes[index]


    return True

if __name__ == '__main__':
    test_LocalDBCreate()