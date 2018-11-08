from DICOM.elements import DICOM_elements
from LocalDB.query import LocalDB_query
from LocalDB.schema import CNBP_blueprint
from dotenv import load_dotenv
import logging
import sys

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logger = logging.getLogger(__name__)

def check_MRN(MRN):
    """
    Return true if the MRN exist within the current database
    :return:
    """

    # Load local database from .env file
    database_path = load_dotenv("LocalDatabase")

    # Store MRN in database.
    MRN_exist_in_database, _ = LocalDB_query.check_value(database_path,
                                                         CNBP_blueprint.table_name,
                                                         CNBP_blueprint.keyfield,
                                                         MRN)
    return MRN_exist_in_database

def create_MRN(MRN):
    database_path = load_dotenv("LocalDatabase")

    # Create the MRN record
    LocalDB_query.create_entry(database_path, CNBP_blueprint.table_name, CNBP_blueprint.keyfield, MRN)


def get_CNBP(MRN):
    """
    Assuming the MRN exist, get the CNBPID.
    :param MRN: the MRN to look for
    :return: the CNBPID associated with that particular MRN number.
    """
    # Load local database from .env file
    database_path = load_dotenv("LocalDatabase")
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
    database_path = load_dotenv("LocalDatabase")
    MRN_exist_in_database, KeyRecords = LocalDB_query.check_value(database_path,
                                                                  CNBP_blueprint.table_name,
                                                                  CNBP_blueprint.keyfield,
                                                                  MRN)
    if MRN_exist_in_database is False:
        return None

    assert(len(KeyRecords) == 1)
    dcc_header_index = LocalDB_query.check_header_index(database_path, CNBP_blueprint.table_name, 'DCCID')

    return KeyRecords[dcc_header_index]


def get_visit(MRN):
    """
    Assuming the MRN exist, get the MRNID.
    :param MRN: the MRN to look for
    :return: the CNBPID associated with that particular MRN number.
    """
    # Load local database from .env file
    database_path = load_dotenv("LocalDatabase")
    MRN_exist_in_database, KeyRecords = LocalDB_query.check_value(database_path,
                                                                  CNBP_blueprint.table_name,
                                                                  CNBP_blueprint.keyfield,
                                                                  MRN)
    if MRN_exist_in_database is False:
        return None

    assert(len(KeyRecords) == 1)
    timepoint_header_index = LocalDB_query.check_header_index(database_path, CNBP_blueprint.table_name, 'Timepoint')

    return KeyRecords[timepoint_header_index]


def set_CNBP(MRN, CNBPID):
    """
    Update record with proper CNBPID which has particular MRN
    :param MRN:
    :return:
    """
    database_path = load_dotenv("LocalDatabase")

    # Update the MRN record with CNBPID
    LocalDB_query.update_entry(database_path, CNBP_blueprint.table_name, CNBP_blueprint.keyfield, MRN, "CNBPID", CNBPID, )


def set_DCCID(MRN, DCCID):
    """
    Update record with proper DCCID which has particular MRN
    :param MRN:
    :return:
    """
    database_path = load_dotenv("LocalDatabase")

    # Update the MRN record with DCCID
    LocalDB_query.update_entry(database_path, CNBP_blueprint.table_name, CNBP_blueprint.keyfield, MRN, "DCCID", DCCID, )


def set_timepoint(MRN, Timepoint):
    """
    Update record with proper Timepoint which has particular MRN
    :param MRN:
    :return:
    """
    database_path = load_dotenv("LocalDatabase")

    # Update the MRN record with Timepoint
    LocalDB_query.update_entry(database_path, CNBP_blueprint.table_name, CNBP_blueprint.keyfield, MRN, "Timepoint", Timepoint, )