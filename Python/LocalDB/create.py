import sys
import sqlite3
import logging
from pathlib import Path
from LocalDB.schema import CNBP_blueprint

# This file database a SQLite local database for CNBP requirement.
# Creation: 2018-07-11T160228EST
# Author: Yang Ding


logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logger = logging.getLogger('database')

class LocalDB_create:

    @staticmethod
    def database(PathString, TableName, KeyFieldString, ColumnsNameTypeList):
        """
        Create the local database based on schema.
        :param PathString:
        :param TableName:
        :param KeyFieldString:
        :param ColumnsNameTypeList:
        :return:
        """


        # if SQL already exist, quit script.
        SQLPath = Path(PathString)

        # check if path is a fiela nd exist.
        if SQLPath.is_file():
            logger.debug('SQLite database file already exist. Not gonna mess with it!')
            return False
        '''Delete current database! During testing only'''
        '''os.remove(sqliteFile)
        logger.info('DEBUG: database file already exist. Deleted it!')'''

        #Create the PRIMARY KEY column.
        KeyFieldType = CNBP_blueprint.keyfield_type  # column data type

        #Try to connect the database to start the process:

        try:
            # Create on Connecting to the database file
            ConnectedDatabase = sqlite3.connect(PathString)

            c = ConnectedDatabase.cursor()

            logger.debug('Creating PRIMARY KEY DBKEY column in database.')

            # Creating a new SQLite table with DBKey column (inspired by: https://sebastianraschka.com/Articles/2014_sqlite_in_python_tutorial.html)
            c.execute('CREATE TABLE {tn} ({nf} {ft} PRIMARY KEY)'.format(tn=TableName, nf=KeyFieldString, ft=KeyFieldType))

            logger.debug('PRIMARY KEY DBKEY column successfully created in database.')

            logger.debug('Creating secondary columns in database.')

            # Adding accessory columns via a loop
            for column in ColumnsNameTypeList:
                if (column[1] != "TEXT" and
                    column[1] != "REAL" and
                    column[1] != "BLOB" and
                    #column[1] != "NULL" and
                    column[1] != "INTEGER"):
                    continue  # skip iteration is the data type is not specified properly.
                else:
                    c.execute("ALTER TABLE {tn} ADD COLUMN '{cn}' {ct}".format(tn=TableName, cn=column[0], ct=column[1]))

            logger.debug('Secondary columns created in database.')

            # Committing changes and closing the connection to the database file
            ConnectedDatabase.commit()
            ConnectedDatabase.close()
        except Exception as e:
            logger.info(e)
            logger.warning('SQLite database creation/update issue, suspect schema non-compliant SQLite database. Did you corrupt this SQLite database somehow?')
            raise IOError
        return True
