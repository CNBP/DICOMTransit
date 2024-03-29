import logging
import sqlite3
from pathlib import Path
from DICOMTransit.LocalDB.schema import CNBP_blueprint

logger = logging.getLogger()


class LocalDB_query:

    """
    Lower level functions that interact with the local database.
    """

    @staticmethod
    def check_value(database_path, table_name, ColumnName, ColumnValue) -> (bool, list):
        """
        Check if a subject exist in the given database and given table
        :param database_path: path to the SQLite database
        :param table_name: the name of the table being queried
        :param ColumnName: the column being queried
        :param ColumnValue: the value of the column being checked
        :return: boolean on if this is ever found in the given database in the given table, in the given column.
        """

        SQLPath = Path(database_path)

        # check if path is a file and exist.
        if not SQLPath.is_file():
            logger.warning("SQLite database file does not exist!")
            return False, None

        # Try to connect the database to start the process:
        try:
            # Create on Connecting to the database file
            ConnectedDatabase = sqlite3.connect(database_path)
            c = ConnectedDatabase.cursor()

            logger.debug(
                f"Checking key value: {str(ColumnValue)} in {ColumnName} in SQLite database."
            )

            # Creating a new SQLite table_name with DBKey column (inspired by: https://sebastianraschka.com/Articles/2014_sqlite_in_python_tutorial.html)
            execution_string = (
                f'SELECT * FROM {table_name} WHERE {ColumnName}="{ColumnValue}"'
            )
            c.execute(execution_string)

            result_rows = c.fetchall()

        except Exception as e:
            logger.info(e)
            raise IOError()

        # Closing the connection to the database file
        ConnectedDatabase.close()

        if len(result_rows) > 0:
            return True, result_rows
        else:
            return False, result_rows

    @staticmethod
    def check_partial_value(database_path, table_name, ColumnName, ColumnValue):
        """
        Check if a subject exist in the given database and given table
        :param database_path: path to the SQLite database
        :param table_name: the name of the table being queried
        :param ColumnName: the column being queried
        :param ColumnValue: the value of the column being checked
        :return: boolean on if this is ever found in the given database in the given table, in the given column.
        """

        SQLPath = Path(database_path)

        # check if path is a file and exist.
        if not SQLPath.is_file():
            logger.info("SQLite database file does not exist!")
            return False, None

        # Try to connect the database to start the process:
        try:
            # Create on Connecting to the database file
            ConnectedDatabase = sqlite3.connect(database_path)
            c = ConnectedDatabase.cursor()

            logger.debug(
                f"Checking key value: {str(ColumnValue)} in {ColumnName} in SQLite database."
            )

            # Creating a new SQLite table_name with DBKey column (inspired by: https://sebastianraschka.com/Articles/2014_sqlite_in_python_tutorial.html)
            execution_string = (
                f'SELECT * FROM {table_name} WHERE {ColumnName} LIKE "%{ColumnValue}%"'
            )
            c.execute(execution_string)

            result_rows = c.fetchall()

        except Exception as e:
            logger.info(e)
            raise IOError()

        # Closing the connection to the database file
        ConnectedDatabase.close()

        if len(result_rows) > 0:
            return True, result_rows
        else:
            return False, result_rows

    @staticmethod
    def create_entry(database_path, table_name, key_field, key_field_value):
        """
        A general function to database entries into the database BY providing the name of the KEYValue field and KEYvalue value to be created
        Note it MUST be the keyfield.
        :param database_path: path to the database
        :param table_name: name of the table
        :param key_field: KeyFiled in the table to be created
        :param key_field_value: value of the key_field to be created.
        :return: if the entry has been successfully created.
        """

        # if SQL already exist, quit script.
        SQLPath = Path(database_path)

        # check if path is a file and exist.
        if not SQLPath.is_file():
            logger.error("SQLite database file does not exist!")
            return False

        # Try to connect the database to start the process:
        try:
            # Create on Connecting to the database file
            ConnectedDatabase = sqlite3.connect(database_path)
            c = ConnectedDatabase.cursor()

            logger.info("Creating new record in SQLite database.")

            # Creating a new SQLite record row (inspired by: https://sebastianraschka.com/Articles/2014_sqlite_in_python_tutorial.html)
            c.execute(
                f'INSERT OR IGNORE INTO {table_name} ({key_field}) VALUES ("{key_field_value}")'
            )
        except Exception as e:
            logger.info(e)
            raise IOError()

        # Closing the connection to the database file
        ConnectedDatabase.commit()
        ConnectedDatabase.close()
        return True

    @staticmethod
    def update_entry(
        database_path, table_name, key_field, key_field_value, field, field_value
    ):
        """
        A general function to database entries into the database BY providing the name of the KEYValue field and KEYvalue value to be created
        :param database_path:
        :param table_name:
        :param key_field:
        :param key_field_value:
        :param field:
        :param field_value:
        :return:
        """

        # if SQL already exist, quit script.
        SQLPath = Path(database_path)

        # check if path is a file and exist.
        if not SQLPath.is_file():
            logger.error("SQLite database file does not exist!")
            return False

        # Try to connect the database to start the process:
        try:
            # Create on Connecting to the database file
            ConnectedDatabase = sqlite3.connect(database_path)
            c = ConnectedDatabase.cursor()

            logger.info(
                f"Updating records in SQLite database {table_name} table {field} for the record."
            )

            # Update SQLite record row where key field values are found (inspired by: https://sebastianraschka.com/Articles/2014_sqlite_in_python_tutorial.html)
            c.execute(
                f"UPDATE {table_name} SET {field}= ? WHERE {key_field}= ?",
                (field_value, key_field_value),
            )

        except Exception as e:
            pass

        # Closing the connection to the database file
        ConnectedDatabase.commit()
        ConnectedDatabase.close()

    @staticmethod
    def check_header(database_path, table_name):
        """
        Finds the table, connect to it, and then return the header.
        :param database_path:
        :param table_name:
        :return:
        """

        table_header = None

        try:
            # Create on Connecting to the database file
            ConnectedDatabase = sqlite3.connect(database_path)

            c = ConnectedDatabase.cursor()
            c.execute("PRAGMA TABLE_INFO({})".format(table_name))

            table_header = c.fetchall()

            ConnectedDatabase.commit()
            ConnectedDatabase.close()

            return table_header  # zero indexed, LIST class of tuple of 5 elements.

        except IOError as e:
            logger.info(e)
            return table_header

    @staticmethod
    def check_header_index(database_path, table_name, field):
        """
        Parse the list of the header and then check it against the field provided to return the index.
        :param database_path:
        :param table_name:
        :param field:
        :return:
        """

        try:
            header_list = LocalDB_query.check_header(
                database_path, table_name
            )  # header list is a list of 5 elements tuples.

            if header_list is not None:
                global header_index
                for table_column in header_list:
                    if table_column[1] == field:  # 1 is field name.
                        global header_index
                        header_index = table_column[0]  # 0 is the index
                        break
                return header_index
        except IOError:
            return None

    @staticmethod
    def validateLocalTableAndSchema(database_path, table_name, field):
        """
        Does a comprehensitve check to ensure the field, 1) exist in the schema, 2) exist in the local table and then are the SAME!
        :param database_path:
        :param table_name:
        :param field: the string of the field name that is to be searched.
        :return:
        """

        field_table_index = -1
        field_schema_index = -2

        # Schema check: note that schema contains keyfield
        if field not in CNBP_blueprint.schema:
            return False, f"Current planned schema does not contain {field}"
        else:
            field_schema_index = CNBP_blueprint.schema.index(field)

        # Table header check: table also must contain keyfield
        try:
            field_table_index = LocalDB_query.check_header_index(
                database_path, table_name, field
            )
            if field_table_index is None:
                return False, f"SQLite table HEADER does not contain {field}"
            else:
                logger.debug(
                    f"SQLite table HEADER for the field {field } is {str(field_table_index)}"
                )
        except IOError:
            return False, "Database not reachable"

        if field_table_index < 0 or field_schema_index < 0:
            return False, "Check program for bugs. Default values not modified"

        # This ensure we checking the right column for field information by validating against both schema and table.
        if field_table_index != field_schema_index:
            return False, "Schema & Table definition not matching"

        return (
            True,
            "Database and Schema congruently support this field and its position",
        )

    @staticmethod
    def get_all(database_path, table_name, field_names):

        SQLPath = Path(database_path)

        # check if path is a file and exist.
        if not SQLPath.is_file():
            logger.error("SQLite database file does not exist!")
            return False, None

        # Try to connect the database to start the process:
        try:
            # Create on Connecting to the database file
            ConnectedDatabase = sqlite3.connect(database_path)
            c = ConnectedDatabase.cursor()

            # logger.info("Checking key value: " + str(ColumnValue) + " in " + ColumnName + " in SQLite database.")

            # Creating a new SQLite table_name with DBKey column (inspired by: https://sebastianraschka.com/Articles/2014_sqlite_in_python_tutorial.html)
            execution_string = f"SELECT {field_names} FROM {table_name}"
            c.execute(execution_string)

            result_rows = c.fetchall()

        except Exception as e:
            logger.info(e)
            raise IOError()

        # Closing the connection to the database file
        ConnectedDatabase.close()

        if len(result_rows) > 0:
            return True, result_rows
        else:
            return False, result_rows


# if __name__ == '__main__':
