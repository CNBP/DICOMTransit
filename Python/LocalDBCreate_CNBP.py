#This file create a SQLite local database for CNBP requirement.
#Creation: 2018-07-11T160228EST
#Author: Yang Ding

from LocalDBCreate import LocalDBCreate

def LocalDBCreate_CNBP(Path):

    # name of the TableName to be created
    TableName = 'id_table'

    #Create the PRIMARY KEY column.
    KeyField = 'MRN'

    #Create the variable array that store the columns information to be used later in loop for column creation
    NewColumns = ['CNBPID', 'CNNID', 'CNFUNID', 'Hash1', 'Hash2', 'Hash3']
    NewColumnsTypes = ['TEXT', 'INTEGER', 'INTEGER', 'TEXT', 'TEXT', 'TEXT']
    NewColumnSpec = zip(NewColumns, NewColumnsTypes)
    NewColumnSpecList = list(NewColumnSpec)

    return LocalDBCreate(Path, TableName, KeyField, NewColumnSpecList)

# Only executed when running directly.
if __name__ == '__main__':
    LocalDBCreate_CNBP("..\LocalDB\LocalDB_CNBPs.sqlite")