import logging
import sys
from LORIS.query import LORIS_query
from LORIS.candidates import LORIS_candidates

logging.basicConfig(stream=sys.stdout, level=logging.INFO)


def test_LORIS_login():
    logger = logging.getLogger('UT_LORIS_login')
    response_success, token = LORIS_query.login()
    assert response_success

    #assert len(token) == 256 #token should always be 256 char long

def test_LORIS_get():
    logger = logging.getLogger('UT_LORIS_get')
    response_success, token = LORIS_query.login()
    assert response_success
    #assert len(token) == 256  # token should always be 256 char long
    response_success, json = LORIS_query.getCNBP(token, "projects")
    assert response_success
    response_success, json = LORIS_query.getCNBP(token, "candidates")
    assert response_success


def test_checkPSCIDExist():
    logger = logging.getLogger('UT_LORIS_PSCID_check')
    response_success, token = LORIS_query.login()
    assert response_success
    #assert len(token) == 256  # token should always be 256 char long
    response_success, exist = LORIS_candidates.checkPSCIDExist(token, "CNBP0010001")
    assert response_success
    assert not exist


def test_checkDCCIDExist():
    logger = logging.getLogger('UT_LORIS_DCCID_check')
    response_success, token = LORIS_query.login()
    assert response_success
    #assert len(token) == 256  # token should always be 256 char long
    response_success, exist = LORIS_candidates.checkDCCIDExist(token, 272264)
    assert response_success
    assert exist


if __name__ == '__main__':
    test_checkPSCIDExist()
