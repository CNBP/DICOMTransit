from orthanc.query import orthanc_query
from LORIS.helper import LORIS_helper
import os
import logging


def step1_orthanc2DICOM(data_folder_path):
    """
    The purpose of this function is to connect to orthanc, retrieve a list of subjects, download each one in turn and unzip them somewhere.
    :return: whether it succeeded, and if succeeded, a list of all folders.
    """
    logger = logging.getLogger("Step1: Orthanc to DICOM files")

    # Input check
    if not os.path.exists(data_folder_path) or not os.path.isdir(data_folder_path):
        logger.info("Bad data folder path")
        return False, None

    # Query Orthanc for all subjects
    reseponse_code, list_subjects = orthanc_query.getOrthanc("patients/")
    if not LORIS_helper.is_response_success(reseponse_code, 200):
        logger.info("Could not connect to Orthanc.")
        return False, None

    all_subject_folder_paths = []

    # For all subjects, unzip them somewhere.
    for subject in list_subjects:

        status, zip_file = orthanc_query.getPatientZipOrthanc(subject)

        # Checks for output from getPatientZipOrthanc
        if not LORIS_helper.is_response_success(status, 200):
            logger.info("Could not get patient zip files from Orthanc")
            return False, None
        if not os.path.exists(zip_file):
            logger.info("Could not locate saved zip files after dowwnloading from Orthanc")
            return False, None

        # Create a directory based on the zip file, which has UUID as name and guarnteed to be unique.
        file, ext = os.path.splitext(zip_file)
        final_folder_name = data_folder_path + file
        os.mkdir(final_folder_name)
        orthanc_query.flatUnZip(zip_file, final_folder_name) #files are guarnteed to be unique and no overwrite of each other. .

        # Keep track of path extracted to for subsequent processing.
        all_subject_folder_paths.append(final_folder_name)
    return True, all_subject_folder_paths

def step2_dicom2LORIS(folder_paths):
    """
    Within each folder, verify they all have the same PatientID.
    :param folder_paths:
    :return:
    """

