# This file database a SQLite local database for CNBP requirement.
# Creation: 2018-07-11T160228EST
# Author: Yang Ding

from dotenv import load_dotenv
from LocalDB.create import LocalDB_create
from settings import config_get
from LocalDB.schema import CNBP_blueprint


class LocalDB_createCNBP:
    @staticmethod
    def database(Path):

        # name of the TableName to be created

        # Create the PRIMARY KEY column.

        # Create the variable array that store the columns information to be used later in loop for column creation
        TableName = CNBP_blueprint.table_name
        KeyField = CNBP_blueprint.keyfield
        NewColumns = CNBP_blueprint.fields
        NewColumnsTypes = CNBP_blueprint.fields_types

        NewColumnSpec = zip(NewColumns, NewColumnsTypes)
        NewColumnSpecList = list(NewColumnSpec)

        return LocalDB_create.database(Path, TableName, KeyField, NewColumnSpecList)


# Only executed when running directly.
if __name__ == "__main__":
    # Mini script used to create the initial database

    localDB_path = config_get("LocalDatabasePath")
    assert localDB_path is not None
    assert localDB_path != ""
    LocalDB_createCNBP.database(localDB_path)
