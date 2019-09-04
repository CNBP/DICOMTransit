import logging
import inspect


logger = logging.getLogger()


def filelist_delete(file_list):
    """
    Batch delete of files when handed a list, no confirmation.
    :param file_list:
    :return:
    """
    from PUFile import filelist_delete as alias

    alias(file_list)


def flatcopy(file_list, destination_path, check_function):
    """
    Takes in a list of files and flatten them to the desintation path while ensure they are guarnteed to be unique files.
    :param file_list: the list of files from different path.
    :param destination_path:
    :param check_function: the function used to validate every single file.
    """
    from PUFile import flatcopy as alias

    alias(file_list, destination_path, check_function)


def unique_name():
    from PUFile import unique_name as alias

    return alias()


def is_name_unique(path):
    """
    Determine if the proposed file exist and suggest alternative name.
    :param path:
    :return:
    """
    from PUFile import is_name_unique as alias

    return alias(path)


def duplicates_into_folders(filelist, output_folder, iterations):
    """
    The function takes a list of files and duplicate them with unique names X times into the output folder, then return the updated input list.
    :param filelist:
    :param output_folder:
    :param iterations:
    :return:
    """
    from PUFile import duplicates_into_folders as alias

    alias(filelist, output_folder, iterations)


def zip_with_name(folder_path, output_filename):
    """
    Take in a folder, and zip to a file.
    :param folder_path:
    :param output_filename:
    :return:
    """
    from PUFile import zip_with_name as alias

    alias(folder_path, output_filename)


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
    from PUFile import full_file_path

    return full_file_path(file)


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
    from PUFile import read_json as alias

    return alias(json_path)


def dictionary_search(dictionary, target_value):
    """
    Quick and dirty search in the Dictionary for desired partial match of the TARGET_VALUE within ANY of the value within the DICTIONARY
    :param dictionary:
    :param target_value:
    :return: the key that contain the target_value from within the dictionary
    """
    from PUFile import dictionary_search as alias

    return alias(dictionary, target_value)


if __name__ == "__main__":
    json_path = r"C:\Yang\Dropbox\Machine_Learning\Recordings\2018-10-14 14-38-21_274.bmp.ROI.json"
    json_dictionary = read_json(json_path)
    print(json_dictionary)
