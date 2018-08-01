import logging
from LORIS.candidates import createCandidateCNBP, deleteCandidateCNBP
from LORIS.query import login
import os
from subprocess import check_call
import sys
from dotenv import load_dotenv

def test_create_subject():
    logger = logging.getLogger('UT_LORIS_create_subject_check')
    response_success, token = login()

    if not response_success:
        raise ConnectionError

    PSCID = "CNBP8881234"

    success, DCCID = createCandidateCNBP(token, PSCID)

    deleteCandidateCNBP(token, DCCID, PSCID)

def test_delete_subjects():
    logger = logging.getLogger('UT_LORIS_create_subject_check')
    response_success, token = login()


    DCCID = "881417"
    PSCID = "CNBP9991234"
    # one time runnable code:
    deleteCandidateCNBP(token, DCCID, PSCID)

if __name__ == "__main__":
    test_create_subject()