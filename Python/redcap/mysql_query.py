# ----------------------------------------------------------------------------------------------------------------------
#  MySQLQuery.py
# ----------------------------------------------------------------------------------------------------------------------

# ----------------------------------------------------------------------------------------------------------------------
#  Imports
# ----------------------------------------------------------------------------------------------------------------------

import mysql.connector
from mysql.connector.cursor import MySQLCursorPrepared
from redcap.constants import mysql_export_host, mysql_export_database, mysql_export_user, mysql_export_password
from redcap.enums import MySQLType
from redcap.transaction import RedcapTransaction
from itertools import groupby


def send_mysql_data(transaction: RedcapTransaction) -> (bool, str):
    """
    Sends all records in the queue to mysql.
    :return: Successful or not and reason
    """

    # If there is at least one record in the queue waiting to be sent to REDCap
    if not len(transaction.redcap_queue) > 0:
        return False, "MySQL queue is empty."

    # Get table list to create. (Group by table name - Position [3] is the tablename.)
    tablelist = groupby(transaction.redcap_metadata, lambda f: f[3])

    # For each table - (create table).
    for tablename, tablefields in tablelist:
        create_mysql_table(tablename, tablefields)

    # Get entries to create.  (Group by table name - redcap_repeat_instrument is the tablename.)
    entrieslist = groupby(transaction.redcap_queue, lambda f: f[0]["redcap_repeat_instrument"])

    # For each table - (insert entries/lines).
    for tablename, entries in entrieslist:
        insert_mysql_entries(tablename, entries)

    # Return success.
    return True, "All data in queue has been sent to MySQL."


def create_mysql_table(tablename: str, tablefields: iter) -> None:
    """
    Insert all entries to a table.
    :param tablename: Table name to create.
    :param tablefields: List of the table fields to create. (Dictionary)
    :return: None
    """

    # Prepare vars.
    first = True
    query = "CREATE TABLE " + tablename + " ("

    # For each fields inside the table.
    for field in tablefields:

        # Ignore masterid field.
        if(field[0] == "masterid"):
            continue

        # If it's not the first element then we need to add a separator.
        if not first:
            query += ", "

        # Add field and flag not as the first one.
        query += convert_redcap_to_mysql_fieldname(tablename, field[0]) + " " + convert_redcap_to_mysql_fieldtype(field[1])
        first = False

    # Close SQL query.
    query += ");"

    # Connecting to MySQL database.
    conn = mysql.connector.connect(host=mysql_export_host, database=mysql_export_database, user=mysql_export_user, password=mysql_export_password)
    mysql_cursor = conn.cursor()

    # Execute MySQL request.
    mysql_cursor.execute(query)
    conn.commit()


def insert_mysql_entries(tablename: str, entries: iter) -> None:
    """
    Insert all entries to a table.
    :param tablename: Table name to do the insert.
    :param entries: List of entries to add. (Dictionary)
    :return: None
    """

    # Connecting to MySQL database.
    # Take note here that we need to use Pure to allow us to use prepare statement.
    conn = mysql.connector.connect(host=mysql_export_host, database=mysql_export_database, user=mysql_export_user, password=mysql_export_password, use_pure=True)

    # For each entries / lines to add inside the database.
    for fields in entries:

        # Prepare vars.
        first = True
        query = "INSERT INTO " + tablename + " ("
        queryvalues = ""

        # Filter dictionary field ( We need to remove useless field )
        valid_fields = {fieldname: fieldvalue for (fieldname, fieldvalue) in fields[0].items() if (fieldname != "masterid" and not fieldname.startswith("mst") and not fieldname.startswith("redcap_"))}

        # For each element inside the dictionary.
        for fieldname, fieldvalue in valid_fields.items():

            # If not the first one, then we need to add separattor.
            if not first:
                query += ", "
                queryvalues += ", "

            # Add field and flag next field not as a first one.
            query += convert_redcap_to_mysql_fieldname(tablename, fieldname) + " "
            queryvalues += "? "
            first = False

        # Add values to the end of the query.
        query += ") VALUES (" + queryvalues + ");"

        # Prepared statement
        mysql_cursor = conn.cursor(cursor_class=MySQLCursorPrepared)

        # Execute MySQL request.
        mysql_cursor.execute(query, tuple(valid_fields[key] for key in valid_fields.keys()))

    # Commit all changes.
    conn.commit()


def convert_redcap_to_mysql_fieldtype(fieldtype: str) -> str:
    """
    Convert redcap to mysql field type.
    :param fieldtype: Field type name in redcap database.
    :return: The MySQL field type to use.
    """

    # The MySQL field type to use.
    if fieldtype == MySQLType.yesno.name:
        return MySQLType.yesno.value
    elif fieldtype == MySQLType.text.name:
        return MySQLType.text.value
    elif fieldtype == MySQLType.textprimary.name:
        return MySQLType.textprimary.value
    else:
        return MySQLType.unknown.value


def convert_redcap_to_mysql_fieldname(tablename: str, fieldname: str) -> str:
    """
    Convert redcap to mysql field name.
    :param tablename: Table name inside the database.
    :param fieldname: Field name inside the redcap database.
    :return: The MySQL fieldname to use.
    """

    # If table name start with mst then we need to remove mst.
    # Otherwise we will not be able to remove the useless name in the field like - [tablename_] because mst is not there.
    if tablename.startswith("mst"):
        return fieldname.replace(tablename[3:] + "_", "").replace("order", "position")
    else:
        return fieldname.replace(tablename + "_", "").replace("order", "position")


def wipe_all_mysql_data() -> None:
    """
    Delete all MySQL data.
    :return: None
    """

    # Deleting old MySQL database SQL request.
    select_statement = ("DROP DATABASE IF EXISTS " + mysql_export_database + ";")

    # Connecting to MySQL database.
    conn = mysql.connector.connect(host=mysql_export_host, user=mysql_export_user, password=mysql_export_password)
    mysql_cursor = conn.cursor()

    # Execute MySQL request.
    mysql_cursor.execute(select_statement)

    # Creating new database.
    select_statement = ("CREATE DATABASE " + mysql_export_database + ";")

    # Execute MySQL request.
    mysql_cursor.execute(select_statement)
    conn.commit()
