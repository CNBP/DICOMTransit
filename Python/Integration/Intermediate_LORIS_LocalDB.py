import logging
from LocalDB.query import LocalDB_query
from LORIS.timepoint import LORIS_timepoint
from LocalDB.schema import CNBP_blueprint

logger = logging.getLogger()


def findTimePointUpdateDatabase(token, DCCID, database_path, table_name):
    """
    Find the timepoint of the subject, IF they exist, then update the given database by finding its relevant MRN.
    :param token:
    :param DCCID:
    :param database_path:
    :param table_name:
    :return:
    """

    MRN = -1

    # todo: permission must be checked to ensure we are not geting 401 error! which is an access issue.
    # todo: 2018-07-24 continue debug this code about entry creation.
    time_point = LORIS_timepoint.findLatestTimePoint(token, DCCID)

    # Timepoint Check
    if time_point is None:
        return False, "No timepoint found"
    else:
        logger.info(f"Timepoint retrieved okay: {time_point}")

    # Validate table and schema congruency
    success, reason = LocalDB_query.validateLocalTableAndSchema(
        database_path, table_name, "DCCID"
    )
    if not success:
        return False, reason

    # Check local database for the rows with matching DCCID.
    success, subject_rows = LocalDB_query.check_value(
        database_path, table_name, "DCCID", DCCID
    )
    if not success:
        return False, "No entries with this DCCID!"

    # Recall each row WILL conform to schema.
    for row in subject_rows:

        # Get MRN:
        DCCID_table_index = LocalDB_query.check_header_index(
            database_path, table_name, "DCCID"
        )

        assert str(DCCID) == str(row[DCCID_table_index])

        # Need to update these rows with the new value.
        MRN = row[0]  # the identifier of the record.

        try:
            LocalDB_query.update_entry(
                database_path,
                table_name,
                CNBP_blueprint.keyfield,
                MRN,
                "Timepoint",
                time_point,
            )
        except IOError:
            return False, "Check the database is not read only. "

    return True, "Timepoint successfully updated in the local SQLite database."


if __name__ == "__main__":

    # Unit test
    from Integration.test_Integration import test_updateLocalTimepoint

    test_updateLocalTimepoint()
