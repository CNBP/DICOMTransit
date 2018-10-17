import os


import tempfile
from orthanc.query import orthanc_query
from LORIS.helper import LORIS_helper

def get_list_of_subjects():
    """
    Get a list of subjects from a .env predefined orthanc server.
    :return: the lsit of all subjects in the orthanc server
    """
    reseponse_code, list_subjects = orthanc_query.getOrthanc("patients/")
    assert (LORIS_helper.is_response_success(reseponse_code, 200))
    return list_subjects

def get_subject_zip(subject_UUID):
    """
    Obtain the actual zip files of the subject based on the UUID given and unzip them to a temporary folder, and return it.
    :param subject_UUID:
    :return: the temporary folder object which contain the reference to the folder in the .name attribute
    """
    status, zip_file = orthanc_query.getPatientZipOrthanc(subject_UUID)
    assert (LORIS_helper.is_response_success(status, 200))
    assert (os.path.exists(zip_file))

    # Create the temporary directory
    folder = tempfile.TemporaryDirectory(prefix=subject_UUID)

    # Unzip into the temporary directory.
    orthanc_query.flatUnZip(zip_file, folder.name)

    # Remove the zip file.
    os.remove(zip_file)

    return folder
