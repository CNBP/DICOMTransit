import logging
from LORIS.candidates import LORIS_candidates
from LORIS.validate import LORIS_validation
from LORIS.query import LORIS_query
import unittest
import sys


logger = logging.getLogger(__name__)

class UT_LORISCandidates(unittest.TestCase):

    @staticmethod
    def test_create_delete_subject():
        """
        Check both the creation and deletion of the subject for LORIS.
        :return:
        """

        response_success, token = LORIS_query.login()

        if not response_success:
            raise ConnectionError

        # Example PSCI ID.
        PSCID = "CNBP9990987"

        success, DCCID = LORIS_candidates.createCandidate(token, "", "1986-11-18", "Male") #todo: check project ensure it is validated. Might need reassignment
        assert success
        LORIS_candidates.deleteCandidateCNBP(DCCID, PSCID)

    @staticmethod
    def test_check_projectID():
        ProjectID = "GL01"
        assert LORIS_validation.validate_projectID(ProjectID)

        ProjectID = "GL09"
        assert not LORIS_validation.validate_projectID(ProjectID)

        ProjectID = "AL01"
        assert not LORIS_validation.validate_projectID(ProjectID)

        ProjectID = "AB01"
        assert LORIS_validation.validate_projectID(ProjectID)

    @staticmethod
    def test_CNBP_PSCID():
        PSCID = "VXS" + "GL01"  + "0001"
        PSCID1 = "VXa" + "GL01" + "0001"
        PSCID2 = "VXS" + "GL02" + "0001"
        PSCID3 = "VXS" + "GL01" + "0001"
        PSCID4 = "VXS" + "GL01" + "0009"

        assert(LORIS_validation.validate_CNBPID(PSCID))
        assert not LORIS_validation.validate_CNBPID(PSCID1)
        assert not LORIS_validation.validate_CNBPID(PSCID2)
        assert LORIS_validation.validate_CNBPID(PSCID3)
        assert LORIS_validation.validate_CNBPID(PSCID4)

if __name__ == "__main__":
    UT_LORISCandidates.test_CNBP_PSCID()