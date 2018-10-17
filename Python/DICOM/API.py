from tempfile import TemporaryDirectory
from DICOM.anonymize import DICOM_anonymize
from shutil import copyfile
import os

def anonymize_files(files):
    """
    Anaonymize the files given using the name provided. WIP!!!
    :param new_name: the anonymize name for the new subjects
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

