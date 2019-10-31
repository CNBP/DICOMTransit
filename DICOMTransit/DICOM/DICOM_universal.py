#!/usr/local/bin/python

from DICOMTransit.DICOM.sort import DICOM_sort
from DICOMTransit.DICOM.decompress import DICOM_decompress
import os
from PythonUtils.PUFolder import create, recursive_list
from PythonUtils.PUFile import flatcopy, unique_name
from DICOMTransit.DICOM.convert import DICOM_convert
from DICOMTransit.DICOM.validate import DICOM_validate
import glob
import logging
import sys
from pathlib import Path

logger = logging.getLogger()


class DICOM_converter:
    @staticmethod
    def DICOM_universal_convert(input_folder, output_folder):
        """
        A universal converter of inputfolder and check all files in there for DICOM before converting them into a sets of standarized format of various level of update.
        :param input_folder:
        :param output_folder:
        :return:
        """

        if not os.path.exists(output_folder):
            return False
        else:
            os.chdir(output_folder)

        # DICOM_converter.raw(input_folder, output_folder)
        DICOM_converter.raw_sorted(input_folder, output_folder)
        # DICOM_converter.raw_sorted_decompressed(input_folder, output_folder)
        # DICOM_converter.nii(input_folder, output_folder)
        from pathlib import Path

        nii_cube = Path.joinpath(Path(output_folder), "raw_sorted_decompressed")
        nii_cube_output = Path.joinpath(Path(output_folder), "nii")
        DICOM_converter.nii_cube_mricron(nii_cube, nii_cube_output)

    @staticmethod
    def raw(input_folder, output_folder):
        """
        FLATCOPY (with timestampe to avoid naming duplications) to a an output folder with raw prefix.
        :param input_folder:
        :param output_folder:
        :return:
        """
        os.chdir(output_folder)
        os.mkdir("raw")
        logger.info("Backup up untouched raw files:")
        path_raw = os.path.join(output_folder, "raw")
        file_list = recursive_list(input_folder)
        flatcopy(file_list, path_raw, DICOM_validate.file)
        logger.info("Raw backup completed!")

    @staticmethod
    def raw_sorted(input_folder, output_folder):
        """
        FLATCOPY (with timestampe to avoid naming duplications) to a an output folder with raw prefix, then SORT THEM with proper protocole series acquisition number.
        :param input_folder:
        :param output_folder:
        :return:
        """
        os.chdir(output_folder)
        os.chdir(output_folder)
        create("raw_sorted")
        logger.info("Generating sorted raw files:")
        path_raw_sorted = os.path.join(output_folder, "raw_sorted")
        DICOM_sort.into_folder(input_folder, path_raw_sorted)
        DICOM_convert.fix_series(path_raw_sorted)
        logger.info("Sorted raw files completed!")

    @staticmethod
    def raw_sorted_decompressed(input_folder, output_folder):
        """
        FLATCOPY (with timestampe to avoid naming duplications) to a an output folder with raw prefix, then SORT THEM with proper protocole series acquisition number, then decompress everything within the folder.
        :param input_folder:
        :param output_folder:
        :return:
        """
        os.chdir(output_folder)
        create("raw_sorted_decompressed")
        logger.info("Generating sorted and decompressed DICOM files:")
        path_raw_sorted_decompressed = os.path.join(
            output_folder, "raw_sorted_decompressed"
        )
        DICOM_sort.into_folder(input_folder, path_raw_sorted_decompressed)
        DICOM_decompress.decompress_folder(path_raw_sorted_decompressed)
        DICOM_convert.fix_series(path_raw_sorted_decompressed)
        logger.info("Sorted decompressed files Completed!")

    @staticmethod
    def nii(input_folder, output_folder):
        """
        Take a folder, recursively traverse through all its subfolders, convert each subfolder into a NII file
        :param input_folder:
        :param output_folder:
        :return:
        """
        os.chdir(output_folder)
        create("nii")
        logger.info("Generating NII files:")
        path_nii = os.path.join(output_folder, "nii")
        DICOM_convert.to_nii(input_folder, path_nii)
        DICOM_convert.fix_series(path_nii)
        logger.info("Nii files generated!")

    @staticmethod
    def nii_cube_mricron(input_folder, output_folder):
        """
        Special function used to handle CUBE sequences which require MRICRON conversion
        :param input_folder:
        :param output_folder:
        :return:
        """
        list_cube = DICOM_converter.DICOM_CUBE_finder(input_folder)
        os.chdir(output_folder)
        for folder_cube in list_cube:
            input_path = Path.joinpath(input_folder, folder_cube)
            DICOM_convert.to_nii_mricron(input_path, output_folder)
        logger.info("CUBE Nii files generated!")

    @staticmethod
    def DICOMOBJ_finder(input_root_folder):
        """
        Run a system search of the root input folder, find ALL instance of DICOMOBJ typically representative of raw data received from scanner etc.
        :param input_root_folder:
        :param output_root_folder:
        :return:
        """
        os.chdir(input_root_folder)
        list_path = glob.glob("**/DICOMOBJ", recursive=True)
        list_full_path = []
        for path in list_path:
            list_full_path.append(os.path.abspath(path))
        return list_full_path

    @staticmethod
    def DICOM_CUBE_finder(input_root_folder):
        """
        Find all folders with "CUBE" in their name.
        :param input_root_folder:
        :return:
        """
        os.chdir(input_root_folder)
        list_folders = os.listdir()
        list_CUBE_folders = []
        for folder in list_folders:
            if "CUBE" in str.upper(folder):
                list_CUBE_folders.append(folder)
        return list_CUBE_folders

    @staticmethod
    def DICOMOBJ_converter(
        input_root_folder, default_folder=f"DICOM_UniversalConvert-{unique_name()}"
    ):
        """
        Create a new folder with
        :param input_root_folder:
        :return:
        """

        path_list = DICOM_converter.DICOMOBJ_finder(input_root_folder)
        for path in path_list:
            logger.info("Begin converting folder: " + path)
            # Get higher folder path.
            path_source = os.path.dirname(path)

            # Generate the potential name for the new path.
            path_result = os.path.join(path_source, default_folder)

            # intellgently create the folder if needed be.
            create(path_result)

            # Trigger the subject specific convertion.
            DICOM_converter.DICOM_universal_convert(path, path_result)
            logger.info(f"Finished converting: {path}")

    @staticmethod
    def DICOM_universal_convert_default(
        input_root_folder, name_default_folder=f"DICOM_UniversalConvert-{unique_name()}"
    ):
        """
        Create a new folder with
        :param input_root_folder:
        :return:
        """

        logger.info("Begin converting folder: " + input_root_folder)

        # Generate the potential name for the new path.
        path_result = f"{input_root_folder}-{name_default_folder}"

        # intellgently create the folder if needed be.
        create(path_result)

        # Trigger the subject specific convertion.
        DICOM_converter.DICOM_universal_convert(input_root_folder, path_result)
        logger.info(f"Finished converting: {input_root_folder}")

    #
    # @staticmethod
    # def fix_dcm2nii_filename(input_nii_folder):
    #     """
    #     A method to fix file names outputted by dcm2nii where they are overly long and not descriptive.
    #
    #     s[0-9]*a
    #
    #     :return:
    #     """
    #     import re
    #     files_list = os.listdir(input_nii_folder)
    #
    #     sequence_prefix="null"
    #
    #     sequence_list = []
    #
    #     for file in files_list:
    #         series_finder = re.compile("s(\d*)a")
    #         regex_match_result = series_finder.match("file")
    #
    #         if regex_match_result is not None:
    #
    #             # Find the file matching the pattern.
    #             sequence_list.append(regex_match_result[1])
    #         else:
    #             continue
    #
    #     for file in files_list:
    #         for sequence_number in  sequence_list:
    #             if sequence_prefix in file:

    # Find the XXX_sequence corredponding to that.

    # Rename the CUBE sequence to convert this properly.


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    if sys.argv is not None:
        logger.info(f"This is the name of the script: {sys.argv[0]}")
        logger.info(f"Number of arguments: {len(sys.argv)}")
        logger.info(f"The arguments are: {str(sys.argv)}")

    if len(sys.argv) != 3:
        input_root_folder = r"/toshiba2/Mathieus_MRI_Sab/dTGA_toConvert/dTGA_025_post_14-06-2019_FromClinicalPACs"
        input_root_folder = r"/tmp/VXS38"
    else:
        logger.info(f"First Argument, input root folder path:{sys.argv[1]}")
        logger.info(f"Second Argument, output folder path: {sys.argv[2]}")
        input_root_folder = sys.argv[1]
        output_folder = sys.argv[2]

    DICOM_converter.DICOM_universal_convert_default(input_root_folder)
