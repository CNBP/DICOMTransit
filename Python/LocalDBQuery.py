import sys
import os
import argparse
import getpass
import logging
import sqlite3
from pathlib import Path

logging.basicConfig(stream=sys.stdout, level=logging.INFO)


def CheckValue(database_path, table_name, ColumnName, ColumnValue):
    '''
    Check if a subject exist in the given database and given table
    :param database_path: path to the SQLite database
    :param table_name: the name of the table being queried
    :param ColumnName: the column being queried
    :param ColumnValue: the value of the column being checked
    :return: boolean on if this is ever found in the given database in the given table, in the given column.
    '''
    logger = logging.getLogger('LORISQuery_CheckSubjectExist')

    # if SQL already exist, quit script.
    SQLPath = Path(database_path)

    # check if path is a file and exist.
    if not SQLPath.is_file():
        logger.info('SQLite database file does not exist!')
        return False

    #Try to connect the database to start the process:
    try:
        # Create on Connecting to the database file
        ConnectedDatabase = sqlite3.connect(database_path)
        c = ConnectedDatabase.cursor()

        logger.info('Creating PRIMARY KEY DBKEY column in database.')

        # Creating a new SQLite table_name with DBKey column (inspired by: https://sebastianraschka.com/Articles/2014_sqlite_in_python_tutorial.html)
        c.execute('SELECT * FROM {table_name} WHERE {columnname}="{columnvalue}"'.format(table_name=table_name, columnname=ColumnName, columnvalue=ColumnValue))

        result_rows = c.fetchall()

    except:
        raise IOError()

    # Closing the connection to the database file
    ConnectedDatabase.close()

    if len(result_rows) > 0:
        return True, result_rows
    else:
        return False, result_rows


def CreateEntry(database_path, table_name, key_field, key_field_value):
    '''
    A general function to create entries into the database BY providing the name of the KEYValue field and KEYvalue value to be created
    Note it MUST be the keyfield.
    :param database_path: path to the database
    :param table_name: name of the table
    :param key_field: KeyFiled in the table to be created
    :param key_field_value: value of the key_field to be created. 
    :return: if the entry has been successfully created.
    '''
    logger = logging.getLogger('LORISQuery_CreateSubject')

    # if SQL already exist, quit script.
    SQLPath = Path(database_path)

    # check if path is a file and exist.
    if not SQLPath.is_file():
        logger.info('SQLite database file does not exist!')
        return False

    # Try to connect the database to start the process:
    try:
        # Create on Connecting to the database file
        ConnectedDatabase = sqlite3.connect(database_path)
        c = ConnectedDatabase.cursor()

        logger.info('Creating new record in SQLite database.')

        # Creating a new SQLite record row (inspired by: https://sebastianraschka.com/Articles/2014_sqlite_in_python_tutorial.html)
        c.execute('INSERT OR IGNORE INTO {tn} ({field}) VALUES ("{value}")'.format(tn=table_name, field=key_field, value=key_field_value))
    except:
        raise IOError()

    # Closing the connection to the database file
    ConnectedDatabase.commit()
    ConnectedDatabase.close()
    return True


def UpdateEntry(database_path, table_name, key_field, key_field_value, field, field_value):
    '''
    A general function to create entries into the database BY providing the name of the KEYValue field and KEYvalue value to be created
    :param database_path:
    :param table_name:
    :param key_field:
    :param key_field_value:
    :param field:
    :param field_value:
    :return:
    '''

    logger = logging.getLogger('LORISQuery_CreateSubject')

    # if SQL already exist, quit script.
    SQLPath = Path(database_path)

    # check if path is a file and exist.
    if not SQLPath.is_file():
        logger.info('SQLite database file does not exist!')
        return False

    # Try to connect the database to start the process:
    try:
        # Create on Connecting to the database file
        ConnectedDatabase = sqlite3.connect(database_path)
        c = ConnectedDatabase.cursor()

        logger.info('Update records in SQLite database.')

        # Update SQLite record row where key field values are found (inspired by: https://sebastianraschka.com/Articles/2014_sqlite_in_python_tutorial.html)
        c.execute('UPDATE {tn} SET {f}="{fv}" WHERE {kf}="{kfv}"'.format(tn=table_name, f=field, fv=field_value, kf=key_field, kfv=key_field_value))

    except:
        raise IOError()

    # Closing the connection to the database file
    ConnectedDatabase.commit()
    ConnectedDatabase.close()

#if __name__ == '__main__':

