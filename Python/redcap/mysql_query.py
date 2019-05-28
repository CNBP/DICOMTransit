# ----------------------------------------------------------------------------------------------------------------------
#  mysql_query.py
# ----------------------------------------------------------------------------------------------------------------------

# ----------------------------------------------------------------------------------------------------------------------
#  Imports
# ----------------------------------------------------------------------------------------------------------------------

import mysql.connector
from mysql.connector.cursor import MySQLCursorPrepared
from redcap.constants import mysql_export_host, mysql_export_port, mysql_export_database, mysql_export_user, mysql_export_password
from redcap.enums import MySQLType
from redcap.transaction import RedcapTransaction
from itertools import groupby
import logging
import sys

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logger = logging.getLogger(__name__)


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

        # If table name is valid, otherwise show a warning.
        if not tablename == "unknown":
            create_mysql_table(tablename, tablefields)
        else:
            logger.info('Warning! : An unknown table name detected')

    # Get entries to create.  (Group by table name - get_mysql_tablename return the tablename to use)
    entrieslist = groupby(transaction.redcap_queue, lambda f: get_mysql_tablename(transaction.redcap_metadata, f[0]))

    # For each table - (insert entries/lines).
    for tablename, entries in entrieslist:

        # If table name is valid.
        if not tablename == "unknown":
            insert_mysql_entries(tablename, entries)

    # Return success.
    return True, "All data in queue has been sent to MySQL."


def get_mysql_tablename(metadata: list, entries: dict) -> str:
    """
    Get the line tablename. (For the entries) (If there is no redcap_repeat_instrument then it will look inside the redcap_metadata.
    :param metadata: List of fields (metadata inside redcap)
    :param entries: List of fields (Line to insert inside mysql with fieldname.)
    :return: tablename.
    """

    # Check if there is a redcap_repeat_instrument inside the line to insert.
    redcap_repeat_instrument = entries.get("redcap_repeat_instrument")

    # If there is a redcap_repeat_instrument then we need to return the value.
    if redcap_repeat_instrument is not None:
        return redcap_repeat_instrument

    # If the last field inside entries is complete then it's the tablename. ( <tablename>_complete )
    lastfieldname = list(entries.items())[-1][0]
    if "complete" in lastfieldname:
        return lastfieldname.replace("_complete", "")

    # For each field in metadata.
    for field in metadata:

        # For each fields inside the entries/fields (the line to insert)
        listentries = [(k,v) for k,v in entries.items()]
        for entry in reversed(listentries):

            # If the entry dictionary contains the field name. (field[0] = fieldname)
            if field[0] == entry[0]:

                # Then we need to return the current table name. (field[3] = tablename)
                return field[3]

    # We don't know what is the current table.
    return "unknown"


def prepare_mysql_metadata_stage5(transaction: RedcapTransaction) -> RedcapTransaction:
    """
    Prepare mysql metadata. (Stage 5)
    *** Sometime some metadata are missing. Ex : Stage 4 is adding caseid, motherid etc and metadata is not updated.
    This fonction will add the missing metadata to allow us to export all the data to mysql.
    :param transaction: RedcapTransaction (Stage 4)
    :return: Updated RedcapTransaction (stage 5)
    """

    # Get entries to create.  (Group by table name - get_mysql_tablename return the tablename to use)
    entrieslist_redcap_queue = groupby(transaction.redcap_queue, lambda f: get_mysql_tablename(transaction.redcap_metadata, f[0]))

    # For each table - (insert entries/lines).
    for tablename_redcap_queue, entries_redcap_queue in entrieslist_redcap_queue:

        # Get the list of metadata for a specific tablename - x[3] is the tablename.
        table_redcap_metadata = [x for x in transaction.redcap_metadata if x[3] == tablename_redcap_queue]

        # For each entries / lines to add inside the database.
        for fields in entries_redcap_queue:

            # For each field we need to check if it's already inside the metadata.
            for fieldname, fieldvalue in fields[0].items():

                # Preparing vars.
                found = False

                # For each field inside the current metadata, check if the field already exist.
                for field in table_redcap_metadata:

                    # If this is the current field that we are looking for. (Flag found to true and exit loop)
                    if field[0] == fieldname:
                        found = True
                        break

                # If not found, then we need to add metadata.
                if found == False:
                    data = [fieldname, convert_redcap_to_mysql_fieldtype("text"), fieldname, tablename_redcap_queue]
                    table_redcap_metadata.append(data)
                    transaction.redcap_metadata.append(data)

    # We need to order the redcap_metadata using tablename - f[3]
    # Otherwise group will not work.
    transaction.redcap_metadata = sorted(transaction.redcap_metadata, key=lambda f: f[3])

    # Return the updated repcap transaction (stage 5)
    return transaction


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

        # If it's not the first element then we need to add a separator.
        if not first:
            query += ", "

        # Add field and flag not as the first one.
        query += convert_redcap_to_mysql_fieldname(tablename, field[0]) + " " + convert_redcap_to_mysql_fieldtype(field[1])
        first = False

    # Close SQL query.
    query += ");"

    # Connecting to MySQL database.
    conn = mysql.connector.connect(host=mysql_export_host, port=mysql_export_port, database=mysql_export_database, user=mysql_export_user, password=mysql_export_password)
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
    conn = mysql.connector.connect(host=mysql_export_host, port=mysql_export_port, database=mysql_export_database, user=mysql_export_user, password=mysql_export_password, use_pure=True)

    # For each entries / lines to add inside the database.
    for fields in entries:

        # Prepare vars.
        first = True
        query = "INSERT INTO " + tablename + " ("
        queryvalues = ""

        # For each element inside the dictionary.
        for fieldname, fieldvalue in fields[0].items():

            # If not the first one, then we need to add separator.
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
        mysql_cursor.execute(query, tuple(fields[0][key] for key in fields[0].keys()))

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
    # Otherwise we will not be able to remove the useless name in the field like - [tablename_]
    # because mst is not there.
    #
    # We need to transform order to position and system to systems, otherwise mysql request will crash.
    # (It will think it's a mysql parameter)

    if tablename.startswith("mst"):
        return fieldname.replace(tablename[3:] + "_", "").replace("order", "position").replace("system", "system_")
    else:
        return fieldname.replace(tablename + "_", "").replace("order", "position").replace("system", "system_")


def wipe_all_mysql_data() -> None:
    """
    Delete all MySQL data.
    :return: None
    """

    # Deleting old MySQL database SQL request.
    select_statement = ("DROP DATABASE IF EXISTS " + mysql_export_database + ";")

    # Connecting to MySQL database.
    conn = mysql.connector.connect(host=mysql_export_host, port=mysql_export_port, user=mysql_export_user, password=mysql_export_password)
    mysql_cursor = conn.cursor()

    # Execute MySQL request.
    mysql_cursor.execute(select_statement)

    # Creating new database.
    select_statement = ("CREATE DATABASE " + mysql_export_database + ";")

    # Execute MySQL request.
    mysql_cursor.execute(select_statement)
    conn.commit()
