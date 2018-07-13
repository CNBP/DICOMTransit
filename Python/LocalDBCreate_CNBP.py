#This file create a SQLite local database for CNBP requirement.
#Creation: 2018-07-11T160228EST
#Author: Yang Ding


import sqlite3
import logging
from pathlib import Path

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logger = logging.getLogger('upload_bom')

sqliteFile = '..\LocalDB\LocalDB_CNBPs.sqlite'    # name of the sqlite database file

# name of the table to be created
tableName = 'id_table'


#Create the PRIMARY KEY column.
new_field = 'DBKEY'
field_type = 'INTEGER'  # column data type

#Create the MRN column.
new_field1 = 'MNR' # name of the column
field_type1 = 'CHAR(10)'  # column data type

#Create the CNBPID column
new_field2 = 'CNBPID' # name of the column
field_type2 = 'CHAR(50)'  # column data type

#Create the CNBPID column
new_field3 = 'CNNID' # name of the column
field_type3 = 'CHAR(12)'  # column data type

new_field4 = 'CNFUNID' # name of the column
field_type4 = 'CHAR(12)'  # column data type

new_field5 = 'Hash_MotherMRN' # name of the column
field_type5 = 'CHAR(20)'  # column data type


#If SQL already exist, quit script.
SQLPath = Path(sqliteFile)
if SQLPath.is_file():
    logger.info('SQLite database file already exist. Not gonna mess with it!')
    quit()


# Create on Connecting to the database file
ConnectedDatabase = sqlite3.connect(sqliteFile)



c = ConnectedDatabase.cursor()

# Creating a new SQLite table with 1 column

CommandString = 'CREATE TABLE' tablename ()

c.execute('CREATE TABLE {tn} ({nf} {ft})'.format(tn=tableName, nf=new_field, ft=field_type))

CREATE TABLE `Sfasdf` (
	`Test`	INTEGER,
	`Field2`	TEXT,
	PRIMARY KEY(`Test`)
);

# Creating a second table with 1 column and set it as PRIMARY KEY
# note that PRIMARY KEY column must consist of unique values!

#c.execute('CREATE TABLE {tn} ({nf} {ft} PRIMARY KEY)'.format(tn=table_name2, nf=new_field, ft=field_type))

# Committing changes and closing the connection to the database file
ConnectedDatabase.commit()
ConnectedDatabase.close()
