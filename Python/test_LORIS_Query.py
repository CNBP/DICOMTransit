from LORISQuery import *
import sqlite3
from pathlib import Path
import logging
import os
import sys

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
def test_LORIS_login():
    success, token = login()
    assert success

def test_LORIS_create():
    success, json = getCNBP("projects")
    assert success
    success, json = getCNBP("candidates")
    assert success

def test_checkPSCIDExist():
    response_success, exist = checkPSCIDExist("CNBP0010001")
    assert response_success
    assert exist

def test_checkDCCIDExist():
    response_success, exist = checkDCCIDExist('272264')
    assert response_success
    assert exist
