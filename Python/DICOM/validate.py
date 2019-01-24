import sys
import logging
import os
from tqdm import tqdm
from PythonUtils.folder import recursive_list
from PythonUtils.file import current_funct_name

class DICOM_validate:

    @staticmethod
    def file(file_path):
        """
        validate to check if the DICOM file is an actual DICOM file.
        :param file_path:
        :return:
        """
        logger = logging.getLogger(current_funct_name())

        global dicom
        dicom = None

        from pydicom.filereader import InvalidDicomError
        from pydicom.filereader import read_file
        try:
            dicom = read_file(file_path)
        except InvalidDicomError:
            logger.warning(f"{file_path} is not a DICOM file. Skipping")
            return False, None

        #if dicom.

        return True, dicom

    @staticmethod
    def path(dir_path):
        """
        Some basic information of the participants must be consistent across the files, such as the SCAN DATE (assuming they are not scanning across MIDNIGHT POINT)
        Birthday date, subject name, etc MUST BE CONSISTENT across a SINGLE subject's folder, RIGHT!

        :param dir_path:
        :returns: 0) if the path is valid, 2) list of ONLY the valid DICOM files.
        """
        logger = logging.getLogger(current_funct_name())

        # Reject bad input check
        if not os.path.exists(dir_path) or not os.path.isdir(dir_path):
            logger.error("Bad data folder path")
            return False, None

        # Get all possible files from the there.
        files = recursive_list(dir_path)

        # Used to record the first encountered patientID and name, and will check against subsequent folder for same matching information.
        PatientID = ""
        PatientName = ""

        # List to store all validated DICOM files.
        validated_DICOM_files = []

        from DICOM.elements import DICOM_elements
        logger.info("Checking individual dicom files for patient info consistencies")

        # Check individual DICOM file for consistencies.
        for file in tqdm(files):

            # Skip current file if they are not DICOM files.
            is_DICOM, _ = DICOM_validate.file(file)
            if not is_DICOM:
                logger.error(f"Bad DICOM files detected: {file}")
                continue

            # todo: what if one of them is NONE?
            # todo: what if the date and other things are inconsistent?
            # Record first instance of patient ID and patient name.
            if PatientID == '' and PatientName == '':
                Success, PatientID = DICOM_elements.retrieve(file, "PatientID")
                Success, PatientName = DICOM_elements.retrieve(file, "PatientName")

                # raise issue if not successful
                if not Success:
                    logger.error("DICOM meta data retrieval failure EVEN for the first DICOM FILE?! Checking next one.")
                else:
                    name = PatientName.original_string.decode("latin_1")
                    logger.debug(f"DICOM meta data retrieval success: {PatientID } {name}")

                # Regardless of success of failure, must continue to process the next file.
                continue

            # Check consistencies across folders in terms of patient ID, NAME.
            Success1, CurrentPatientID = DICOM_elements.retrieve(file, "PatientID")
            Success2, CurrentPatientName = DICOM_elements.retrieve(file, "PatientName")

            if not Success1 or not Success2:
                logger.error("Could not retrieve fields for comparison. At least ONE DICOM file has inconsistent Patient ID/NAME field.")
                return False, None

            if not (PatientID == CurrentPatientID) or not (PatientName == CurrentPatientName):
                logger.info("PatientID or Name mismatch from the dicom archive. .")
                return False, None

            validated_DICOM_files.append(file)

        return True, validated_DICOM_files

    #if __name__ == '__main__':
