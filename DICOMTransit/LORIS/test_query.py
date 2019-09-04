import logging
import sys
from DICOMTransit.LORIS.query import LORIS_query
from DICOMTransit.LORIS.candidates import LORIS_candidates


logger = logging.getLogger()

import unittest


class UT_LORISQuery(unittest.TestCase):
    def test_LORIS_login(self):
        response_success, _ = LORIS_query.login()
        assert response_success

        # assert len(token) == 256 #token should always be 256 char long

    def test_LORIS_get(self):
        response_success, token = LORIS_query.login()
        assert response_success
        # assert len(token) == 256  # token should always be 256 char long
        response_success, _ = LORIS_query.getCNBP(token, "projects")
        assert response_success
        response_success, _ = LORIS_query.getCNBP(token, "candidates")
        assert response_success

    def test_checkPSCIDExist(self):
        response_success, token = LORIS_query.login()
        assert response_success
        # assert len(token) == 256  # token should always be 256 char long
        response_success, exist = LORIS_candidates.checkPSCIDExist(token, "VXS9000000")
        assert response_success
        assert not exist
        response_success, exist = LORIS_candidates.checkPSCIDExist(token, "VXS0000001")
        assert response_success
        assert exist

    def test_checkDCCIDExist(self):
        response_success, token = LORIS_query.login()
        assert response_success
        # assert len(token) == 256  # token should always be 256 char long
        exist, _ = LORIS_candidates.checkDCCIDExist(token, 471400)
        assert exist
