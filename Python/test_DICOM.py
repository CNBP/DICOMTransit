import pydicom
import sys
import os
import argparse
import getpass
import logging
from pydicom.data import get_testdata_files

logging.basicConfig(stream=sys.stdout, level=logging.INFO)


def test():
    filename = get_testdata_files("rtplan.dcm")[0]
    ds = pydicom.dcmread(filename)  # plan dataset
    ds.PatientName
    ds.dir("setup")  # get a list of tags with "setup" somewhere in the name
    ['PatientSetupSequence']
    ds.PatientSetupSequence[0]
    ds.PatientSetupSequence[0].PatientPosition = "HFP"
    ds.save_as("rtplan2.dcm")
    os.remove("rtplan2.dcm")
    return False