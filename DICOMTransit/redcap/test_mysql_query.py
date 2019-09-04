# ----------------------------------------------------------------------------------------------------------------------
#  test_mysql_query.py
# ----------------------------------------------------------------------------------------------------------------------

# ----------------------------------------------------------------------------------------------------------------------
#  Imports
# ----------------------------------------------------------------------------------------------------------------------

import unittest
from DICOMTransit.redcap.mysql_query import (
    send_mysql_data,
    get_mysql_tablename,
    convert_redcap_to_mysql_fieldtype,
    convert_redcap_to_mysql_fieldname,
)
from DICOMTransit.redcap.enums import MySQLType
from DICOMTransit.redcap.transaction import RedcapTransaction


# ----------------------------------------------------------------------------------------------------------------------
#  UT_REDCapMySQLQuery
# ----------------------------------------------------------------------------------------------------------------------


class UT_REDCapMySQLQuery(unittest.TestCase):
    @staticmethod
    def test_send_mysql_data() -> None:

        # Test empty / no redcap transaction.
        assert send_mysql_data(RedcapTransaction())[0] is False

    @staticmethod
    def test_get_mysql_tablename() -> None:

        # METADATA.
        metadata_test = [
            [
                "admissioncasetype_descriptionfr",
                "text",
                "admissioncasetype_descriptionfr",
                "test_metadata_tablename",
            ]
        ]

        # TEST #1
        entries_test_redcap_repeat_instrument = {
            "masterid": "1",
            "redcap_repeat_instrument": "test_redcap_repeat_instrument",
            "redcap_repeat_instance": "1",
            "admissioncasetype_casetypeid": "1",
            "admissioncasetype_description": "1a. CNN - NICU Adm (Meets CNN criteria)",
            "admissioncasetype_upload": "1",
            "admissioncasetype_descriptiones": "",
            "admissioncasetype_descriptionpt": "",
            "admissioncasetype_descriptionfr": "",
            "mstadmissioncasetype_complete": 2,
        }

        # TEST #2
        entries_test_mstadmissioncasetype_complete = {
            "masterid": "1",
            "redcap_repeat_instrument": "mstadmissioncasetype",
            "admissioncasetype_casetypeid": "1",
            "admissioncasetype_description": "1a. CNN - NICU Adm (Meets CNN criteria)",
            "admissioncasetype_upload": "1",
            "admissioncasetype_descriptiones": "",
            "admissioncasetype_descriptionpt": "",
            "admissioncasetype_descriptionfr": "",
            "mstadmissioncasetype_complete": 2,
        }

        # TEST #3
        entries_test_metadata = {
            "masterid": "1",
            "redcap_repeat_instance": "1",
            "admissioncasetype_casetypeid": "1",
            "admissioncasetype_description": "1a. CNN - NICU Adm (Meets CNN criteria)",
            "admissioncasetype_upload": "1",
            "admissioncasetype_descriptiones": "",
            "admissioncasetype_descriptionpt": "",
            "admissioncasetype_descriptionfr": "",
        }

        # TEST #4
        entries_test_metadata_unknown = {
            "masterid": "1",
            "redcap_repeat_instance": "1",
            "admissioncasetype_casetypeid": "1",
            "admissioncasetype_description": "1a. CNN - NICU Adm (Meets CNN criteria)",
            "admissioncasetype_upload": "1",
            "admissioncasetype_descriptiones": "",
            "admissioncasetype_descriptionpt": "",
        }

        # TEST #1 ( We test if it return the redcap_repeat_instrument. )
        assert (
            get_mysql_tablename(metadata_test, entries_test_redcap_repeat_instrument)
            == "test_redcap_repeat_instrument"
        )

        # TEST #2 ( If no redcap_repeat_instrument, we need to use the complete field at the end. )
        assert (
            get_mysql_tablename(
                metadata_test, entries_test_mstadmissioncasetype_complete
            )
            == "mstadmissioncasetype"
        )

        # TEST #3 ( If no complete & no redcap_repeat_instrument is found then we need to match with the metadata list. )
        assert (
            get_mysql_tablename(metadata_test, entries_test_metadata)
            == "test_metadata_tablename"
        )

        # TEST #4 ( If no complete & no redcap_repeat_instrument is found then we need to match with the metadata list. )
        assert (
            get_mysql_tablename(metadata_test, entries_test_metadata_unknown)
            == "unknown"
        )

    @staticmethod
    def test_convert_redcap_to_mysql_fieldtype() -> None:

        # TEST - yes no field.
        assert (
            convert_redcap_to_mysql_fieldtype(MySQLType.yesno.name)
            is MySQLType.yesno.value
        )

        # TEST - text field.
        assert (
            convert_redcap_to_mysql_fieldtype(MySQLType.text.name)
            is MySQLType.text.value
        )

        # TEST - text primary field.
        assert (
            convert_redcap_to_mysql_fieldtype(MySQLType.textprimary.name)
            is MySQLType.textprimary.value
        )

        # TEST - text primary field.
        assert convert_redcap_to_mysql_fieldtype("ttt") is MySQLType.unknown.value

    @staticmethod
    def test_convert_redcap_to_mysql_fieldname() -> None:

        # TEST - mst in tablename.
        assert (
            convert_redcap_to_mysql_fieldname("msttablename", "tablename_test")
            == "test"
        )

        # TEST - Order to position convert.
        assert (
            convert_redcap_to_mysql_fieldname("msttablename", "tablename_ordertest")
            == "positiontest"
        )

        # TEST - system to system_
        assert (
            convert_redcap_to_mysql_fieldname("tablename", "tablename_ordersystemtest")
            == "positionsystem_test"
        )

        # TEST - Remove useless _
        assert (
            convert_redcap_to_mysql_fieldname("tablename", "tablename_test_test")
            == "test_test"
        )


if __name__ == "__main__":

    UT_REDCapMySQLQuery.test_send_mysql_data()
    UT_REDCapMySQLQuery.test_get_mysql_tablename()
    UT_REDCapMySQLQuery.test_convert_redcap_to_mysql_fieldtype()
    UT_REDCapMySQLQuery.test_convert_redcap_to_mysql_fieldname()
