import logging
from LocalDB.query import validateLocalTableAndSchema, check_value, update_entry, check_header_index
from LORIS.timepoint import findLatestTimePoint
from LocalDB.schema import *


def findTimePointUpdateDatabase(token, DCCID, database_path, table_name):
    """
    Find the timepoint of the subject, IF they exist, then update the given database by finding its relevant MRN.
    :param token:
    :param DCCID:
    :param database_path:
    :param table_name:
    :param ColumnName:
    :param ColumnValue:
    :return:
    """

    logger = logging.getLogger('Intermediate_findTimePointUpdateDatabase')

    MRN = -1


    # todo: permission must be checked to ensure we are not geting 401 error! which is an access issue.
    # todo: 2018-07-24 continue debug this code about entry creation.
    time_point = findLatestTimePoint(token, DCCID)

    # Timepoint Check
    if time_point is None:
        return False, "No timepoint found"
    else:
        logger.info("Timepoint retrieved okay:" + time_point)

    # Validate table and schema congruency
    success, reason = validateLocalTableAndSchema(database_path, table_name, "DCCID")
    if not success:
        return False, reason

    # Check local database for the rows with matching DCCID.
    success, subject_rows = check_value(database_path, table_name, "DCCID", DCCID)
    if not success:
        return False, "No entries with this DCCID!"

    # Recall each row WILL conform to schema.
    for row in subject_rows:

        # Get MRN:
        DCCID_table_index = check_header_index(database_path, table_name, "DCCID")

        assert (str(DCCID) == str(row[DCCID_table_index]))

        # Need to update these rows with the new value.
        MRN = row[0] # the identifier of the record.

        try:
            update_entry(database_path, table_name, CNBP_schema_keyfield, MRN, "Timepoint", time_point)
        except IOError:
            return False, "Check the database is not read only. "

    return True, "Timepoint successfully updated in the local SQLite database."


if __name__ == '__main__':

    # Unit test
    from Integration.test_Integration import test_updateLocalTimepoint
    test_updateLocalTimepoint()
