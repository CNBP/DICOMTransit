import os
import datetime
import logging
import shutil
from DICOM.validate import DICOM_validate
from DICOM.decompress import DICOM_decompress


class oshelper_files:

    @staticmethod
    def recursive_list_files(root_dicom_path):
        """
        load all the files, validate and then pass to decompress or anonimize.
        :param root_dicom_path:
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

    @staticmethod
    def decompress_folder(input_folder):
        files_list = oshelper_files.recursive_list_files(input_folder)
        oshelper_files.decompress_files(files_list)

    @staticmethod
    def decompress_files(file_list):
        """
        Decompress all compressed files in the list OVERWRITE the files.
        :param file_list:
        :return:
        """

        for file in file_list:
            logger = logging.getLogger("Compression checking file: " + file)

            # find if the file is DICOM, if not, skip this file.
            is_DICOM_file, _ = DICOM_validate.file(file)
            if not is_DICOM_file:
                continue

            # check if the file is compressed.
            TransferSyntax = DICOM_decompress.get_transferSyntax(file)
            try:
                RequireDecompression = DICOM_decompress.check_decompression(TransferSyntax)
                if RequireDecompression:
                    DICOM_decompress.save_as(file, file)

            except ValueError:
                logger.info("Unknwonw DICOM syntax. You sure it is DICOM?")
                continue

    @staticmethod
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
            is_DICOM_file, _ = DICOM_validate.file(file)
            if not is_DICOM_file:
                continue

            # get the final path name.
            file_name = os.path.basename(file)
            destination_path_name = os.path.join(destination_path, file_name)

            # check if the final path is unique.
            unique, new_name = oshelper_files.is_file_name_unique(destination_path_name)

            # append date time microsecond string if the file is not unique.
            if not unique:
                destination_path_name = new_name

            copyfile(file, destination_path_name)

    @staticmethod
    def is_file_name_unique(path):
        """
        Determine if the proposed file exist and suggest alternative name.
        :param path:
        :return:
        """
        if os.path.exists(path):
            timestamp = datetime.datetime.now().isoformat()
            timestamp = timestamp.replace(':', '')  # Remove : which are not compatible with string

            file, ext = os.path.splitext(path)

            return False, file + "_" + timestamp + "_" + ext
        else:
            return True, path

    @staticmethod
    def zip_with_name(folder_path, output_filename):
        shutil.make_archive(output_filename, 'zip', folder_path)