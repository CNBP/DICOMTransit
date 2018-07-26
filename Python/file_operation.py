import time
import os
import logging
import sys
from DICOM import DICOM_validator, DICOM_RequireDecompression, DICOM_TransferSyntax

def recursive_list_files(root_dicom_path):
    """
    load all the files, validate and then pass to decompress or anonimize.
    :param path:
    :return:
    """
    global file_list
    file_list = []

    for root, directories, filenames in os.walk(root_dicom_path):
        #for directory in directories:
            #file_list.append(os.path.join(root, directory))
        for filename in filenames:
            file_list.append(os.path.join(root,filename))
    return file_list


def get_file_name(path):
    file_name = os.path.basename(path)
    return file_name

def decompress_folder(file_list):
    """
    Decompress all compressed file within the lsit.
    :param file_list:
    :return:
    """

    for file in file_list:
        logger = logging.getLogger("Compression checking file: " + file)

        # find if the file is DICOM, if not, skip this file.
        is_DICOM_file, _ = DICOM_validator(file)
        if not is_DICOM_file:
            continue

        # check if the file is compressed.
        TransferSyntax = DICOM_TransferSyntax(file)
        try:
            RequireDecompression = DICOM_RequireDecompression(TransferSyntax)
            # if RequireDecompression:
                # DecompressFile

        except ValueError:
            logger.info("Unknwonw DICOM syntax. You sure it is DICOM?")
            continue



def copy_files_to_flat_folder(file_list, destination_path):
    """
    Takes in a list of files and flatten them to the desintation path while ensure they are guarnteed to be unique files.
    :param file_list: the list of files from different path.
    :param destination_path:
    """
    logger = logging.getLogger(__name__)
    logger.info("Copying checking and checking files to destination: " + destination_path)

    from shutil import copyfile

    for file in file_list:

        # find if the file is DICOM, if not, skip this file.
        is_DICOM_file, _ = DICOM_validator(file)
        if not is_DICOM_file:
            continue

        # get the final path name.
        file_name = get_file_name(file)
        destination_path_name = os.path.join(destination_path, file_name)

        # check if the final path is unique.
        unique, new_name = is_file_name_unique(destination_path_name)

        # append date time microsecond string if the file is not unique.
        if not unique:
            destination_path_name = new_name

        copyfile(file, destination_path_name)

def is_file_name_unique(path):
    """
    Determine if the proposed file exist and suggest alternative name.
    :param path:
    :return:
    """
    import datetime
    timestamp = datetime.datetime.now().isoformat()
    timestamp = timestamp.replace(':','') # string : which are incompatible with path
    if os.path.exists(path):
        return False, path + "_" + timestamp
    else:
        return True, path

def zip_with_name(path, name):
    return