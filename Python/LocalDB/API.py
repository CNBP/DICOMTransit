from LocalDB.query import LocalDB_query
from LocalDB.schema import CNBP_blueprint
from LORIS.validate import LORIS_validation
import logging
import sys
import os
from settings import config_get
from PythonUtils.env import load_dotenv_var
from PythonUtils.intmath import int_incrementor
from typing import List
import json

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logger = logging.getLogger(__name__)




def check_status():
    from settings import config_get
    # Load local database from .env file
    database_path = config_get("LocalDatabasePath")

    if not os.path.isfile(database_path):
        return False

    # Get the name from the blueprint.
    tableName = CNBP_blueprint.table_name  # All CNBP database should have this table name.

    # do a quick header check.
    fetchallResult = LocalDB_query.check_header(database_path, tableName)

    # If the table is valid, it should have MORE than one header... I HOPE?
    if len(fetchallResult) > 0:
        return True
    else:
        return False



def get_list_MRN():
    """
    Return a list_return of all MRN from the database.
    :return:
    """
    # Load local database from .env file
    database_path = config_get("LocalDatabasePath")


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
    database_path = config_get("LocalDatabasePath")


    # Store MRN in database.
    MRN_exist_in_database, _ = LocalDB_query.check_value(database_path,
                                                         CNBP_blueprint.table_name,
                                                         CNBP_blueprint.keyfield,
                                                         MRN)
    if MRN_exist_in_database:
        logger.info("MRN found to exist at local database")
    return MRN_exist_in_database


def create_MRN(MRN):
    database_path = config_get("LocalDatabasePath")

    # Create the MRN record
    LocalDB_query.create_entry(database_path, CNBP_blueprint.table_name, CNBP_blueprint.keyfield, MRN)


def get_CNBP(MRN):
    """
    Assuming the MRN exist, get the CNBPID.
    :param MRN: the MRN to look for
    :return: the CNBPID associated with that particular MRN number.
    """
    # Load local database from .env file
    database_path = config_get("LocalDatabasePath")
    MRN_exist_in_database, KeyRecords = LocalDB_query.check_value(database_path,
                                                                  CNBP_blueprint.table_name,
                                                                  CNBP_blueprint.keyfield,
                                                                  MRN)
    if MRN_exist_in_database is False:
        return None

    # Only ONE record per MRN.
    assert(len(KeyRecords) == 1)
    cnbp_header_index = LocalDB_query.check_header_index(database_path, CNBP_blueprint.table_name, 'CNBPID')

    return KeyRecords[0][cnbp_header_index]


def get_seriesUID(MRN: int) -> List[str]:
    """
    Assuming the MRN exist, get the SeriesUID of all scans that ever past through here.
    :param MRN: the MRN to look for
    :return: the CNBPID associated with that particular MRN number.
    """
    # Load local database from .env file
    database_path = config_get("LocalDatabasePath")
    MRN_exist_in_database, KeyRecords = LocalDB_query.check_value(database_path,
                                                                  CNBP_blueprint.table_name,
                                                                  CNBP_blueprint.keyfield,
                                                                  MRN)
    if MRN_exist_in_database is False:
        return None

    # Only ONE record per MRN.
    assert(len(KeyRecords) == 1)
    seriesUID_index = LocalDB_query.check_header_index(database_path, CNBP_blueprint.table_name, 'SeriesUID')

    # Load the json and return the variable structure
    json_SeriesUID = KeyRecords[0][seriesUID_index]
    if json_SeriesUID is None:
        logger.warning("No existing UID Data information found.")
        return None
    list_SeriesUID = json.load(json_SeriesUID)

    return list_SeriesUID


def get_DCCID(MRN):
    """
    Assuming the MRN exist, get the MRNID.
    :param MRN: the MRN to look for
    :return: the CNBPID associated with that particular MRN number.
    """
    # Load local database from .env file
    database_path = config_get("LocalDatabasePath")
    MRN_exist_in_database, KeyRecords = LocalDB_query.check_value(database_path,
                                                                  CNBP_blueprint.table_name,
                                                                  CNBP_blueprint.keyfield,
                                                                  MRN)
    if MRN_exist_in_database is False:
        return None

    # Only ONE record per MRN.
    assert(len(KeyRecords) == 1)
    dcc_header_index = LocalDB_query.check_header_index(database_path, CNBP_blueprint.table_name, 'DCCID')

    return KeyRecords[0][dcc_header_index]


def get_timepoint(MRN):
    """
    Assuming the MRN exist, get the MRNID.
    :param MRN: the MRN to look for
    :return: the CNBPID associated with that particular MRN number.
    """
    # Load local database from .env file
    database_path = config_get("LocalDatabasePath")
    MRN_exist_in_database, KeyRecords = LocalDB_query.check_value(database_path,
                                                                  CNBP_blueprint.table_name,
                                                                  CNBP_blueprint.keyfield,
                                                                  MRN)
    if MRN_exist_in_database is False:
        return None

    # Only ONE record per MRN, even if there are multiple timepoint. We keep the latest one.
    assert(len(KeyRecords) == 1)
    timepoint_header_index = LocalDB_query.check_header_index(database_path, CNBP_blueprint.table_name, 'Timepoint')

    return KeyRecords[0][timepoint_header_index]


def get_scan_date(MRN):
    """
    Assuming the MRN exist, get the MRNID.
    :param MRN: the MRN to look for
    :return: the CNBPID associated with that particular MRN number.
    """
    # Load local database from .env file
    database_path = config_get("LocalDatabasePath")
    MRN_exist_in_database, KeyRecords = LocalDB_query.check_value(database_path,
                                                                  CNBP_blueprint.table_name,
                                                                  CNBP_blueprint.keyfield,
                                                                  MRN)
    if MRN_exist_in_database is False:
        return None

    # Only ONE record per MRN, even if there are multiple timepoint. We keep the latest one.
    assert(len(KeyRecords) == 1)
    date_header_index = LocalDB_query.check_header_index(database_path, CNBP_blueprint.table_name, 'Date')
    scan_date = KeyRecords[0][date_header_index]
    return scan_date


def set_CNBP(MRN: int, CNBPID): #fixme: all the SET RECORDS NEED TO CONSIDER THE MULTIROW possiblities.
    """
    Update record with proper CNBPID which has particular MRN
    :param MRN:
    :return:
    """
    database_path = config_get("LocalDatabasePath")

    # Update the MRN record with CNBPID
    LocalDB_query.create_entry(database_path, CNBP_blueprint.table_name, CNBP_blueprint.keyfield, MRN)
    LocalDB_query.update_entry(database_path, CNBP_blueprint.table_name, CNBP_blueprint.keyfield, MRN, "CNBPID", CNBPID)


def append_seriesUID(MRN: int, SeriesUID: List[str]):
    """
    Append record with SeriesUID list. which has particular MRN
    :param MRN:
    :return:
    """
    database_path = config_get("LocalDatabasePath")
    existing_series_UID = get_seriesUID(MRN)
    if existing_series_UID is None:
        total_series_UID = SeriesUID
    else:
        total_series_UID = existing_series_UID + SeriesUID

    # JSON dumps.
    json_seriesUID = json.dumps(total_series_UID )

    # Update the MRN record with SeriesUID
    LocalDB_query.update_entry(database_path, CNBP_blueprint.table_name, CNBP_blueprint.keyfield, MRN, "SeriesUID",
                               json_seriesUID)


def set_seriesUID(MRN: int, SeriesUID: List[str]):
    """
    Update record with SeriesUID list. which has particular MRN
    :param MRN:
    :return:
    """
    database_path = config_get("LocalDatabasePath")


    # JSON dumps.
    json_seriesUID = json.dumps(SeriesUID)

    # Update the MRN record with SeriesUID
    LocalDB_query.update_entry(database_path, CNBP_blueprint.table_name, CNBP_blueprint.keyfield, MRN, "SeriesUID", json_seriesUID)


def set_DCCID(MRN: int, DCCID):
    """
    Update record with proper DCCID which has particular MRN
    :param MRN:
    :return:
    """
    database_path = config_get("LocalDatabasePath")

    # Update the MRN record with DCCID
    LocalDB_query.update_entry(database_path, CNBP_blueprint.table_name, CNBP_blueprint.keyfield, MRN, "DCCID", DCCID, )


def set_completion(MRN: int, status: int = 0):
    """
    Update record with proper completion status which has particular MRN
    :param MRN:
    :return:
    """
    database_path = config_get("LocalDatabasePath")

    # Update the MRN record with DCCID
    LocalDB_query.update_entry(database_path, CNBP_blueprint.table_name, CNBP_blueprint.keyfield, MRN, "Completed", status)


def set_scan_date(MRN: int, scan_date: str):
    """
    Update record with proper scan time which has particular MRN
    :param MRN:
    :return:
    """
    database_path = config_get("LocalDatabasePath")

    # Update the MRN record with Timepoint
    LocalDB_query.update_entry(database_path, CNBP_blueprint.table_name, CNBP_blueprint.keyfield, MRN, "Date",
                               scan_date)


def set_timepoint(MRN: int, Timepoint: str):
    """
    Update record with proper Timepoint which has particular MRN
    :param MRN:
    :return:
    """
    database_path = config_get("LocalDatabasePath")

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
    InstitionID = config_get("institutionID")

    import DICOM.API
    # Check ProjectID string and then return the ProjectID;
    ProjectID = DICOM.API.study_validation(DICOM_protocol)

    # Use those two pieces of information to form a partial query pattern that can run on the SQLite
    partial_search_input = InstitionID + ProjectID

    DB_path = config_get("LocalDatabasePath")

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
            logger.warning(
                "A non-compliant record has been found in the existing SQLite database, you might want to look into that. ")
            logger.warning(
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
    path_config_database = load_dotenv_var("config_database") # Default location to dtconfigure.sqlite
    name_config_table = load_dotenv_var("config_table")  # Default location to dtconfigure.sqlite

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
