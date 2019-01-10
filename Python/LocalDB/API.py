from LocalDB.query import LocalDB_query
from LocalDB.schema import CNBP_blueprint
from LORIS.validate import LORIS_validation
import logging
import sys
from PythonUtils.env import load_validate_dotenv
from settings import get
from PythonUtils.math import int_incrementor


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


def get_setting(setting_name: str):
    """
    Used to access the dtconfigure.sqlite database to retrieve the settings necessary for most other operations.
    :param setting_name: assumed the string already exist. Prior method need to check that.
    :return:
    """
    from LocalDB.query import LocalDB_query
    from LocalDB.schema import configuration_blueprint
    from PythonUtils.env import validate_dotenv_var
    from datetime import datetime

    # Load env on where the setting database is located.
    path_config_database = load_validate_dotenv("config_database", configuration_blueprint.dotenv_variables) # Default location to dtconfigure.sqlite
    name_config_table = load_validate_dotenv("config_table", configuration_blueprint.dotenv_variables)  # Default location to dtconfigure.sqlite

    # Look for setting variable in the DEFAULT ORDER
    success, records_setting = LocalDB_query.get_all(path_config_database, name_config_table, setting_name)
    assert success
    assert len(records_setting) > 0

    # Ensure that timestamp is still a relevant field in the table. Cross validate against blueprint.
    assert validate_dotenv_var("created", configuration_blueprint.fields)

    # Retrieve TIMESTAMP of all records. in the DEFAULT ORDER
    success, records_timestamp = LocalDB_query.get_all(path_config_database, name_config_table, "created")
    assert success
    assert len(records_timestamp) > 0

    # Find the index of the record that has the latest timepoint.
    list_datetime = []
    for record in records_timestamp:
        record_time = datetime.strptime(record[0],"%Y-%m-%d %H:%M:%S")
        list_datetime.append(record_time)
    timestamp_latest = max(list_datetime)
    index_timestamp_latest = list_datetime.index(timestamp_latest)

    # in that row, retrieve setting.
    setting_value = records_setting[index_timestamp_latest][0]

    return setting_value


if __name__ == "__main__":
    propose_CNBPID("GregoryLodygensky012 Study")
