import sys
import os
import argparse
import getpass
import logging
import sqlite3
from pathlib import Path

logging.basicConfig(stream=sys.stdout, level=logging.INFO)

def CheckSubjectExist(DatabasePath, Table, ColumnName, ColumnValue):
    logger = logging.getLogger('')

    # if SQL already exist, quit script.
    SQLPath = Path(DatabasePath)

    # check if path is a fiel and exist.
    if not SQLPath.is_file():
        logger.info('SQLite database file does not exist!')
        return False

    #Try to connect the database to start the process:
    try:
        # Create on Connecting to the database file
        ConnectedDatabase = sqlite3.connect(DatabasePath)
        c = ConnectedDatabase.cursor()

        logger.info('Creating PRIMARY KEY DBKEY column in database.')

        # Creating a new SQLite table with DBKey column (inspired by: https://sebastianraschka.com/Articles/2014_sqlite_in_python_tutorial.html)
        c.execute('SELECT * FROM {tablename} WHERE {columnname}="{columnvalue}"'.format(tablename=Table, columnname=ColumnName, columnvalue=ColumnValue))

        ResultRows = c.fetchall()
    except:
        raise IOError()

    # Closing the connection to the database file
    ConnectedDatabase.close()

    if len(ResultRows) > 0:
        return True
    else:
        return False

#def CreateSubject(database, table, CNBPID)

#if __name__ == '__main__':

