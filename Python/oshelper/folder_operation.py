import os
from oshelper.file_operation import oshelper_files
class oshelper_folder:

    @staticmethod
    def is_empty(input_folder):


        # when folder does not exist
        if not os.path.exists(input_folder):
            return True

        # the the folder is not empty.
        if len(os.listdir(input_folder)) > 0:
            return False

        # must be empty then
        return True

    @staticmethod
    def create(input_folder):
        """
        Create a folder intellgently throw error if needed be.
        :param input_folder:
        :return:
        """
        if oshelper_folder.is_empty(input_folder):
            os.mkdir(input_folder)
        else:
            raise ValueError

    @staticmethod
    def decompress(input_folder):
        files_list = oshelper_files.recursive_list(input_folder)
        oshelper_files.decompress(files_list)

    @staticmethod
    def anonymize(input_folder, new_ID):
        files_list = oshelper_files.recursive_list(input_folder)
        oshelper_files.anonymize(files_list, new_ID)