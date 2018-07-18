from LocalDBCreate_CNBP import LocalDBCreate, LocalDBCreate_CNBP
import sqlite3
from pathlib import Path
import logging
import os
import sys
import LocalDB_schema

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

    TableName = 'whatchacallitid_table'  # All CNBP database should have this table name.
    KeyFieldString = 'whatchacalitkeyfield'

    # must pappend DBKEY creaed as the indexer column.
    NewColumns = ['whasdfasdfasdffsdf', '123345sdb', 'CNvaasa31NID', 'CNFUasdfNID', 'Ha1234sh1', 'Hasha2', 'adsfas']
    NewColumnsTypes = ['TEXT', 'BLOB', 'REAL', 'TEXT', 'TEXT', 'BLOB', 'TEXT']
    NewColumnSpec = zip(NewColumns, NewColumnsTypes)
    NewColumnSpecList = list(NewColumnSpec)

    # Create the database
    assert LocalDBCreate(PathString, TableName, KeyFieldString, NewColumnSpecList)

    # Create on Connecting to the database file
    ConnectedDatabase = sqlite3.connect(PathString)

    c = ConnectedDatabase.cursor()
    c.execute('PRAGMA TABLE_INFO({})'.format(TableName))

    fetchallResult = c.fetchall()

    NewColumns = [KeyFieldString, 'whasdfasdfasdffsdf', '123345sdb', 'CNvaasa31NID', 'CNFUasdfNID', 'Ha1234sh1',
                  'Hasha2', 'adsfas']
    NewColumnsTypes = ['INTEGER', 'TEXT', 'BLOB', 'REAL', 'TEXT', 'TEXT', 'BLOB', 'TEXT']

    for index in range(0, len(NewColumns)):
        print(fetchallResult[index][1])
        assert fetchallResult[index][1] == NewColumns[index]
        print(fetchallResult[index][2])
        assert fetchallResult[index][2] == NewColumnsTypes[index]
    ConnectedDatabase.commit()
    ConnectedDatabase.close()

    # remove test database
    os.remove(PathString)

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
    assert LocalDBCreate_CNBP(PathString)

    # Create on Connecting to the database file
    ConnectedDatabase = sqlite3.connect(PathString)
    tableName = 'id_table' #All CNBP database should have this table name.
    c = ConnectedDatabase.cursor()
    c.execute('PRAGMA TABLE_INFO({})'.format(tableName))

    #names = [tup[1] for tup in c.fetchall()]
    fetchallResult = c.fetchall()

    # must pappend DBKEY creaed as the indexer column.
    newColumns, newColumnsTypes = LocalDB_schema.concatenatedSchema()

    for index in range(0, len(newColumns)):
        print(fetchallResult[index][1])
        assert fetchallResult[index][1] == newColumns[index]
        print(fetchallResult[index][2])
        assert fetchallResult[index][2] == newColumnsTypes[index]
    ConnectedDatabase.commit()
    ConnectedDatabase.close()

    # remove test database
    os.remove(PathString)

    return True

if __name__ == '__main__':
    test_LocalDBCreate_CNBP()