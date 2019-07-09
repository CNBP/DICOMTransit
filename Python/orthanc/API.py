import os
import tempfile
from orthanc.query import orthanc_query, orthanc_credential
from LORIS.helper import LORIS_helper
from PythonUtils.file import unique_name
import logging
from typing import List
import urllib.parse
import json

logger = logging.getLogger()


def check_dev_orthanc_status() -> bool:
    """
    Check the orthanc status to ensure that it is online.
    :return:
    """
    credential = get_dev_orthanc_credentials()
    try:

        endpoint = urllib.parse.urljoin(credential.url, "studies")
        reseponse_code, _ = orthanc_query.getOrthanc(endpoint, credential)
        success = LORIS_helper.is_response(reseponse_code, 200)
    except:
        # in case any thing goes wrong
        return False
    return success


def check_prod_orthanc_status() -> bool:
    """
    Check the orthanc status to ensure that it is online.
    :return:
    """
    credential = get_prod_orthanc_credentials()
    try:
        endpoint = urllib.parse.urljoin(credential.url, "studies")
        reseponse_code, _ = orthanc_query.getOrthanc(endpoint, credential)
        success = LORIS_helper.is_response(reseponse_code, 200)
    except:
        # in case any thing goes wrong
        return False
    return success


def get_dev_orthanc_credentials() -> orthanc_credential:
    """
    Obtain the Development Orthanc instance credential
    :return:
    """
    from settings import config_get

    url = config_get("DevOrthancIP")
    user = config_get("DevOrthancUser")
    password = config_get("DevOrthancPassword")
    return orthanc_credential(url, user, password)


def get_prod_orthanc_credentials() -> orthanc_credential:
    """
    Obtain the Production Orthanc instance credential
    :return:
    """
    from settings import config_get

    url = config_get("ProdOrthancIP")
    user = config_get("ProdOrthancUser")
    password = config_get("ProdOrthancPassword")
    return orthanc_credential(url, user, password)


def get_list_of_subjects_noauth(orthanc_URL: str) -> List[str]:
    """
    Get a list of subjects from a .env predefined orthanc server.
    :return: the lsit of all subjects in the orthanc server
    """
    endpoint = urllib.parse.urljoin(orthanc_URL, "patients/")

    reseponse_code, list_subjects = orthanc_query.getOrthanc_noauth(endpoint)

    if not (LORIS_helper.is_response(reseponse_code, 200)):
        raise ConnectionError("LORIS server did not return list of subjects. ")
    return list_subjects


def get_all_subject_StudyUIDs(credential: orthanc_credential) -> List[List[str]]:
    """
    Get a list of STUDIES from a .env predefined orthanc server.
    :return: the list of all studies in the orthanc server
    """
    endpoint = urllib.parse.urljoin(credential.url, "studies/")

    reseponse_code, list_studies = orthanc_query.getOrthanc(endpoint, credential)

    if not LORIS_helper.is_response(reseponse_code, 200):
        raise ConnectionError("LORIS server did not return list of subjects. ")

    return list_studies


def get_StudyUID_zip(
    orthanc_URL_with_StudyUID: str, credential: orthanc_credential
) -> str:
    """
    Obtain the actual zip files of the subject based on the StudyUID given and unzip them to a temporary folder, and return it.
    :param orthanc_URL_with_StudyUID:
    :return: the temporary folder object which contain the reference to the folder in the .name attribute
    """

    status, local_zip_file_path = orthanc_query.getZipFromOrthanc(
        orthanc_URL_with_StudyUID, credential
    )
    if not (LORIS_helper.is_response(status, 200)):
        raise ConnectionError("Orthanc is not reachable!")

    if not os.path.exists(local_zip_file_path):
        raise FileNotFoundError("Local zip file to be uploaded has not been found!")

    logger.info("Subject ZIP downloaded.")

    return local_zip_file_path


def unpack_subject_zip(
    zip_file: str, temp_folder: str = "/toshiba4/tmp"
) -> tempfile.TemporaryDirectory:
    """
    Unpack the given Zip file to a temporary folder and return the reference to that temporary folder.
    :param zip_file:
    :return:
    """

    # Create the temporary directory at the location specified, auto erased later as system reclaim resource.
    folder = tempfile.TemporaryDirectory(prefix=unique_name(), dir=temp_folder)

    logger.debug("Subject ZIP temporary location created at:" + folder.name)
    logger.debug("Unzipping to that location")
    # Unzip into the temporary directory.
    orthanc_query.flatUnZip(zip_file, folder.name)

    logger.debug("Unzip completed. ")

    # Remove the zip file.
    os.remove(zip_file)
    logger.debug("Removing zip archived.")
    return folder


def delete_study(StudyUID: str) -> bool:
    """
    API to delete subject from the production Orthanc instance.
    :param StudyUID:
    :return: successful deletion status.
    """
    credential = get_prod_orthanc_credentials()
    reseponse_code, _ = orthanc_query.deleteOrthanc(f"studies/{StudyUID}", credential)
    return LORIS_helper.is_response(reseponse_code, 200)
