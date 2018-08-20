import sys
import logging

from DICOM.validate import DICOM_validate
from DICOM.test_DICOM import get_test_DICOM_path
from pydicom.data import get_testdata_files

logging.basicConfig(stream=sys.stdout, level=logging.INFO)


def test_MRN():
    string = 1234567
    assert DICOM_validate.MRN(string)

    string = "1234567"
    assert DICOM_validate.MRN(string)

    string = "12345678"
    assert not DICOM_validate.MRN(string)

    string = 12345678
    assert not DICOM_validate.MRN(string)

    string = "123456"
    assert DICOM_validate.MRN(string)

    string = 123456
    assert DICOM_validate.MRN(string)

def test_DICOM_validator():



    file_name = get_test_DICOM_path()
    success, data = DICOM_validate.file(file_name)
    assert success

    file_name = get_testdata_files("README.txt")[0]
    success, data = DICOM_validate.file(file_name)
    assert not success

