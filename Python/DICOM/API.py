from tempfile import TemporaryDirectory
from shutil import copyfile
from LORIS.validate import LORIS_validation
from PythonUtils.file import dictionary_search
from PythonUtils.env import load_validate_dotenv
from PythonUtils.folder import get_abspath
from LocalDB.schema import CNBP_blueprint
import os


def anonymize_to_zip(folder_path, zip_ID):
    """
    Takes everything within the folder, and zip create a zip file in the DEFAULT .env configured zip storage location.
    #todo!!! Shoddily done for now. MUST REFACTOR!
    :param folder_path:
    :param zip_ID: should be CNBPID_DCCID_VISIT format without .zip extension
    :return:
    """
    from DICOM.anonymize import DICOM_anonymize

    # Find the root fo the project where the zip storage is related to the location of the current DICOM directory.
    project_root = get_abspath(__file__, 2)



    # Load the name of the storage folder from the configuration file.
    zip_folder = load_validate_dotenv("zip_storage_location", CNBP_blueprint.dotenv_variables)

    # Anonymize the entire folder provided with the ZIP ID.
    DICOM_anonymize.folder(folder_path, zip_ID)

    from PythonUtils.file import zip_with_name

    # Create absolute path to the folder to be zipped
    zip_path = os.path.join(project_root, zip_folder)

    #
    os.chdir(zip_path)
    zip_with_name(folder_path, zip_ID) #todo! it does not check if there are OTHER files in there!

def anonymize_files(files):
    """
    Anaonymize the files given using the name provided. WIP!!!
    :param files:
    :return:
    """

    # Copy files to Temporary Folder
    with TemporaryDirectory() as temp_folder:

        # Copy all files
        for file in files:
            _, fileName = os.path.split(file)
            copyfile(file, os.path.join(temp_folder, fileName))

        # Anonymize that folder.
        DICOM_anonymize.folder(temp_folder, "NEW_CONTESTANT")
    pass

def retrieve_study_descriptions(files):
    """
    From the list of files, find the names of all the possible studies descriptions.
    #(0008,1030)	Study Description	e.g. FUNCTIONAL^Dr.Bohbot
    :param files:
    :return:
    """
    studies = []

    from DICOM.elements import DICOM_elements

    # Get DICOM files.
    for file in files:

        # Ensure it exists before attempting to retrieve it.
        assert (os.path.exists(file))
        success, StudyDescription = DICOM_elements.retrieve(file, "StudyDescription")

        # Only add if it is not already in the list (avoid dupliate, ensure unique entries
        if LORIS_validation.validate_projectID(StudyDescription) and StudyDescription not in studies:
            studies.append(StudyDescription)

    return studies

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

    projectID_dictionary_json: str = load_validate_dotenv("projectID_dictionary", CNBP_blueprint.dotenv_variables)
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
    studies = retrieve_study_descriptions(files)

    # There should only be ONE studies specificed in the files provided.
    if len(studies) > 1:
        return False, "Files provided have inconsistent studies protocols"

    # INFER project using them.
    projectID = study_validation(studies[0]) # recall, studies can only have one member.

    return projectID

if __name__ == "__main__":
    anonymize_to_zip(r"C:\Users\dyt81\Downloads\TestAnonymize", "VTXGL019998_598399_V1")