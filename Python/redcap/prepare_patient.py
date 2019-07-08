# ----------------------------------------------------------------------------------------------------------------------
#  Imports
# ----------------------------------------------------------------------------------------------------------------------

from redcap.common import process_field
from redcap.constants import *
from redcap.enums import Field
from redcap.local_odbc import (
    get_case_ids,
    get_database_column_names,
    get_data_rows_for_patient_table,
    get_primary_key_name,
)
from redcap.query import get_fields
from redcap.transaction import RedcapTransaction
from LocalDB.API import set_CNNIDs, get_CNBP

import sys
import logging


# ----------------------------------------------------------------------------------------------------------------------
#  Prepare Patient Data
# ----------------------------------------------------------------------------------------------------------------------

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logger = logging.getLogger(__name__)


def prepare_patient_tables(transaction: RedcapTransaction) -> RedcapTransaction:
    """
    Creates REDCap records for of all patient tables and adds them to the global queue (only for each hospital record
    number loaded).
    :param transaction: RedcapTransaction
    :return: RedcapTransaction
    """

    # For each hospital record number
    for index_hospital_record_number in range(len(transaction.hospital_record_numbers)):

        # Set hospital record number.
        transaction.set_hospital_record_number(index_hospital_record_number)

        # Set any additional id that has a 1 to 1 relationship with the hospital record number.
        transaction.set_cnbp_id(get_CNBP(transaction.HospitalRecordNumber))

        # Get all case ids related to this Hospital Record Number
        cases = get_case_ids(transaction)

        # If no data was retrieved from the database, skip.
        if cases is None:
            return

        # Record caseIDs
        set_CNNIDs(transaction.HospitalRecordNumber, cases)

        # For each case related to this Hospital Record Number
        for index_case in range(len(cases)):

            # Set case id.
            transaction.set_case_id(cases[index_case])

            process_case(transaction)

    return transaction


def process_case(transaction: RedcapTransaction) -> None:
    """
    Process a case.
    :param transaction: RedcapTransaction
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


def process_table(index_table, transaction: RedcapTransaction) -> None:
    """
    Process each patient table.
    :param index_table: Index of current table
    :param transaction: RedcapTransaction
    :return: None
    """

    table_configuration = transaction.data_import_configuration

    # Get current table redcap fields.
    current_table_redcap_fields = get_fields(
        table_configuration[index_table][REDCAP_FORM_NAME], transaction
    )

    # Get database columns list.
    database_column_list = get_database_column_names(
        table_configuration[index_table], transaction
    )

    # Get all data for this case in this patient table
    rows = get_data_rows_for_patient_table(
        table_configuration[index_table], transaction
    )

    # If no data were retrieved from the database, skip.
    if rows is None:
        return

    # For each row of data retrieved from the database
    for index_row in range(len(rows)):

        process_row(
            current_table_redcap_fields,
            database_column_list,
            index_row,
            index_table,
            rows,
            transaction,
        )


def process_row(
    current_table_redcap_fields,
    database_column_list,
    index_row,
    index_table,
    rows,
    transaction,
) -> None:
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
    if (
        index_row == 0
        and table_configuration[index_table][AUTHORITY_ON_IDS] is not None
    ):
        # Set all case related ids that the current table has authority on
        set_case_related_ids(
            database_column_list, index_row, index_table, rows, transaction
        )

    # Create a blank dictionary.
    record_text = {}

    # If the current table is the table holding additional ids having a 1 to 1 relationship
    # with the hospital record number.
    if (
        table_configuration[index_table][DATABASE_TABLE_NAME].lower()
        == redcap_form_holding_ids_directly_linked_to_hospital_record_numbers
    ):
        # Add any additional id that has a 1 to 1 relationship with the hospital record number.
        record_text["cnbpid"] = transaction.CNBPId

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
        record_text[redcap_repeat_instrument_key_name] = table_configuration[
            index_table
        ][REDCAP_FORM_NAME].lower()
        record_text[redcap_repeat_instance_key_name] = str(index_row + 1)

    # For each REDCap field in this table
    for index_field in range(len(current_table_redcap_fields)):

        process_field(
            index_field,
            current_table_redcap_fields,
            database_column_list,
            index_row,
            record_text,
            rows,
        )

    # Mark this table entry as 'complete'.
    redcap_complete_status_key_name = (
        table_configuration[index_table][REDCAP_FORM_NAME].lower()
        + redcap_complete_status_suffix
    )
    record_text[redcap_complete_status_key_name] = redcap_complete_status_value

    # Add this item to the REDCap queue.
    transaction.add_redcap_queue(
        record_text, table_configuration[index_table][REDCAP_PROJECT]
    )


def set_case_related_ids(
    database_column_list, index_row, index_table, rows, transaction
) -> None:
    """
    This function will set all case related ids that the current table has authority on
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
