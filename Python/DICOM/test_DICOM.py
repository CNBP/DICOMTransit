import os
import sys
import logging
import unittest

from DICOM.decompress import DICOM_decompress
from DICOM.anonymize import DICOM_anonymize
from DICOM.elements import DICOM_elements
from pydicom.data import get_testdata_files


logging.basicConfig(stream=sys.stdout, level=logging.INFO)

def get_test_DICOM_path():
    filename = get_testdata_files("rtplan.dcm")[0]
    return filename

def test_DICOM_decompress():

    logger = logging.getLogger(__name__)

    # Get all test files with "JPEG" in them.
    file_names = get_testdata_files("[Jj][Pp][Ee][Gg]")

    logger.info("List of files to try to decompress:")
    logger.info(file_names)

    success_counter = 0
    fail_counter = 0

    for file in file_names:
        logger.info("Processing: " + file)

        decompressed_file = file+"DECOM"

        success, reason = DICOM_decompress.save_as(file, decompressed_file)

        logger.info(reason)

        if success:
            success_counter += 1
            os.remove(decompressed_file) # restore the test environment to its former state.
            logger.info("Successful.")
        else:
            fail_counter += 1
            logger.info("Failed. Reason:" + reason)
    assert success_counter == 7 # within the test data folder, there should be SEVEN files with JPEG in their name that CAN be successfully loaded.
    assert fail_counter == 4 # within the test data folder, there should be FOUR files with JPEG in their name that CANNOT be successfully loaded.



def test_DICOM_RequireDecompression():
    assert not (DICOM_decompress.check_decompression('1.2.840.10008.1.2'))
    assert not (DICOM_decompress.check_decompression('1.2.840.10008.1.2.1'))
    assert not (DICOM_decompress.check_decompression('1.2.840.10008.1.2.2'))
    assert (DICOM_decompress.check_decompression('1.2.840.10008.1.2.4'))
    assert (DICOM_decompress.check_decompression('1.2.840.10008.1.2.4.57'))


#class MyTestCase(unittest.TestCase):
#    def test_wrong_syntax(self):
#        self.assertRaises(ValueError, DICOM_decompress.check_decompression, 'FakeTest')


def test_DICOM_anonymizer():
    file_names = get_testdata_files("emri")
    for file_name in file_names:
        success = DICOM_anonymize.save(file_name, "CNBP0010001")
        assert success
    for file_name in file_names:
        success, value = DICOM_elements.retrieve(file_name, "PatientID")
        assert success
        assert (value == "CNBP0010001")


def test_DICOM_retrieveMRN():
    path = get_testdata_files("emri_small_big_endian")[0]
    success, MRN = DICOM_elements.retrieveMRN(path)
    assert success
    assert (MRN == 'CNBP0010001')


def test_DICOM_update():
    path = get_testdata_files("emri")
    for file in path:
        success, _ = DICOM_elements.update(file, "PatientBirthDate", "19950101", file)
        assert success

    for file in path:
        success, value = DICOM_elements.retrieve(file, "PatientBirthDate")
        assert success
        assert(value == "19950101")


def test_DICOM_computerScanAge():
    logger = logging.getLogger("DICOM compute age")
    path = get_testdata_files("emri_small_RLE")[0]
    success, Age = DICOM_elements.computeScanAge(path)
    assert success
    logger.info(Age.day)


if __name__ == '__main__':
    test_DICOM_decompress()