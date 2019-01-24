import logging
import sys
from LORIS.query import LORIS_query
from LORIS.candidates import LORIS_candidates


logger = logging.getLogger(__name__)

import unittest
class UT_LORISQuery(unittest.TestCase):

    @staticmethod
    def test_LORIS_login():
        response_success, _ = LORIS_query.login()
        assert response_success

        #assert len(token) == 256 #token should always be 256 char long
    @staticmethod
    def test_LORIS_get():
        response_success, token = LORIS_query.login()
        assert response_success
        #assert len(token) == 256  # token should always be 256 char long
        response_success, _ = LORIS_query.getCNBP(token, "projects")
        assert response_success
        response_success, _ = LORIS_query.getCNBP(token, "candidates")
        assert response_success

    @staticmethod
    def test_checkPSCIDExist():
        response_success, token = LORIS_query.login()
        assert response_success
        #assert len(token) == 256  # token should always be 256 char long
        response_success, exist = LORIS_candidates.checkPSCIDExist(token, "CNBP0010001")
        assert response_success
        assert not exist

    @staticmethod
    def test_checkDCCIDExist():
        response_success, token = LORIS_query.login()
        assert response_success
        #assert len(token) == 256  # token should always be 256 char long
        exist, _ = LORIS_candidates.checkDCCIDExist(token, 836559)
        assert exist


if __name__ == '__main__':
    UT_LORISQuery.test_checkPSCIDExist()
