import os
import logging
import shutil
from datetime import datetime
from tqdm import tqdm
import sys
import json
import inspect


logger = logging.getLogger()


def filelist_delete(file_list):
    """
    Batch delete of files when handed a list, no confirmation.
    :param file_list:
    :return:
    """
    for file in tqdm(file_list, position=0):
        os.remove(file)


def flatcopy(file_list, destination_path, check_function):
    """
    Takes in a list of files and flatten them to the desintation path while ensure they are guarnteed to be unique files.
    :param file_list: the list of files from different path.
    :param destination_path:
    :param check_function: the function used to validate every single file.
    """
    logger = logging.getLogger()
    logger.debug(
        f"Copying checking and checking files to destination: {destination_path}"
    )

    from shutil import copyfile

    for file in tqdm(file_list, position=0):

        # find if the file is DICOM, if not, skip this file.
        if check_function is not None:
            check_passes, _ = check_function(file)
            if not check_passes:
                continue

        # get the final path name.
        file_name = os.path.basename(file)
        destination_path_name = os.path.join(destination_path, file_name)

        # check if the final path is unique.
        is_unique, new_name = is_name_unique(destination_path_name)

        # append date time microsecond string if the file is not unique.
        if not is_unique:
            destination_path_name = new_name

        copyfile(file, destination_path_name)


def unique_name():

    timestamp = datetime.now().isoformat(sep="T", timespec="auto")
    name = timestamp.replace(":", "_")
    return name


def is_name_unique(path):
    """
    Determine if the proposed file exist and suggest alternative name.
    :param path:
    :return:
    """
    if os.path.exists(path):

        file, ext = os.path.splitext(path)

        return False, f"{file}_{unique_name()}_{ext}"
    else:
        return True, path


def duplicates_into_folders(filelist, output_folder, iterations):
    """
    The function takes a list of files and duplicate them with unique names X times into the output folder, then return the updated input list.
    :param filelist:
    :param output_folder:
    :param iterations:
    :return:
    """
    from folder import recursive_list

    logger.debug(f"Duplication files for {str(iterations)} iteraitons.")
    # Duplicate the folder x times
    for x in range(0, iterations):
        # each time, duplicate all the files within it
        for file in tqdm(filelist, position=0):
            # Make sure to assign UNIQUE name.
            new_file_name = os.path.join(output_folder, f"{unique_name()}.png")
            shutil.copyfile(file, new_file_name)

    # Make DIR if it does not already exist.
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Recursively list the output folder
    updated_file_list = recursive_list(output_folder)

    return updated_file_list


def zip_with_name(folder_path, output_filename):
    """
    Take in a folder, and zip to a file.
    :param folder_path:
    :param output_filename:
    :return:
    """
    shutil.make_archive(output_filename, "zip", folder_path)


def current_funct_name():
    """
    Return the current functions' name. Used to allow better snippets generation.
    Source: https://www.stefaanlippens.net/python_inspect/
    :return:
    """
    return inspect.stack()[1][3]


def full_file_path(file):
    """
    When given a file reference, it will tell you its full path.
    :param file:
    :return:
    """
    dir_path = os.path.dirname(os.path.realpath(file))
    return dir_path


def parental_funct_name():
    """
        Return the current functions' name. Used to allow better snippets generation.
        Source: https://www.stefaanlippens.net/python_inspect/
        :return:
        """
    return inspect.stack()[2][3]


def read_json(json_path):
    """
    Load JSON and return it as a dictionary.
    :param json_path:
    :return:
    """
    if not os.path.exists(json_path):
        return None

    json_file = open(json_path, "r")
    json_dictionary = json.loads(json_file)
    return json_dictionary


def dictionary_search(dictionary, target_value):
    """
    Quick and dirty search in the Dictionary for desired partial match of the TARGET_VALUE within ANY of the value within the DICTIONARY
    :param dictionary:
    :param target_value:
    :return: the key that contain the target_value from within the dictionary
    """
    for key_value_pair in dictionary:
        for current_value in dictionary[key_value_pair]:
            if target_value in current_value:
                return key_value_pair
    return None


if __name__ == "__main__":
    json_path = r"C:\Yang\Dropbox\Machine_Learning\Recordings\2018-10-14 14-38-21_274.bmp.ROI.json"
    json_dictionary = read_json(json_path)
    print(json_dictionary)
