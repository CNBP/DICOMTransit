import sqlite3

from LocalDB.query import LocalDB_query
from LocalDB.schema import CNBP_blueprint
from LORIS.validate import LORIS_validation
import logging
import sys
from PythonUtils.env import load_validate_dotenv
from PythonUtils.math import int_incrementor
from redcap import development as environment

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logger = logging.getLogger(__name__)


def get_list_MRN():
    """
    Return a list_return of all MRN from the database.
    :return:
    """
    # Load local database from .env file
    database_path = load_validate_dotenv("LocalDatabasePath", CNBP_blueprint.dotenv_variables)

    list_MRN = []

    success, result_rows = LocalDB_query.get_all(database_path, CNBP_blueprint.table_name, "MRN")

    for row in result_rows:
        list_MRN.append(row[0]) # MRN is the first variable requested.

    return list_MRN #todo: verify this is in integer? or string as that has dire consequences.


def check_MRN(MRN):
    """
    Return true if the MRN exist within the current database
    :return:
    """

    # Load local database from .env file
    database_path = load_validate_dotenv("LocalDatabasePath", CNBP_blueprint.dotenv_variables)


    # Store MRN in database.
    MRN_exist_in_database, _ = LocalDB_query.check_value(database_path,
                                                         CNBP_blueprint.table_name,
                                                         CNBP_blueprint.keyfield,
                                                         MRN)
    if MRN_exist_in_database:
        logger.info("MRN found to exist at local database")
    return MRN_exist_in_database


def create_MRN(MRN):
    database_path = load_validate_dotenv("LocalDatabasePath", CNBP_blueprint.dotenv_variables)

    # Create the MRN record
    LocalDB_query.create_entry(database_path, CNBP_blueprint.table_name, CNBP_blueprint.keyfield, MRN)


def get_CNBP(MRN):
    """
    Assuming the MRN exist, get the CNBPID.
    :param MRN: the MRN to look for
    :return: the CNBPID associated with that particular MRN number.
    """
    # Load local database from .env file
    database_path = load_validate_dotenv("LocalDatabasePath", CNBP_blueprint.dotenv_variables)
    MRN_exist_in_database, KeyRecords = LocalDB_query.check_value(database_path,
                                                                  CNBP_blueprint.table_name,
                                                                  CNBP_blueprint.keyfield,
                                                                  MRN)
    if MRN_exist_in_database is False:
        return None

    assert(len(KeyRecords) == 1)
    cnbp_header_index = LocalDB_query.check_header_index(database_path, CNBP_blueprint.table_name, 'CNBPID')
    return KeyRecords[cnbp_header_index]


def get_DCCID(MRN):
    """
    Assuming the MRN exist, get the MRNID.
    :param MRN: the MRN to look for
    :return: the CNBPID associated with that particular MRN number.
    """
    # Load local database from .env file
    database_path = load_validate_dotenv("LocalDatabasePath",CNBP_blueprint.dotenv_variables)
    MRN_exist_in_database, KeyRecords = LocalDB_query.check_value(database_path,
                                                                  CNBP_blueprint.table_name,
                                                                  CNBP_blueprint.keyfield,
                                                                  MRN)
    if MRN_exist_in_database is False:
        return None

    assert(len(KeyRecords) == 1)
    dcc_header_index = LocalDB_query.check_header_index(database_path, CNBP_blueprint.table_name, 'DCCID')

    return KeyRecords[dcc_header_index]


def get_timepoint(MRN):
    """
    Assuming the MRN exist, get the MRNID.
    :param MRN: the MRN to look for
    :return: the CNBPID associated with that particular MRN number.
    """
    # Load local database from .env file
    database_path = load_validate_dotenv("LocalDatabasePath",CNBP_blueprint.dotenv_variables)
    MRN_exist_in_database, KeyRecords = LocalDB_query.check_value(database_path,
                                                                  CNBP_blueprint.table_name,
                                                                  CNBP_blueprint.keyfield,
                                                                  MRN)
    if MRN_exist_in_database is False:
        return None

    assert(len(KeyRecords) == 1)
    timepoint_header_index = LocalDB_query.check_header_index(database_path, CNBP_blueprint.table_name, 'Timepoint')

    return KeyRecords[timepoint_header_index]


def get_scan_date(MRN):
    """
    Assuming the MRN exist, get the MRNID.
    :param MRN: the MRN to look for
    :return: the CNBPID associated with that particular MRN number.
    """
    # Load local database from .env file
    database_path = load_validate_dotenv("LocalDatabasePath", CNBP_blueprint.dotenv_variables)
    MRN_exist_in_database, KeyRecords = LocalDB_query.check_value(database_path,
                                                                  CNBP_blueprint.table_name,
                                                                  CNBP_blueprint.keyfield,
                                                                  MRN)
    if MRN_exist_in_database is False:
        return None

    assert(len(KeyRecords) == 1)
    date_header_index = LocalDB_query.check_header_index(database_path, CNBP_blueprint.table_name, 'Date')
    scan_date = KeyRecords[0][date_header_index]
    return scan_date


def set_CNBP(MRN: int, CNBPID):
    """
    Update record with proper CNBPID which has particular MRN
    :param MRN:
    :return:
    """
    database_path = load_validate_dotenv("LocalDatabasePath", CNBP_blueprint.dotenv_variables)

    # Update the MRN record with CNBPID
    LocalDB_query.create_entry(database_path, CNBP_blueprint.table_name, CNBP_blueprint.keyfield, MRN)
    LocalDB_query.update_entry(database_path, CNBP_blueprint.table_name, CNBP_blueprint.keyfield, MRN, "CNBPID", CNBPID, )


def set_DCCID(MRN: int, DCCID):
    """
    Update record with proper DCCID which has particular MRN
    :param MRN:
    :return:
    """
    database_path = load_validate_dotenv("LocalDatabasePath", CNBP_blueprint.dotenv_variables)

    # Update the MRN record with DCCID
    LocalDB_query.update_entry(database_path, CNBP_blueprint.table_name, CNBP_blueprint.keyfield, MRN, "DCCID", DCCID, )


def set_scan_date(MRN: int, scan_date: str):
    """
    Update record with proper scan time which has particular MRN
    :param MRN:
    :return:
    """
    database_path = load_validate_dotenv("LocalDatabasePath", CNBP_blueprint.dotenv_variables)

    # Update the MRN record with Timepoint
    LocalDB_query.update_entry(database_path, CNBP_blueprint.table_name, CNBP_blueprint.keyfield, MRN, "Date",
                               scan_date)


def set_timepoint(MRN: int, Timepoint: str):
    """
    Update record with proper Timepoint which has particular MRN
    :param MRN:
    :return:
    """
    database_path = load_validate_dotenv("LocalDatabasePath", CNBP_blueprint.dotenv_variables)

    # Update the MRN record with Timepoint
    LocalDB_query.update_entry(database_path, CNBP_blueprint.table_name, CNBP_blueprint.keyfield, MRN, "Timepoint", Timepoint)


def propose_CNBPID(DICOM_protocol: str):
    """
    This function takes in a string that is representative of the DICOM acquisition study protocol, and propose a CNBPID composed of two parts:
        Institution_ID (from the .env configuration file)
        Project_ID (inferred from the protocol and incremented
        SubjectCount (kept track by localDB.
    :param DICOM_protocol:
    :return:
    """
    # Get and retrieve  institution_ID
    InstitionID = load_validate_dotenv("institutionID", CNBP_blueprint.dotenv_variables)

    import DICOM.API
    # Check ProjectID string and then return the ProjectID;
    ProjectID = DICOM.API.study_validation(DICOM_protocol)

    # Use those two pieces of information to form a partial query pattern that can run on the SQLite
    partial_search_input = InstitionID + ProjectID

    DB_path = load_validate_dotenv("LocalDatabasePath", CNBP_blueprint.dotenv_variables)

    # Partial match search records: (currently has SQL error).
    success, matched_records = LocalDB_query.check_partial_value(DB_path, CNBP_blueprint.table_name, "CNBPID", partial_search_input)

    # Default subject ID when no match is found.
    latest_subject_ID = "0000001"

    if matched_records is None or len(matched_records) == 0:
        # no previous subjects found. Use default value.
        pass
    else:
        latest_subject_ID = check_all_existing_records(matched_records)

    # Combined all the parts to return the proposed CNBPID

    proposed_CNBPID = InstitionID + ProjectID + latest_subject_ID

    return proposed_CNBPID


def check_all_existing_records(matched_records):
    """
    Check the list of records past, find the maximum subject ID and then return the new proposed SubjectID
    :param matched_records:
    :return:
    """
    max_subject_ID = 0

    # Loop through all subjects belong to this project and ensure that we can track the latest subjects number.
    for matched_record in matched_records:
        CNBPID_schema_index: int = CNBP_blueprint.schema.index("CNBPID")
        CNBPID = matched_record[CNBPID_schema_index]

        # Skip non-compliance records
        if not LORIS_validation.validate_CNBPID(CNBPID):
            logger.info(
                "A non-compliant record has been found in the existing SQLite database, you might want to look into that. ")
            logger.info(
                "Will ignore this record and try not to infer subject ID from it as it is not reliable potentially due to following OLD SCHEMA.")
            continue

        # store as INT for the last 4 digits of the string.
        current_subject_ID = int(CNBPID[:4])

        # Should the currentID number be bigger than the anticipated, one,
        if current_subject_ID > max_subject_ID:
            max_subject_ID = current_subject_ID

    assert(0 < max_subject_ID < 10000)

    subjectID: str = str(max_subject_ID)

    incremented_subjectID = int_incrementor(subjectID)

    # return the zero leading int.
    return incremented_subjectID


def load_hospital_record_numbers(use_predefined: bool):
    """
    A wrapper function of get_list_MRN which allow static loading of a predefined list of all hospital record numbers
    for which we want to transfer data to REDCap by utilizing API calls.
    :return: List of hospital record numbers (MRNs)
    """
    return_list = []

    if not use_predefined:
        # Get the numbers from a dynamic source:
        return_list = get_list_MRN()
    else:
        # Get the numbers from a static source:
        return_list = [
            3143750,
            3144235,
            3147383,
            3149523,
            3152931,
            3153280,
            3154386,
            3154822,
            3156430,
            3160223,
            3161091,
            3161116,
            3161146,
            3162999,
            3163000,
            3163509,
            3163750,
            3165201,
            3165984,
            3166489,
            3170659,
            3171022,
            3172805,
            3173436,
            3174439,
            3176163,
            3178972,
            3181830,
            3187252,
            3190535,
            3191237,
            3191976,
            3193639,
            3202977,
            2404933
        ]
    return return_list


if __name__ == "__main__":

    propose_CNBPID("GregoryLodygensky012 Study")
