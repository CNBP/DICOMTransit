import pydicom
import sys
import os
import argparse
import getpass
import logging
import unittest
from DICOM import DICOM_RequireDecompression, DICOM_validator, DICOM_retrieveMRN, DICOM_computeScanAge, DICOM_anonymizer

logging.basicConfig(stream=sys.stdout, level=logging.INFO)

def get_test_DICOM_path():
    from pydicom.data import get_testdata_files
    filename = get_testdata_files("rtplan.dcm")[0]
    return filename

def test_DICOM_validator():

    file_name= get_test_DICOM_path()
    success, data = DICOM_validator(file_name)
    assert success

    file_name = ".coverage"
    success, data = DICOM_validator(file_name)
    assert not success

def test_DICOM_RequireDecompression():
    assert not (DICOM_RequireDecompression('1.2.840.10008.1.2'))
    assert not (DICOM_RequireDecompression('1.2.840.10008.1.2.1'))
    assert not (DICOM_RequireDecompression('1.2.840.10008.1.2.2'))
    assert (DICOM_RequireDecompression('1.2.840.10008.1.2.4'))
    assert (DICOM_RequireDecompression('1.2.840.10008.1.2.4.57'))

class MyTestCase(unittest.TestCase):
    def test_wrong_syntax(self):
        self.assertRaises(ValueError, DICOM_RequireDecompression, 'FakeTest')


def test_DICOM_retrieveMRN():
    file_name = get_test_DICOM_path()
    success, MRN = DICOM_retrieveMRN(file_name)
    assert success
    assert (MRN == 'CNBP0010001')

def test_DICOM_computerScanAge():
    logger = logging.getLogger("DICOM compute age")
    success, Age = DICOM_computeScanAge("0000000A")
    assert success
    logger.info(Age.day)

def test_DICOM_anonymizer():
    file_name = get_test_DICOM_path()
    success = DICOM_anonymizer(file_name, "CNBP0010001")
    assert success


if __name__ == '__main__':
    test_DICOM_validator()
    Test = MyTestCase()
    Test.test_wrong_syntax()
    test_DICOM_RequireDecompression()
    test_DICOM_computerScanAge()
    test_DICOM_validator()
    test_DICOM_anonymizer()
    test_DICOM_retrieveMRN()