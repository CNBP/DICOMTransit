#This file create a SQLite local database for CNBP requirement.
#Creation: 2018-07-11T160228EST
#Author: Yang Ding

import os
from dotenv import load_dotenv
from LocalDB_create import LocalDBCreate
import LocalDB_schema

def create_localDB_CNBP(Path):

    # name of the TableName to be created


    #Create the PRIMARY KEY column.


    load_dotenv()

    username = os.getenv("LORISusername")
    password = os.getenv("LORISpassword")

    # Create the variable array that store the columns information to be used later in loop for column creation
    TableName = LocalDB_schema.CNBP_schema_table_name
    KeyField = LocalDB_schema.CNBP_schema_keyfield
    NewColumns = LocalDB_schema.CNBP_schema_fields
    NewColumnsTypes = LocalDB_schema.CNBP_schema_fields_types

    NewColumnSpec = zip(NewColumns, NewColumnsTypes)
    NewColumnSpecList = list(NewColumnSpec)

    return LocalDBCreate(Path, TableName, KeyField, NewColumnSpecList)

# Only executed when running directly.
if __name__ == '__main__':
    create_localDB_CNBP("..\LocalDB\LocalDB_CNBPs.sqlite")