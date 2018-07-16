import sys
import os
import argparse
import getpass
import logging
import sqlite3
from pathlib import Path

logging.basicConfig(stream=sys.stdout, level=logging.INFO)

def CheckSubjectExist(DatabasePath, TableName, ColumnName, ColumnValue):
    logger = logging.getLogger('LORISQuery_CheckSubjectExist')

    # if SQL already exist, quit script.
    SQLPath = Path(DatabasePath)

    # check if path is a file and exist.
    if not SQLPath.is_file():
        logger.info('SQLite database file does not exist!')
        return False

    #Try to connect the database to start the process:
    try:
        # Create on Connecting to the database file
        ConnectedDatabase = sqlite3.connect(DatabasePath)
        c = ConnectedDatabase.cursor()

        logger.info('Creating PRIMARY KEY DBKEY column in database.')

        # Creating a new SQLite TableName with DBKey column (inspired by: https://sebastianraschka.com/Articles/2014_sqlite_in_python_tutorial.html)
        c.execute('SELECT * FROM {tablename} WHERE {columnname}="{columnvalue}"'.format(tablename=TableName, columnname=ColumnName, columnvalue=ColumnValue))

        ResultRows = c.fetchall()
    except:
        raise IOError()

    # Closing the connection to the database file
    ConnectedDatabase.close()

    if len(ResultRows) > 0:
        return True
    else:
        return False

'''A general function to create entries into the database BY providing the name of the KEYValue field and KEYvalue value to be created'''
def CreateEntry(DatabasePath, TableName, KeyField, KeyFieldValue):
    logger = logging.getLogger('LORISQuery_CreateSubject')

    # if SQL already exist, quit script.
    SQLPath = Path(DatabasePath)

    # check if path is a file and exist.
    if not SQLPath.is_file():
        logger.info('SQLite database file does not exist!')
        return False

    # Try to connect the database to start the process:
    try:
        # Create on Connecting to the database file
        ConnectedDatabase = sqlite3.connect(DatabasePath)
        c = ConnectedDatabase.cursor()

        logger.info('Creating new record in SQLite database.')

        # Creating a new SQLite record row (inspired by: https://sebastianraschka.com/Articles/2014_sqlite_in_python_tutorial.html)
        c.execute('INSERT OR IGNORE INTO {tn} ({field}) VALUES ("{value}")'.format(tn=TableName, field=KeyField, value=KeyFieldValue))
    except:
        raise IOError()

    # Closing the connection to the database file
    ConnectedDatabase.commit()
    ConnectedDatabase.close()

'''A general function to create entries into the database BY providing the name of the KEYValue field and KEYvalue value to be created'''
def UpdateEntry(DatabasePath, TableName, KeyField, KeyFieldValue, Field, FieldValue):
    logger = logging.getLogger('LORISQuery_CreateSubject')

    # if SQL already exist, quit script.
    SQLPath = Path(DatabasePath)

    # check if path is a file and exist.
    if not SQLPath.is_file():
        logger.info('SQLite database file does not exist!')
        return False

    # Try to connect the database to start the process:
    try:
        # Create on Connecting to the database file
        ConnectedDatabase = sqlite3.connect(DatabasePath)
        c = ConnectedDatabase.cursor()

        logger.info('Update records in SQLite database.')

        # Update SQLite record row where key field values are found (inspired by: https://sebastianraschka.com/Articles/2014_sqlite_in_python_tutorial.html)
        c.execute('UPDATE {tn} SET {f}="{fv}" WHERE {kf}="{kfv}"'.format(tn=TableName, f=Field, fv=FieldValue, kf=KeyField, kfv=KeyFieldValue))

    except:
        raise IOError()

    # Closing the connection to the database file
    ConnectedDatabase.commit()
    ConnectedDatabase.close()

#if __name__ == '__main__':

