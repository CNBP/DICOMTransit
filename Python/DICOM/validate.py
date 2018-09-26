import sys
import logging
import os
from tqdm import tqdm

logging.basicConfig(stream=sys.stdout, level=logging.INFO)

class DICOM_validate:

    @staticmethod
    def MRN(input_string):
        string=str(input_string)
        if not string.isdigit():
            return False
        try:
            MRN = int(string)
            if 0 < MRN < 9999999:
                return True
            else:
                return False
        except ValueError:
            return False

    @staticmethod
    def file(file_path):
        """
        validate to check if the DICOM file is an actual DICOM file.
        :param file_path:
        :return:
        """
        logger = logging.getLogger(__name__)

        global dicom
        dicom = None

        from pydicom.filereader import InvalidDicomError
        from pydicom.filereader import read_file
        try:
            dicom = read_file(file_path)
        except InvalidDicomError:
            logger.info(file_path + " is not a DICOM file. Skipping")
            return False, None
        return True, dicom

    @staticmethod
    def path(dir_path):
        """
        Some basic information of the participants must be consistent across the files, such as the SCAN DATE (assuming they are not scanning across MIDNIGHT POINT)
        Birthday date, subject name, etc MUST BE CONSISTENT across a SINGLE subject's folder, RIGHT!

        :param dir_path:
        :return:
        """
        logger = logging.getLogger(__name__)


        # Input check
        if not os.path.exists(dir_path) or not os.path.isdir(dir_path):
            logger.info("Bad data folder path")
            return False

        files = os.listdir(dir_path)

        # Used to record the first encountered patientID and name, and will check against subsequent folder for same matching information.
        PatientID = ""
        PatientName = ""

        validated_DICOM_files = []

        from DICOM.elements import DICOM_elements
        logger.info("Checking individual dicom files for patient info consistencies")

        # Check individual DICOM file for consistencies.
        for file in tqdm(files):

            # Skip current file if they are not DICOM files.
            isDICOM, _ = DICOM_validate.file(file)
            if not isDICOM:
                continue

            # Record first instance of patient ID and patient name.
            if PatientID is None and PatientName is None:
                Success, PatientID = DICOM_elements.retrieve(files[0], "PatientID")
                Success, PatientName = DICOM_elements.retrieve(files[0], "PatientName")

                # raise issue if not successful
                if not Success:
                    logger.info("DICOME meta data retrieval failure.")
                    return False
                continue

            # Check consistencies across folders in terms of patient ID, NAME.
            CurrentPatientID = DICOM_elements.retrieve(file, "PatientID")
            CurrentPatientName = DICOM_elements.retrieve(file, "PatientName")

            if not (PatientID == CurrentPatientID) or not (PatientName == CurrentPatientName):
                logger.info("PatientID or Name mismatch from the dicom archive. .")
                return False

            validated_DICOM_files.append(file)

        return True, validated_DICOM_files

    #if __name__ == '__main__':
