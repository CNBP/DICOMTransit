# ----------------------------------------------------------------------------------------------------------------------
#  Imports
# ----------------------------------------------------------------------------------------------------------------------

from LocalDB.API import load_hospital_record_numbers
from redcap.prepare_patient import prepare_patient_tables
from redcap.prepare_reference import prepare_reference_tables
from redcap.initialization import initialize_import_configuration
from redcap.transaction import RedcapTransaction
from redcap.query import load_metadata, send_data, wipe_all_redcap_data
from redcap.mysql_query import send_mysql_data, wipe_all_mysql_data
from redcap.constants import environment, mysql_export_enabled

import datetime
import logging
import sys


# ----------------------------------------------------------------------------------------------------------------------
#  CNN and CNFUN to REDCap
# ----------------------------------------------------------------------------------------------------------------------

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logger = logging.getLogger(__name__)


def update_redcap_data() -> None:
    """
    This method is the main method of this script. It calls all methods necessary to transfer CNN and CNFUN data
    to REDCap.
    :return: None
    """

    # Indicate that the script is started.
    logger.info('Update REDCap Data Started: ' + str(datetime.datetime.now()))

    # Initialize the RedcapTransaction class object to be past and returned each step of the way.
    transaction_stage0 = RedcapTransaction()

    # Load data import configuration matrix.
    logger.info('Loading Data Import Configuration...')
    transaction_stage1_initialized = initialize_import_configuration(transaction_stage0)
    logger.info('Done.')

    # Get all information about REDCap table names and fields.
    logger.info('Loading REDCap Metadata...')
    transaction_stage2_meta_added = load_metadata(transaction_stage1_initialized)
    logger.info('Done.')

    # Get all hospital record numbers.
    logger.info('Loading Hospital Record Numbers...')
    # Change this flag in environment module or here to force local of DB loading.
    transaction_stage2_meta_added.hospital_record_numbers = \
        load_hospital_record_numbers(environment.USE_LOCAL_HOSPITAL_RECORD_NUMBERS_LIST)
    logger.info('Done.')

    # Prepare Reference Data.
    logger.info('Preparing Reference Data Transfer...')
    transaction_stage3_references_added = prepare_reference_tables(transaction_stage2_meta_added)
    logger.info('Done.')

    # Prepare Patient Data.
    logger.info('Preparing Patient Data Transfer...')
    transaction_stage4_patients_added = prepare_patient_tables(transaction_stage3_references_added)
    logger.info('Done.')

    # Wipe all existing data from REDCap.
    logger.info('Wiping ALL existing data from REDCap...')
    wipe_all_redcap_data()
    logger.info('Done.')

    # Send data to REDCap.
    logger.info('Sending ALL data to REDCap...')
    send_data(transaction_stage4_patients_added)
    logger.info('Done.')

    # If MySQL export is enabled, then we need to export the data to MySQL.
    if mysql_export_enabled:

        # Wiping old MySQL data.
        logger.info('Wiping ALL existing data from MySQL...')
        wipe_all_mysql_data()
        logger.info('Done.')

        # Send data to MySQL.
        logger.info('Sending ALL data to MySQL...')
        send_mysql_data(transaction_stage4_patients_added)
        logger.info('Done.')

    # Indicate that the script is completed.
    logger.info('Update REDCap Data Completed: ' + str(datetime.datetime.now()))

    return

if __name__ == "__main__":
    # Update REDCap Data.
    update_redcap_data()
