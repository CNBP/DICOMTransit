import time
import os
import logging
import sys

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

def make_flat_folder_structure():
    return

def zip_with_name(path, name):
    return