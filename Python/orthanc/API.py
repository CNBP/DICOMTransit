import os
import tempfile
from orthanc.query import orthanc_query
from LORIS.helper import LORIS_helper
from PythonUtils.file import unique_name
import logging

logger = logging.getLogger()

def check_status():
    url, user, password = get_prod_orthanc_credentials()
    try:
        endpoint = f"{url}patients/"
        reseponse_code, _ = orthanc_query.getOrthanc(endpoint, user, password)
        success = LORIS_helper.is_response_success(reseponse_code, 200)
    except:
        # in case any thing goes wrong
        return False
    return success


def get_dev_orthanc_credentials():
    from settings import config_get
    url = config_get("DevOrthancIP")
    user = config_get("DevOrthancUser")
    password = config_get("DevOrthancPassword")
    return url, user, password

def get_prod_orthanc_credentials():
    from settings import config_get
    url = config_get("ProdOrthancIP")
    user = config_get("ProdOrthancUser")
    password = config_get("ProdOrthancPassword")
    return url, user, password


def get_list_of_subjects_noauth(orthanc_URL):
    """
    Get a list of subjects from a .env predefined orthanc server.
    :return: the lsit of all subjects in the orthanc server
    """
    endpoint = f"{orthanc_URL}patients/"

    reseponse_code, list_subjects = orthanc_query.getOrthanc_noauth(endpoint)

    assert (LORIS_helper.is_response_success(reseponse_code, 200))
    return list_subjects

def get_list_of_subjects(orthanc_URL, orthanc_user, orthanc_password):
    """
    Get a list of subjects from a .env predefined orthanc server.
    :return: the lsit of all subjects in the orthanc server
    """
    endpoint = f"{orthanc_URL}patients/"

    reseponse_code, list_subjects = orthanc_query.getOrthanc(endpoint, orthanc_user, orthanc_password)

    assert (LORIS_helper.is_response_success(reseponse_code, 200))
    return list_subjects

def get_subject_zip(orthanc_URL_with_UUID, orthaner_user, orthanc_password):
    """
    Obtain the actual zip files of the subject based on the UUID given and unzip them to a temporary folder, and return it.
    :param orthanc_URL_with_UUID:
    :return: the temporary folder object which contain the reference to the folder in the .name attribute
    """
    
    status, local_zip_file_path = orthanc_query.getPatientZipOrthanc(orthanc_URL_with_UUID, orthaner_user, orthanc_password)
    assert (LORIS_helper.is_response_success(status, 200))
    assert (os.path.exists(local_zip_file_path))

    logger.info("Subject ZIP downloaded.")

    return local_zip_file_path

def unpack_subject_zip(zip_file):
    

    # Create the temporary directory
    folder = tempfile.TemporaryDirectory(prefix=unique_name())

    logger.debug("Subject ZIP temporary location created at:"+folder.name)
    logger.debug("Unzipping to that location")
    # Unzip into the temporary directory.
    orthanc_query.flatUnZip(zip_file, folder.name)

    logger.debug("Unzip completed. ")
    # Remove the zip file.
    os.remove(zip_file)
    logger.debug("Removing zip archived.")
    return folder

def delete_subject(subjectUUID: str):
    """
    API to delete subject from the production Orthanc instance.
    :param subjectUUID:
    :return: successful deletion status.
    """
    url, user, password = get_prod_orthanc_credentials()
    reseponse_code, _ = orthanc_query.deleteOrthanc(f"patients/{subjectUUID}", user, password)
    return LORIS_helper.is_response_success(reseponse_code, 200)