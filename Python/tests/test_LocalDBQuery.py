import sqlite3
from pathlib import Path
import logging
import os
import sys
from ..LocalDB_query import check_value, update_entry, create_entry
from ..LocalDB_create_CNBP import create_localDB_CNBP


logging.basicConfig(stream=sys.stdout, level=logging.INFO)

def test_CreateSubject():
    logger = logging.getLogger('UT_CreateSubject')
    PathString = "TestCNBPQuery.sqlite"

    # if SQL already exist, quit script.
    SQLPath = Path(PathString)

    # check if path is a file and exist.
    if SQLPath.is_file():
        logger.info('Test SQLite database file already exist. Gonna mess with it!')
        ''''Delete current database! During testing only'''
        os.remove(PathString)

    # Create the database
    assert create_localDB_CNBP(PathString)
    logger.info('Test SQLite database successfully created. Gonna mess with it!')

    tableName = 'id_table'  # All CNBP database should have this table name.
    MRNColumn = "MRN"
    CNBPIDColumn = "CNBPID"

    create_entry(PathString, tableName, MRNColumn, 291033)
    logger.info('Test SQLite database successfully inserted with mock records. Gonna check!')

    # Populate the table with some fake records.
    ConnectedDatabase = sqlite3.connect(PathString)
    c = ConnectedDatabase.cursor()
    c.execute(
        'SELECT * FROM {tablename} WHERE {columnname}="{columnvalue}"'.
            format(tablename=tableName, columnname=MRNColumn,columnvalue=291033))
    ResultRows = c.fetchall()

    assert len(ResultRows) > 0

    # Closing the connection to the database file
    ConnectedDatabase.close()

    # Remove test data base created
    os.remove(PathString)

    return True

def test_CheckSubjectExist():
    logger = logging.getLogger('UT_CheckSubjectExist')
    PathString = "TestCNBPQuery.sqlite"

    # if SQL already exist, quit script.
    SQLPath = Path(PathString)

    # check if path is a file and exist.
    if SQLPath.is_file():
        logger.info('Test SQLite database file already exist. Gonna mess with it!')
        ''''Delete current database! During testing only'''
        os.remove(PathString)

    # Create the database
    assert create_localDB_CNBP(PathString)
    logger.info('Test SQLite database successfully created. Gonna mess with it!')

    tableName = 'id_table'  # All CNBP database should have this table name.
    MRNColumn = "MRN"
    CNBPIDColumn = "CNBPID"

    # Populate the table with some fake records.
    ConnectedDatabase = sqlite3.connect(PathString)
    c = ConnectedDatabase.cursor()
    c.execute("INSERT INTO {tn} ({mrn},{cnbpid}) VALUES (291010,'CNBP0010001')".
              format(tn=tableName, mrn=MRNColumn, cnbpid=CNBPIDColumn))
    c.execute("INSERT INTO {tn} ({mrn},{cnbpid}) VALUES (292010,'CNBP0020001')".
              format(tn=tableName, mrn=MRNColumn, cnbpid=CNBPIDColumn))
    c.execute("INSERT INTO {tn} ({mrn},{cnbpid}) VALUES (295010,'CNBP0010001')".
              format(tn=tableName, mrn=MRNColumn, cnbpid=CNBPIDColumn))
    c.execute("INSERT INTO {tn} ({mrn},{cnbpid}) VALUES (297120,'CNBP0030001')".
              format(tn=tableName, mrn=MRNColumn, cnbpid=CNBPIDColumn))
    c.execute("INSERT INTO {tn} ({mrn},{cnbpid}) VALUES (291310,'CNBP0510001')".
              format(tn=tableName, mrn=MRNColumn, cnbpid=CNBPIDColumn))
    ConnectedDatabase.commit()
    ConnectedDatabase.close()

    logger.info('Test SQLite database successfully inserted with mock records. Gonna mess with it!')

    # Create on Connecting to the database file
    assert(check_value(PathString, tableName, "MRN", 291010))
    assert(check_value(PathString, tableName, "CNBPID", "CNBP0010001"))

    # Remove test data base created
    os.remove(PathString)

    return True

def test_CreateSubjectCheckExist():
    logger = logging.getLogger('UT_CreateAndCheck')
    PathString = "TestCNBPQuery.sqlite"

    # if SQL already exist, quit script.
    SQLPath = Path(PathString)

    # check if path is a file and exist.
    if SQLPath.is_file():
        logger.info('Test SQLite database file already exist. Gonna mess with it!')
        ''''Delete current database! During testing only'''
        os.remove(PathString)

    # Create the database
    assert create_localDB_CNBP(PathString)
    logger.info('Test SQLite database successfully created. Gonna mess with it!')

    tableName = 'id_table'  # All CNBP database should have this table name.
    MRNColumn = "MRN"
    CNBPIDColumn = "CNBPID"

    create_entry(PathString, tableName, MRNColumn, 2918210)
    create_entry(PathString, tableName, MRNColumn, 23452346)
    create_entry(PathString, tableName, MRNColumn, 2345234)
    create_entry(PathString, tableName, MRNColumn, 273411)
    create_entry(PathString, tableName, MRNColumn, 364573)
    create_entry(PathString, tableName, MRNColumn, 7424141)

    success, _ = check_value(PathString, tableName, MRNColumn, 7129112)
    assert not success

    success, _ = check_value(PathString, tableName, MRNColumn, 2918210)
    assert success

    success, _ = check_value(PathString, tableName, MRNColumn, 712921)
    assert not success

    success, _ = check_value(PathString, tableName, MRNColumn, 742)
    assert not success

    success, _ = check_value(PathString, tableName, MRNColumn, 364573)
    assert success

    logger.info('Tested SQLIte database entry. ')

    # Remove test data base created
    os.remove(PathString)

    return True

def test_SubjectUpdate():
    logger = logging.getLogger('UT_CreateAndCheck')
    PathString = "TestCNBPQuery.sqlite"

    # if SQL already exist, quit script.
    SQLPath = Path(PathString)

    # check if path is a file and exist.
    if SQLPath.is_file():
        logger.info('Test SQLite database file already exist. Gonna mess with it!')
        ''''Delete current database! During testing only'''
        os.remove(PathString)

    # Create the database
    assert create_localDB_CNBP(PathString)
    logger.info('Test SQLite database successfully created. Gonna mess with it!')

    tableName = 'id_table'  # All CNBP database should have this table name.
    MRNColumn = "MRN"
    CNBPIDColumn = "CNBPID"

    create_entry(PathString, tableName, MRNColumn, 2918210)
    create_entry(PathString, tableName, MRNColumn, 23452346)
    create_entry(PathString, tableName, MRNColumn, 2345234)
    create_entry(PathString, tableName, MRNColumn, 273411)
    create_entry(PathString, tableName, MRNColumn, 364573)
    create_entry(PathString, tableName, MRNColumn, 7424141)

    update_entry(PathString, tableName, MRNColumn, 7424141, CNBPIDColumn, "CNBPID0010001")
    update_entry(PathString, tableName, MRNColumn, 2345234, CNBPIDColumn, "CNBPID0010002")
    update_entry(PathString, tableName, MRNColumn, 2918210, CNBPIDColumn, "CNBPID0010003")
    update_entry(PathString, tableName, MRNColumn, 273411, CNBPIDColumn, "CNBPID0010004")

    success, _ = check_value(PathString, tableName, CNBPIDColumn, 'CNBPID0010006')
    assert not success

    success, _ = check_value(PathString, tableName, CNBPIDColumn, 'CNBPID0010001')
    assert success

    success, _ = check_value(PathString, tableName, CNBPIDColumn, 55555)
    assert not success

    success, _ = check_value(PathString, tableName, CNBPIDColumn, 742)
    assert not success

    success, _ = check_value(PathString, tableName, CNBPIDColumn, 'CNBPID0010003')
    assert success

    logger.info('Tested SQLIte database entry. ')

    # Remove test data base created
    os.remove(PathString)

    return True

if __name__ == '__main__':
    test_SubjectUpdate()