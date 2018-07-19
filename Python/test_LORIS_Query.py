from LORISQuery import *
import sqlite3
from pathlib import Path
import logging
import os
import sys

logging.basicConfig(stream=sys.stdout, level=logging.INFO)

def test_LORIS_login():
    logger = logging.getLogger('UT_LORIS_login')
    response_success, token = login()
    assert response_success
    assert len(token) == 256 #token should always be 256 char long

def test_LORIS_get():
    logger = logging.getLogger('UT_LORIS_get')
    response_success, json = getCNBP("projects")
    assert response_success
    response_success, json = getCNBP("candidates")
    assert response_success

def test_checkPSCIDExist():
    logger = logging.getLogger('UT_LORIS_PSCID_check')
    response_success, exist = checkPSCIDExist("CNBP0010001")
    assert response_success
    assert exist

def test_checkDCCIDExist():
    logger = logging.getLogger('UT_LORIS_DCCID_check')
    response_success, exist = checkDCCIDExist('272264')
    assert response_success
    assert exist
