import logging
from LORIS.candidates import LORIS_candidates
from LORIS.validate import LORIS_validation
from LORIS.query import LORIS_query
import unittest
import sys


logger = logging.getLogger()

class UT_LORISCandidates(unittest.TestCase):


    def test_create_delete_subject(self):
        """
        Check both the creation and deletion of the subject for LORIS.
        :return:
        """

        response_success, token = LORIS_query.login()

        if not response_success:
            raise ConnectionError

        # Example PSCI ID.
        PSCID = "VSX9990987"

        success, DCCID = LORIS_candidates.createCandidate(token, "loris", "1986-11-18", "Male") #todo: check project ensure it is validated. Might need reassignment
        assert success
        LORIS_candidates.deleteCandidateCNBP(DCCID, PSCID)



    # Commenting out this function until project implementation has been sorted out
    """    
    def test_check_projectID(self):
        ProjectID = "GL01"
        assert LORIS_validation.validate_projectID(ProjectID)

        ProjectID = "GL09"
        assert not LORIS_validation.validate_projectID(ProjectID)

        ProjectID = "AL01"
        assert not LORIS_validation.validate_projectID(ProjectID)

        ProjectID = "AB01"
        assert LORIS_validation.validate_projectID(ProjectID)
    """

    def test_CNBP_PSCID(self):
        PSCID = "VXS0000000"
        PSCID1 = "VXa0129410"
        PSCID2 = "VXS9204812"
        PSCID3 = "VXSasdfiea"
        PSCID4 = "VXS8d8d9s0"

        assert LORIS_validation.validate_CNBPID(PSCID)
        assert not LORIS_validation.validate_CNBPID(PSCID1)
        assert LORIS_validation.validate_CNBPID(PSCID2)
        assert not LORIS_validation.validate_CNBPID(PSCID3)
        assert not LORIS_validation.validate_CNBPID(PSCID4)

if __name__ == "__main__":
    UT_LORISCandidates.test_CNBP_PSCID()