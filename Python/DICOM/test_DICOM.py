import os
import sys
import logging
import unittest
from pathlib import Path
from DICOM.decompress import DICOM_decompress
from DICOM.anonymize import DICOM_anonymize
from DICOM.elements import DICOM_elements
from pydicom.data import get_testdata_files







# Set all debugging level:
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

# Create logger.
logger = logging.getLogger()


def get_test_DICOM_path():
    filename = get_testdata_files("rtplan.dcm")[0]
    return filename


class UT_DICOMManipulation(unittest.TestCase):


    def test_DICOM_decompress(self):

        # Get all test files with "JPEG" in them.
        file_names = get_testdata_files("[Jj][Pp][Ee][Gg]")

        logger.info("List of files to try to decompress:")
        logger.info(file_names)

        success_counter = 0
        fail_counter = 0

        for file in file_names:
            logger.info(f"Processing: {file}")

            decompressed_file = f"{file}DECOM"

            success, reason = DICOM_decompress.save_as(file, decompressed_file)

            logger.info(reason)

            if success:
                success_counter += 1
                os.remove(decompressed_file)  # restore the test environment to its former state.
                logger.info("Successful.")
            else:
                fail_counter += 1
                logger.critical(f"Failed. Reason:{reason}")
        assert success_counter == 7 # within the test data folder, there should be SEVEN files with JPEG in their name that CAN be successfully loaded.
        assert fail_counter == 4 # within the test data folder, there should be FOUR files with JPEG in their name that CANNOT be successfully loaded.


    def test_DICOM_RequireDecompression(self):
        assert not (DICOM_decompress.check_decompression('1.2.840.10008.1.2'))
        assert not (DICOM_decompress.check_decompression('1.2.840.10008.1.2.1'))
        assert not (DICOM_decompress.check_decompression('1.2.840.10008.1.2.2'))
        assert (DICOM_decompress.check_decompression('1.2.840.10008.1.2.4'))
        assert (DICOM_decompress.check_decompression('1.2.840.10008.1.2.4.57'))

    def test_DICOM_wrong_syntax(self):
        self.assertRaises(ValueError, DICOM_decompress.check_decompression, 'FakeTest')


    def test_DICOM_anonymizer(self):
        file_names = get_testdata_files("emri")
        for file_name in file_names:
            success = DICOM_anonymize.save(file_name, "CNBP0010001")
            assert success
        for file_name in file_names:
            success, value = DICOM_elements.retrieve(file_name, "PatientID")
            assert success
            assert (value == "CNBP0010001")


    def test_DICOM_retrieveMRN(self):
        path = get_testdata_files("emri")
        for file_name in path:
            success = DICOM_anonymize.save(file_name, "1234567")
            assert success
            success, MRN = DICOM_elements.retrieve_MRN(file_name)
            assert success
            assert (MRN == '1234567')


    def test_DICOM_update(self):
        path = get_testdata_files("emri")
        for file in path:
            success, _ = DICOM_elements.update(file, "PatientBirthDate", "19950101", file)
            assert success

        for file in path:
            success, value = DICOM_elements.retrieve(file, "PatientBirthDate")
            assert success
            assert(value == "19950101")


    def test_DICOM_computerScanAge(self):

        path = get_testdata_files("emri_small_RLE")[0]
        success, Age = DICOM_elements.compute_age(path)
        assert success
        logger.info(Age.day)


    def test_DICOM_check_dependency(self):
        import subprocess

        project_root = Path(__file__).parents[2]
        sys.path.append(project_root)
        path_nii = os.path.join(project_root, "BinDependency", "dcm2niix")
        os.environ["PATH"] += os.pathsep + path_nii
        path_dcm = os.path.join(project_root, "BinDependency", "dcmtoolkit")
        os.environ["PATH"] += os.pathsep + path_dcm


        print(path_dcm)
        try:
            # SUPER IMPORTANT! MAKE SURE DCMDJPEG is in the system path!
            subprocess.check_output('dcmdjpeg', cwd=Path(path_nii))
        # When dcmdjpeg has errors
        except Exception as e:
            logger.info(e)
            ErrorMessage = "DCMDJPEG decompression call failed! Make sure DCMDJPEG is in your SYSTEMOS PATH. "
            logger.critical(ErrorMessage)
            raise ImportError

        try:
            # SUPER IMPORTANT! MAKE SURE DCMDJPEG is in the system path!
            subprocess.check_output('dcm2niix', cwd=Path(path_dcm))
        # When dcmdjpeg has errors
        except Exception as e:
            logger.info(e)
            ErrorMessage = "DCMDJPEG decompression call failed! Make sure DCMDJPEG is in your SYSTEMOS PATH. "
            logger.critical(ErrorMessage)
            raise ImportError

        assert(True)

if __name__ == '__main__':
    UT_DICOMManipulation.test_DICOM_check_dependency()
    