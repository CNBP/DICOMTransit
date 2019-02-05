# ----------------------------------------------------------------------------------------------------------------------
#  Imports
# ----------------------------------------------------------------------------------------------------------------------

from redcap.enums import Field
from redcap.constants import *
from redcap.local_odbc import get_database_column_names, get_data_rows_for_patient_table, get_primary_key_name
from redcap.query import get_fields
from redcap.transaction import RedcapTransaction


# ----------------------------------------------------------------------------------------------------------------------
#  Prepare Patient
# ----------------------------------------------------------------------------------------------------------------------

def prepare_patient_tables(transaction: RedcapTransaction):
    """
    Creates REDCap records for of all patient tables and adds them to the global queue (only for each hospital record
    number loaded).
    :return: RedcapTransaction
    """

    # For each hospital record number
    for index_hospital_record_number in range(len(transaction.hospital_record_numbers)):

        # Initialize ids.
        transaction.initialize_ids(index_hospital_record_number)

        process_record(transaction)

    return transaction


def process_record(transaction: RedcapTransaction):
    """
    Process each patient record.
    :return: None
    """

    table_configuration = transaction.data_import_configuration

    # For each table in the import configuration matrix
    for index_table in range(len(table_configuration)):

        # If the current table IS NOT set to be imported, return
        if not table_configuration[index_table][IS_IMPORT_ENABLED]:
            return

        # If the current table IS a reference table
        if table_configuration[index_table][IS_REFERENCE_TABLE]:
            return

        process_table(index_table, transaction)

    pass


def process_table(index_table, transaction: RedcapTransaction):
    """
    Process each patient table.
    :param index_table: Index of current table
    :param transaction: RedcapTransaction
    :return: None
    """

    table_configuration = transaction.data_import_configuration

    # Get current table redcap fields.
    current_table_redcap_fields = get_fields(table_configuration[index_table][REDCAP_FORM_NAME], transaction)

    # Get database columns list.
    database_column_list = get_database_column_names(table_configuration[index_table], transaction)

    # Get all data for this patient in this table
    rows = get_data_rows_for_patient_table(table_configuration[index_table], transaction)

    # If no data were retrieved from the database, skip.
    if rows is None:
        return

    # For each row of data retrieved from the database
    for index_row in range(len(rows)):

        process_row(current_table_redcap_fields, database_column_list, index_row, index_table, rows, transaction)


def process_row(current_table_redcap_fields, database_column_list, index_row, index_table, rows, transaction):
    """
    Process each row of the current table for the current MRN.
    :param current_table_redcap_fields: Current table REDCap fields
    :param database_column_list: Database columns list
    :param index_row: Index of current row
    :param index_table: Index of current table
    :param rows: All data contained in current table
    :param transaction: RedcapTransaction
    :return: None
    """

    table_configuration = transaction.data_import_configuration

    # If this is the first row of data and the current table has authority on any ids
    if index_row == 0 and table_configuration[index_table][AUTHORITY_ON_IDS] is not None:
        set_field_id(database_column_list, index_row, index_table, rows, transaction)

    # Create a blank dictionary.
    record_text = {}

    # Add the ID
    pk_for_filter = table_configuration[index_table][PRIMARY_KEY_NAME]
    pk_for_value = table_configuration[index_table][PRIMARY_KEY_VALUE]

    if pk_for_value == Field.BabyId.value:
        record_text[get_primary_key_name(pk_for_filter).lower()] = transaction.BabyId
    elif pk_for_value == Field.CaseId.value:
        record_text[get_primary_key_name(pk_for_filter).lower()] = transaction.CaseId
    elif pk_for_value == Field.CNNPatientUI.value:
        record_text[Field.PatientId.name.lower()] = transaction.PatientId
    elif pk_for_value == Field.HospitalRecordNumber.value:
        # Special Case: We do not save the Hospital Record Number in REDCap.
        # Instead, we save the CaseId.'
        record_text[Field.CaseId.name.lower()] = transaction.CaseId
    elif pk_for_value == Field.MotherId.value:
        record_text[get_primary_key_name(pk_for_filter).lower()] = transaction.MotherId
    elif pk_for_value == Field.PatientId.value:
        record_text[get_primary_key_name(pk_for_filter).lower()] = transaction.PatientId
    elif pk_for_value == Field.PatientUI.value:
        record_text[Field.PatientId.name.lower()] = transaction.PatientId
    elif pk_for_value == Field.MasterId.value:
        record_text[get_primary_key_name(pk_for_filter).lower()] = transaction.MasterId

    # Set repeatable data (if applicable).
    if table_configuration[index_table][IS_REPEATABLE_INSTRUMENT]:
        record_text[redcap_repeat_instrument_key_name] = table_configuration[index_table][REDCAP_FORM_NAME].lower()
        record_text[redcap_repeat_instance_key_name] = str(index_row + 1)

    # For each REDCap field in this table
    for index_field in range(len(current_table_redcap_fields)):

        try:

            # 0 is for redcap field_label
            position_in_database_table = \
                database_column_list.index(current_table_redcap_fields[index_field][0])

            if str(rows[index_row][position_in_database_table]) == 'False':
                value = '0'
            elif str(rows[index_row][position_in_database_table]) == 'True':
                value = '1'
            elif str(rows[index_row][position_in_database_table]) == 'None':
                value = ''
            else:
                value = str(rows[index_row][position_in_database_table])

            # 1 is for redcap field_name
            record_text[current_table_redcap_fields[index_field][1]] = str(value)

        except ValueError:

            pass

    # Mark this table entry as 'complete'.
    redcap_complete_status_key_name = table_configuration[index_table][REDCAP_FORM_NAME].lower() + \
                                      redcap_complete_status_suffix
    record_text[redcap_complete_status_key_name] = redcap_complete_status_value

    # Add this item to the REDCap queue.
    transaction.add_redcap_queue(record_text, table_configuration[index_table][REDCAP_PROJECT])


def set_field_id(database_column_list, index_row, index_table, rows, transaction):
    """
    :param database_column_list: Database columns list
    :param index_row: Index of current row
    :param index_table: Index of current table
    :param rows: All data contained in current table
    :param transaction: RedcapTransaction
    :return: None
    """

    table_configuration = transaction.data_import_configuration

    for index in range(len(table_configuration[index_table][AUTHORITY_ON_IDS])):

        pk = table_configuration[index_table][AUTHORITY_ON_IDS][index]

        position = database_column_list.index(get_primary_key_name(pk))

        if pk == Field.BabyId.value:
            transaction.BabyId = str(rows[index_row][position])
        elif pk == Field.CaseId.value:
            transaction.CaseId = str(rows[index_row][position])
        elif pk == Field.CNNPatientUI.value:
            transaction.CNNPatientUI = str(rows[index_row][position])
        elif pk == Field.HospitalRecordNumber.value:
            transaction.HospitalRecordNumber = str(rows[index_row][position])
        elif pk == Field.MotherId.value:
            transaction.MotherId = str(rows[index_row][position])
        elif pk == Field.PatientId.value:
            transaction.PatientId = str(rows[index_row][position])
        elif pk == Field.PatientUI.value:
            transaction.PatientUI = str(rows[index_row][position])
        elif pk == Field.MasterId.value:
            transaction.MasterId = str(rows[index_row][position])
