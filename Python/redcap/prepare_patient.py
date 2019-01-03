from redcap import globalvars
from redcap.enums import Field
from redcap.constants import redcap_repeat_instrument_key_name, redcap_repeat_instance_key_name, \
    redcap_complete_status_suffix, redcap_complete_status_value
from redcap.initialization import initialize_ids
from redcap.local_odbc import get_database_column_names, get_data_rows_for_patient_table, get_primary_key_name
from redcap.query import get_redcap_fields, add_record_to_redcap_queue


table_configuration = globalvars.data_import_configuration

# Setting index in the table_configuration
IS_IMPORT_ENABLED = 1
IS_REFERENCE_TABLE = 2
REDCAP_PROJECT = 3
DATABASE_TABLE_NAME = 4
DATABASE = 5
PRIMARY_KEY_NAME = 6
PRIMARY_KEY_VALUE = 7
AUTHORITY_ON_IDS = 8
IS_REPEATABLE_INSTRUMENT = 9
REDCAP_FORM_NAME = 10


def prepare_patient_tables():
    """
    Creates REDCap records for of all patient tables and adds them to the global queue (only for each hospital record
    number loaded).
    :return: None
    """
    # For each hospital record number
    for index_hospital_record_number in range(len(globalvars.hospital_record_numbers)):

        # Initialize ids.
        initialize_ids(globalvars.hospital_record_numbers[index_hospital_record_number])

        process_record()

    return


def process_record():
    """
    Process each patient record.
    :return:
    """
    # For each table in the import configuration matrix
    for index_table in range(len(table_configuration)):

        # If the current table is set to be imported, return
        if not table_configuration[index_table][IS_IMPORT_ENABLED]:
            return

        if not table_configuration[index_table][IS_REFERENCE_TABLE]:
            return

        process_table(index_table)

    pass


def process_table(index_table):
    """
    Process each patient table.
    :param index_table:
    :return:
    """
    # Get current table redcap fields.
    current_table_redcap_fields = get_redcap_fields(table_configuration[index_table][REDCAP_FORM_NAME])

    # Get database columns list.
    database_column_list = get_database_column_names(table_configuration[index_table])

    # Get all data for this patient in this table
    rows = get_data_rows_for_patient_table(table_configuration[index_table])

    # If no data were retrieved from the database, skip.
    if rows is None:
        return

    # For each row of data retrieved from the database
    for index_row in range(len(rows)):

        process_row(current_table_redcap_fields, database_column_list, index_row, index_table, rows)


def process_row(current_table_redcap_fields, database_column_list, index_row, index_table, rows):
    """
    Process each row of the current table for the current MRN.
    :param current_table_redcap_fields:
    :param database_column_list:
    :param index_row:
    :param index_table:
    :param rows:
    :return:
    """

    # If this is the first row of data and the current table has authority on any ids
    if index_row == 0 and table_configuration[index_table][AUTHORITY_ON_IDS] is not None:
        set_field_id(database_column_list, index_row, index_table, rows)

    # Create a blank dictionary.
    record_text = {}

    # Add the ID
    pk_for_filter = table_configuration[index_table][PRIMARY_KEY_NAME]
    pk_for_value = table_configuration[index_table][PRIMARY_KEY_VALUE]

    if pk_for_value == Field.BabyId.value:
        record_text[get_primary_key_name(pk_for_filter).lower()] = globalvars.BabyId
    elif pk_for_value == Field.CaseId.value:
        record_text[get_primary_key_name(pk_for_filter).lower()] = globalvars.CaseId
    elif pk_for_value == Field.CNNPatientUI.value:
        record_text[Field.PatientId.name.lower()] = globalvars.PatientId
    elif pk_for_value == Field.HospitalRecordNumber.value:
        # Special Case: We do not save the Hospital Record Number in REDCap.
        # Instead, we save the CaseId.'
        record_text[Field.CaseId.name.lower()] = globalvars.CaseId
    elif pk_for_value == Field.MotherId.value:
        record_text[get_primary_key_name(pk_for_filter).lower()] = globalvars.MotherId
    elif pk_for_value == Field.PatientId.value:
        record_text[get_primary_key_name(pk_for_filter).lower()] = globalvars.PatientId
    elif pk_for_value == Field.PatientUI.value:
        record_text[Field.PatientId.name.lower()] = globalvars.PatientId
    elif pk_for_value == Field.MasterId.value:
        record_text[get_primary_key_name(pk_for_filter).lower()] = globalvars.MasterId

    # Set repeatable data (if applicable).
    if table_configuration[index_table][IS_REPEATABLE_INSTRUMENT]:
        record_text[redcap_repeat_instrument_key_name] = \
            table_configuration[index_table][
                REDCAP_FORM_NAME].lower()
        record_text[redcap_repeat_instance_key_name] = str(index_row + 1)

    # For each REDCap field in this table
    for current_field in range(len(current_table_redcap_fields)):

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

            pass

    # Mark this table entry as 'complete'.
    redcap_complete_status_key_name = table_configuration[index_table][REDCAP_FORM_NAME].lower() + \
                                      redcap_complete_status_suffix
    record_text[redcap_complete_status_key_name] = redcap_complete_status_value

    # Add this item to the REDCap queue.
    add_record_to_redcap_queue(record_text, table_configuration[index_table][REDCAP_PROJECT])


def set_field_id(database_column_list, index_row, index_table, rows):

    for index in range(len(table_configuration[index_table][AUTHORITY_ON_IDS])):

        pk = table_configuration[index_table][AUTHORITY_ON_IDS][index]

        position = database_column_list.index(get_primary_key_name(pk))

        if pk == Field.BabyId.value:
            globalvars.BabyId = str(rows[index_row][position])
        elif pk == Field.CaseId.value:
            globalvars.CaseId = str(rows[index_row][position])
        elif pk == Field.CNNPatientUI.value:
            globalvars.CNNPatientUI = str(rows[index_row][position])
        elif pk == Field.HospitalRecordNumber.value:
            globalvars.HospitalRecordNumber = str(rows[index_row][position])
        elif pk == Field.MotherId.value:
            globalvars.MotherId = str(rows[index_row][position])
        elif pk == Field.PatientId.value:
            globalvars.PatientId = str(rows[index_row][position])
        elif pk == Field.PatientUI.value:
            globalvars.PatientUI = str(rows[index_row][position])
        elif pk == Field.MasterId.value:
            globalvars.MasterId = str(rows[index_row][position])

