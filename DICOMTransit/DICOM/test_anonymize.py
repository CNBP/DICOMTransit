import unittest
import DICOMTransit.DICOM.API


class UT_DICOMAnonymization(unittest.TestCase):
    @staticmethod
    def test_folder():

        # Retrieve list of files to be anonymized.
        from pydicom.data import get_testdata_files

        files = get_testdata_files("[mM][rR][iI]")

        # Call the API under testings.
        DICOMTransit.DICOM.API.anonymize_files(files)
