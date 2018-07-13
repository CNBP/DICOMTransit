from LocalDBQuery import CheckSubjectExist
from LocalDBCreate_CNBP import LocalDBCreate_CNBP
import sqlite3
from pathlib import Path
import logging
import os
import sys

logging.basicConfig(stream=sys.stdout, level=logging.INFO)

#def test_LocalDBQuery():
logger = logging.getLogger('UT_LocalDBQuery')
PathString = "TestCNBPQuery.sqlite"

# if SQL already exist, quit script.
SQLPath = Path(PathString)

# check if path is a file and exist.
if SQLPath.is_file():
    logger.info('Test SQLite database file already exist. Gonna mess with it!')
    ''''Delete current database! During testing only'''
    os.remove(PathString)

# Create the database
assert LocalDBCreate_CNBP(PathString)
logger.info('Test SQLite database successfully created. Gonna mess with it!')

tableName = 'id_table'  # All CNBP database should have this table name.
MRNColumn = "MRN"
CNBPIDColumn = "CNBPID"

# Populate the table with some fake records.
conn = sqlite3.connect(PathString)
c = conn.cursor()
c.execute("INSERT INTO {tn} ({mrn},{cnbpid}) VALUES (291010,'CNBP0010001')".format(tn=tableName, mrn=MRNColumn, cnbpid=CNBPIDColumn))
c.execute("INSERT INTO {tn} ({mrn},{cnbpid}) VALUES (292010,'CNBP0020001')".format(tn=tableName, mrn=MRNColumn, cnbpid=CNBPIDColumn))
c.execute("INSERT INTO {tn} ({mrn},{cnbpid}) VALUES (295010,'CNBP0010001')".format(tn=tableName, mrn=MRNColumn,
                                                                                   cnbpid=CNBPIDColumn))
c.execute("INSERT INTO {tn} ({mrn},{cnbpid}) VALUES (29710,'CNBP0030001')".format(tn=tableName, mrn=MRNColumn,
                                                                                   cnbpid=CNBPIDColumn))
c.execute("INSERT INTO {tn} ({mrn},{cnbpid}) VALUES (291310,'CNBP0510001')".format(tn=tableName, mrn=MRNColumn,
                                                                                 cnbpid=CNBPIDColumn))
conn.commit()
conn.close()

logger.info('Test SQLite database successfully inserted with mock records. Gonna mess with it!')

# Create on Connecting to the database file
assert(CheckSubjectExist(PathString, tableName, "MRN", 291010))
assert(CheckSubjectExist(PathString, tableName, "CNBPID", "CNBP0010001"))

#return True