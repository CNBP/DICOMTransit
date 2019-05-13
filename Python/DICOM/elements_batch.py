from DICOM.elements import DICOM_elements
from typing import List, Optional
from tqdm import tqdm
import logging
import os
from PythonUtils.folder import recursive_list
from pydicom.dataset import FileDataset

logger = logging.getLogger()


class DICOM_elements_batch:
    @staticmethod
    def retrieve_sUID(dicom_files: list, sample_rate: int = 10) -> List[str]:
        """
        Check all dicom files to get a unique list of all possible UUIDs.
        :param dicom_files:
        :return:
        """
        logger.debug(
            "Commencing unique series UID retrieval across representative DICOM files provided. "
        )
        from DICOM.elements import DICOM_elements

        # Randomly sample the list every 10 items as most DICOM scans have at least 10 DICOM files and this ensures performance.
        short_list = dicom_files[0::sample_rate]  # sample every 10 items.

        list_unique_sUID = []
        for file in tqdm(short_list, position=0):
            success, UID = DICOM_elements.retrieve_seriesUID(file)
            if UID not in list_unique_sUID:
                list_unique_sUID.append(UID)
        logger.debug(
            "Finished compiling a representative samples of unique series UID across DICOM files provided."
        )

        return list_unique_sUID

    @staticmethod
    def traversal(dir_path: str, consistency_check: bool = True):
        """
        Some basic information of the participants must be consistent across the files, such as the SCAN DATE (assuming they are not scanning across MIDNIGHT POINT)
        Birthday date, subject name, etc MUST BE CONSISTENT across a SINGLE subject's folder, RIGHT!

        :param dir_path:
        :returns: 0) if the path is valid, 2) list of ONLY the valid DICOM files.
        """
        from DICOM.validate import DICOM_validate

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

        logger.info("Traversing individual dicom file for validation information.")

        list_unique_sUID = []
        previous_sUID = None  # a shorthand to bypass the list check.
        # Check individual DICOM file for consistencies.
        for file in tqdm(files, position=0):

            # Skip current file if they are not DICOM files.
            is_DICOM, dicom_obj = DICOM_validate.file(file)

            if not is_DICOM:
                logger.error(
                    f"Bad DICOM files detected: {file}. They are not returned in the validated list!"
                )

                continue

            # The following section checks individual files and determine if all files have consistency name/patient etc.
            # Useful for unanticipated ZIP files which can be contaminated.
            # Not useful when dealing with ORTHANC output files.

            if consistency_check:
                # todo: what if one of them is NONE?
                # todo: what if the date and other things are inconsistent?
                # Record first instance of patient ID and patient name.
                if PatientID == "" and PatientName == "":
                    Success, PatientID = DICOM_elements.retrieve_fast(
                        dicom_obj, "PatientID"
                    )
                    Success, PatientName = DICOM_elements.retrieve_fast(
                        dicom_obj, "PatientName"
                    )

                    # raise issue if not successful
                    if not Success:
                        logger.error(
                            "DICOM meta data retrieval failure EVEN for the first DICOM FILE?! Checking next one."
                        )
                    else:
                        name = PatientName.original_string.decode("latin_1")
                        logger.debug(
                            f"DICOM meta data retrieval success: {PatientID} {name}"
                        )

                    # Regardless of success of failure, must continue to process the next file.
                    continue

                # Check consistencies across folders in terms of patient ID, NAME.
                Success1, CurrentPatientID = DICOM_elements.retrieve_fast(
                    dicom_obj, "PatientID"
                )
                Success2, CurrentPatientName = DICOM_elements.retrieve_fast(
                    dicom_obj, "PatientName"
                )

                if not Success1 or not Success2:
                    logger.error(
                        "Could not retrieve fields for comparison. At least ONE DICOM file has inconsistent Patient ID/NAME field."
                    )
                    return False, None

                if not (PatientID == CurrentPatientID) or not (
                    PatientName == CurrentPatientName
                ):
                    logger.info("PatientID or Name mismatch from the dicom archive. .")
                    return False, None

            success, UID = DICOM_elements.retrieve_fast(dicom_obj, "SeriesInstanceUID")

            # A quick UID check before the HEAVY list operation.
            if not UID == previous_sUID and UID not in list_unique_sUID:
                list_unique_sUID.append(UID)

            validated_DICOM_files.append(file)
            previous_sUID = UID

        return True, validated_DICOM_files, list_unique_sUID

    @staticmethod
    def retrieval(
        dicom_object: FileDataset, DICOM_properties=List[str]
    ) -> (bool, Optional[List[str]]):
        """
        Retrieve a series of properties from an in memory DICOM object.
        :param dicom_object:
        :param DICOM_properties:
        :return:
        """
        list_properties = []
        for DICOM_property in DICOM_properties:
            success, retrieved_property = DICOM_elements.retrieve_fast(
                dicom_object, DICOM_property
            )
            if success:
                list_properties.append(retrieved_property)
            else:
                return False, None
        return True, list_properties
