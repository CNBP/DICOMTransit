from tempfile import TemporaryDirectory
from shutil import copyfile
from LORIS.validate import LORIS_validation
from PythonUtils.file import dictionary_search
from settings import config_get
from PythonUtils.folder import get_abspath
from tqdm import tqdm
import os
import logging

logger = logging.getLogger()


def anonymize_to_zip(folder_path, zip_ID):
    """
    Takes everything within the folder, and zip create a zip file in the DEFAULT .env configured zip storage location.
    :param folder_path:
    :param zip_ID: should be CNBPID_DCCID_VISIT format without .zip extension
    :return:
    """
    from DICOM.anonymize import DICOM_anonymize
    DICOM_anonymize.folder(folder_path, zip_ID)

    change_to_zip_dir()

    from PythonUtils.file import zip_with_name
    zip_with_name(folder_path, zip_ID)  # todo! it does not check if there are OTHER files in there!

def change_to_zip_dir():
    # Load the name of the storage folder from the configuration file.
    folder_to_zip = config_get("ZipPath")

    # Find the root fo the project where the zip storage is related to the location of the current DICOM directory.
    project_root = get_abspath(__file__, 2)

    # Create absolute path to the folder to be zipped
    zip_path = os.path.join(project_root, folder_to_zip)
    #
    os.chdir(zip_path)


def anonymize_files(files):
    """
    #fixme: not working not sure why these exist...
    Anaonymize the files given using the name provided. WIP!!!
    :param files:
    :return:
    """
    from DICOM.anonymize import DICOM_anonymize
    # Copy files to Temporary Folder
    with TemporaryDirectory() as temp_folder:

        # Copy all files
        for file in files:
            _, fileName = os.path.split(file)
            copyfile(file, os.path.join(temp_folder, fileName))

        # Anonymize that folder.
        DICOM_anonymize.folder(temp_folder, "NEW_CONTESTANT")
    pass


def check_anonymization(files: list, anonymized_name) -> bool:
    """
    A function to double check a list of files against the KNOWN anonymized value. This ensures that the anonymization actually gets carried out.

    NOTE!!!!
    This is the part where we have to ensure all the values are properly anonymized.
    todo: generalize this such that it will provide a list of fields and then anonymize them all from the database etc.
    :param files: File must be the absolute path!
    :param anonymized_name:
    :return:
    """
    from DICOM.elements import DICOM_elements
    from DICOM.elements_batch import DICOM_elements_batch
    from DICOM.validate import DICOM_validate

    # Check every single file in the DICOM collections.
    for file in tqdm(files, position=0):

        success, DICOM = DICOM_validate.file(file)

        if not success:
            return False

        properties = ["PatientID", "PatientName"]

        properties_output = DICOM_elements_batch.retrieval(DICOM, properties)


        success1, patient_id = DICOM_elements.retrieve_fast(DICOM, "PatientID")
        success2, name = DICOM_elements.retrieve_fast(DICOM, "PatientName")

        # bad retrieval.
        if not success1 or not success2:
            return False

        # not properly anonymized patient ID
        if not patient_id == anonymized_name:
            return False

        # not properly anonymized name.
        if not name ==anonymized_name:
            return False

    return True

def retrieve_study_protocol(files):
    """
    From the list of files, find the names of all the possible studies descriptions.
    #(0008,1030)	Study Description	e.g. FUNCTIONAL^Dr.Bohbot
    :param files:
    :return:
    """
    protocols = []

    from DICOM.elements import DICOM_elements

    # Get DICOM files.
    for file in files:

        # Ensure it exists before attempting to retrieve it.
        if os.path.exists(file):
            success, study_protocol = DICOM_elements.retrieve(file, "ProtocolName")
        else:
            logger.error(f"Study protocol could not be retrieved from: {file}. Skipping this file!")
            continue

        # Only add if it is not already in the list (avoid dupliate, ensure unique entries
        if LORIS_validation.validate_projectID(study_protocol) and study_protocol not in protocols:
            protocols.append(study_protocol)

    return protocols

def study_validation(study):
    """
    Given a string read from the DICOM studies field, check it against the project ID dictionary to see if any of the project belongs.
    :param study:
    :return: PROJECT or NONE
    """
    import json

    # It checks if the key exist first.
    if LORIS_validation.validate_projectID(study) is False:
        return False

    projectID_dictionary_json: str = config_get("projectID_dictionary")
    projectID_list = json.loads(projectID_dictionary_json)

    # check if project ID is in the projectID list.
    key = dictionary_search(projectID_list, study)
    # todo: what if the key does not exist?

    return key


def infer_project_using_protocol(files):
    """
    Check if the DICOM files provided contain the appropriate project specific acquisition information tags that would be necessary to be considered to be one of the project.
    :param files:
    :return: one or more project definition
    """

    # Check acquisition protocols.
    # Compile unique list of acquisition protocoles
    studies = retrieve_study_protocol(files)

    # There should only be ONE studies specificed in the files provided.
    if len(studies) > 1:
        return False, "Files provided have inconsistent studies protocols"

    # INFER project using them.
    projectID = study_validation(studies[0]) # recall, studies can only have one member.

    return projectID

if __name__ == "__main__":
    anonymize_to_zip(r"C:\Users\dyt81\Downloads\TestAnonymize", "VTXGL019998_598399_V1")