import unittest

from DICOM.elements import DICOM_elements
from PythonUtils.folder import recursive_list


class UT_DICOMElement(unittest.TestCase):
    @staticmethod
    def test_element_retrieval():
        # Get all files with JPEG in them.
        file_names = recursive_list(r"C:\Users\Yang Ding\Desktop\test")

        # files = get_testdata_files("[Jj][Pp][Ee][Gg]")
        for file in file_names:
            A, _ = DICOM_elements.retrieve(file, "StudyDescription") # can be ''
            B, _ = DICOM_elements.retrieve(file, "PatientBirthDate") # can be 1995-12-19
            C, _ = DICOM_elements.retrieve(file, "PatientSex") # can be M or F
            assert A and B and C
