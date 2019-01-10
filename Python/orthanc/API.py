import os
import tempfile
from orthanc.query import orthanc_query
from LORIS.helper import LORIS_helper
from PythonUtils.file import unique_name

import logging
import sys

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logger = logging.getLogger(__name__)

def get_dev_orthanc_credentials():
    from settings import get
    url = get("DevOrthancIP")
    user = get("DevOrthancUser")
    password = get("DevOrthancPassword")
    return url, user, password

def get_prod_orthanc_credentials():
    from settings import get
    url = get("ProdOrthancIP")
    user = get("ProdOrthacUser")
    password = get("ProdOrthancPassword")
    return url, user, password


def get_list_of_subjects_noauth(orthanc_URL):
    """
    Get a list of subjects from a .env predefined orthanc server.
    :return: the lsit of all subjects in the orthanc server
    """
    endpoint = orthanc_URL + "patients/"

    reseponse_code, list_subjects = orthanc_query.getOrthanc_noauth(endpoint)

    assert (LORIS_helper.is_response_success(reseponse_code, 200))
    return list_subjects

def get_list_of_subjects(orthanc_URL, orthanc_user, orthanc_password):
    """
    Get a list of subjects from a .env predefined orthanc server.
    :return: the lsit of all subjects in the orthanc server
    """
    endpoint = orthanc_URL + "patients/"

    reseponse_code, list_subjects = orthanc_query.getOrthanc(endpoint, orthanc_user, orthanc_password)

    assert (LORIS_helper.is_response_success(reseponse_code, 200))
    return list_subjects

def get_subject_zip(orthanc_URL_with_UUID, orthaner_user, orthanc_password):
    """
    Obtain the actual zip files of the subject based on the UUID given and unzip them to a temporary folder, and return it.
    :param orthanc_URL_with_UUID:
    :return: the temporary folder object which contain the reference to the folder in the .name attribute
    """
    status, zip_file = orthanc_query.getPatientZipOrthanc(orthanc_URL_with_UUID, orthaner_user, orthanc_password)
    assert (LORIS_helper.is_response_success(status, 200))
    assert (os.path.exists(zip_file))

    logger.info("Subject ZIP downloaded.")
    # Create the temporary directory
    folder = tempfile.TemporaryDirectory(prefix=unique_name())

    logger.info("Subject ZIP temporary location created at:"+folder.name)
    logger.info("Unzipping to that location")
    # Unzip into the temporary directory.
    orthanc_query.flatUnZip(zip_file, folder.name)

    logger.info("Unzip completed. ")
    # Remove the zip file.
    os.remove(zip_file)
    logger.info("Removing zip archived.")

    return folder
