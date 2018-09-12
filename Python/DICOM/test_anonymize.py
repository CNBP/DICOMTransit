import unittest
from tempfile import TemporaryDirectory
from DICOM.anonymize import DICOM_anonymize
from shutil import copyfile
import os

class UT_DICOMAnonymization(unittest.TestCase):

    @staticmethod
    def test_folder():
        from pydicom.data import get_testdata_files

        # Make Temporary Folder
        files = get_testdata_files("[mM][rR][iI]")

        # Copy files to Temporary Folder
        with TemporaryDirectory() as temp_folder:

            # Copy all files
            for file in files:
                path, fileName = os.path.split(file)
                copyfile(file, os.path.join(temp_folder, fileName))

            # Anonymize that folder.
            DICOM_anonymize.folder(temp_folder, "NEW_CONTESTANT")

