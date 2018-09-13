import logging
from LORIS.candidates import LORIS_candidates
from LORIS.query import LORIS_query
import unittest
import sys

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logger = logging.getLogger(__name__)

class UT_LORISCandidates(unittest.TestCase):

    """
    def test_create_subject():
        logger = logging.getLogger('UT_LORIS_create_subject_check')
        response_success, token = LORIS_query.login()

        if not response_success:
            raise ConnectionError

        PSCID = "CNBP8881234"

        success, DCCID = LORIS_candidates.createCandidateCNBP(token, PSCID)

        LORIS_candidates.deleteCandidateCNBP(token, DCCID, PSCID)
        logger.info("UT_LORIS_create_subject_check PASSED")


    def test_delete_subjects():
        logger = logging.getLogger('UT_LORIS_create_subject_check')
        response_success, token = LORIS_query.login()

        DCCID = "881417"
        PSCID = "CNBP9991234"
        # one time runnable code:
        LORIS_candidates.deleteCandidateCNBP(token, DCCID, PSCID)
        logger.info("UT_LORIS_create_subject_check PASSED")
    """

    @staticmethod
    def test_check_projectID():
        ProjectID = "GL01"
        assert LORIS_candidates.check_projectID_compliance(ProjectID)

        ProjectID = "GL09"
        assert not LORIS_candidates.check_projectID_compliance(ProjectID)

        ProjectID = "AL01"
        assert not LORIS_candidates.check_projectID_compliance(ProjectID)

        ProjectID = "AB01"
        assert LORIS_candidates.check_projectID_compliance(ProjectID)

    @staticmethod
    def test_CNBP_PSCID():
        PSCID = "VXS" + "GL01"  + "0001"
        PSCID1 = "VXa" + "GL01" + "0001"
        PSCID2 = "VXS" + "GL02" + "0001"
        PSCID3 = "VXS" + "GL01" + "0001"
        PSCID4 = "VXS" + "GL01" + "0009"

        assert(LORIS_candidates.check_PSCID_compliance(PSCID))
        assert not LORIS_candidates.check_PSCID_compliance(PSCID1)
        assert not LORIS_candidates.check_PSCID_compliance(PSCID2)
        assert LORIS_candidates.check_PSCID_compliance(PSCID3)
        assert LORIS_candidates.check_PSCID_compliance(PSCID4)

if __name__ == "__main__":
    UT_LORISCandidates.test_CNBP_PSCID()