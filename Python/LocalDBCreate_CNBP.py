#This file create a SQLite local database for CNBP requirement.
#Creation: 2018-07-11T160228EST
#Author: Yang Ding

import sys
import os
import sqlite3
import logging
from pathlib import Path
import argparse
import getpass

def LocalDBCreate_CNBP():

    logging.basicConfig(stream=sys.stdout, level=logging.INFO)
    logger = logging.getLogger('upload_bom')

    # name of the sqlite database file
    sqliteFile = '..\LocalDB\LocalDB_CNBPs.sqlite'

    #If SQL already exist, quit script.
    SQLPath = Path(sqliteFile)
    if SQLPath.is_file():
        #logger.info('SQLite database file already exist. Not gonna mess with it!')
        #quit()

        '''Delete current database! During testing only'''
        os.remove(sqliteFile)
        logger.info('DEBUG: database file already exist. Deleted it!')


    # name of the table to be created
    tableName = 'id_table'


    #Create the PRIMARY KEY column.
    new_field = 'DBKEY'
    field_type = 'INTEGER'  # column data type

    #Create the variable array that store the columns information to be used later in loop for column creation
    newColumns = ['MRN','CNBPID','CNNID','CNFUNID','Hash1','Hash2','Hash3']
    newColumnsTypes = ['INTEGER', 'TEXT', 'INTEGER', 'INTEGER', 'TEXT', 'TEXT', 'TEXT']
    newColumnSpec = zip(newColumns, newColumnsTypes)
    newColumnSpecList = list(newColumnSpec)

    # Create on Connecting to the database file
    ConnectedDatabase = sqlite3.connect(sqliteFile)

    c = ConnectedDatabase.cursor()

    logger.info('Creating PRIMARY KEY DBKEY column in database.')

    # Creating a new SQLite table with DBKey column (inspired by: https://sebastianraschka.com/Articles/2014_sqlite_in_python_tutorial.html)
    c.execute('CREATE TABLE {tn} ({nf} {ft} PRIMARY KEY)'.format(tn=tableName, nf=new_field, ft=field_type))

    logger.info('PRIMARY KEY DBKEY column successfully created in database.')

    logger.info('Creating secondary columns in database.')

    # Adding accessory columns via a loop
    for column in newColumnSpecList:
        c.execute("ALTER TABLE {tn} ADD COLUMN '{cn}' {ct}".format(tn=tableName, cn=column[0], ct=column[1]))
    logger.info('Secondary columns created in database.')

    # Committing changes and closing the connection to the database file
    ConnectedDatabase.commit()
    ConnectedDatabase.close()

#Only executed when running directly.
if __name__ == '__main__':
    LocalDBCreate_CNBP()