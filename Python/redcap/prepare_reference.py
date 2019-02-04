# ----------------------------------------------------------------------------------------------------------------------
#  Imports
# ----------------------------------------------------------------------------------------------------------------------

from redcap.constants import *
from redcap.local_odbc import get_database_column_names, get_data_rows_for_reference_table, get_primary_key_name
from redcap.query import get_fields
from redcap.transaction import RedcapTransaction

import sys
import logging


# ----------------------------------------------------------------------------------------------------------------------
#  Prepare Reference
# ----------------------------------------------------------------------------------------------------------------------

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logger = logging.getLogger(__name__)

def prepare_reference_tables(transaction: RedcapTransaction):
    """
    Creates REDCap records for of all reference tables and adds them to the global queue.
    :return: None
    """
    table_configuration = transaction.data_import_configuration

    # REDCAP_PROJECT, DATABASE_TABLE_NAME, DATABASE,
    #primary_key_name, primary_key_value, authority_on_ids, , redcap_form_name

    # For each table in the import configuration matrix
    for index_table in range(len(table_configuration)):

        # Process table which update the transaction.redcap_queue
        process_table(index_table, transaction)

    return transaction


def process_table(index_table, transaction: RedcapTransaction):
    """
    Process each reference table
    :param index_table:
    :param transaction: the transaction content to be updated.
    :return:
    """
    table_configuration = transaction.data_import_configuration

    # If the current table is set to be imported
    if not table_configuration[index_table][IS_IMPORT_ENABLED]:
        return

    # If the current table is a reference table
    if not table_configuration[index_table][IS_REFERENCE_TABLE]:
        return

    # Get current table redcap fields.
    current_table_redcap_fields = get_fields(table_configuration[index_table][REDCAP_FORM_NAME], transaction)

    # Get database columns list.
    database_column_list = get_database_column_names(table_configuration[index_table], transaction)

    # Get all the data contained in this table.
    rows = get_data_rows_for_reference_table(table_configuration[index_table])

    # For each row of data in this table
    for index_row in range(len(rows)):

        process_row(current_table_redcap_fields, database_column_list, index_row, index_table, rows, transaction)


def process_row(current_table_redcap_fields, database_column_list, index_row, index_table, rows, transaction):
    """
    Process each each reference row.
    :param current_table_redcap_fields:
    :param database_column_list:
    :param index_row:
    :param index_table:
    :param rows:
    :param transaction: the transaction content to be updated.
    :return:
    """

    table_configuration = transaction.data_import_configuration

    # Create a blank dictionary. Add the ID (always 1 for a reference table)
    record_text = {get_primary_key_name(table_configuration[index_table][PRIMARY_KEY_NAME]).lower(): str(1)}



    # Set repeatable data (if applicable).
    if table_configuration[index_table][IS_REPEATABLE_INSTRUMENT] == 1:
        record_text[redcap_repeat_instrument_key_name] = table_configuration[index_table][
            REDCAP_FORM_NAME].lower()
        record_text[redcap_repeat_instance_key_name] = str(index_row + 1)

    # For each REDCap field in this table
    for current_field in range(len(current_table_redcap_fields)):

        process_field(current_field, current_table_redcap_fields, database_column_list, index_row, record_text, rows)

    # Mark this table entry as 'complete'.
    redcap_complete_status_key_name = table_configuration[index_table][REDCAP_FORM_NAME].lower() + \
                                      redcap_complete_status_suffix
    record_text[redcap_complete_status_key_name] = redcap_complete_status_value

    # Add this item to the REDCap queue.
    transaction.add_redcap_queue(record_text, table_configuration[index_table][REDCAP_PROJECT])


def process_field(current_field, current_table_redcap_fields, database_column_list, index_row, record_text, rows):
    """
    Process the field of the row within the reference table.
    :param current_field:
    :param current_table_redcap_fields:
    :param database_column_list:
    :param index_row:
    :param record_text:
    :param rows:
    :return:
    """
    try:
        # 0 is for redcap field_label
        position_in_database_table = \
            database_column_list.index(current_table_redcap_fields[current_field][0])

        if str(rows[index_row][position_in_database_table]) == 'False':
            value = '0'
        elif str(rows[index_row][position_in_database_table]) == 'True':
            value = '1'
        elif str(rows[index_row][position_in_database_table]) == 'None':
            value = ''
        else:
            value = str(rows[index_row][position_in_database_table])

        # 1 is for redcap field_name
        record_text[current_table_redcap_fields[current_field][1]] = str(value)

    except ValueError:
        logger.info("issue encountered when dealing with...") # fixme: add details of the bugs encountered.
        pass
