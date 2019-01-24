from DICOM.sort import DICOM_sort
from DICOM.decompress import DICOM_decompress
import os
from PythonUtils.folder import create, recursive_list
from PythonUtils.file import flatcopy, unique_name
from DICOM.convert import DICOM_convert
from DICOM.validate import DICOM_validate
import glob
import logging
import sys



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

        DICOM_converter.raw(input_folder, output_folder)
        DICOM_converter.raw_sorted(input_folder, output_folder)
        DICOM_converter.raw_sorted_decompressed(input_folder, output_folder)
        DICOM_converter.nii(input_folder, output_folder)

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
        logger = logging.getLogger(__name__)
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
        logger = logging.getLogger(__name__)
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
        logger = logging.getLogger(__name__)
        logger.info("Generating sorted and decompressed DICOM files:")
        path_raw_sorted_decompressed = os.path.join(output_folder, "raw_sorted_decompressed")
        DICOM_sort.into_folder(input_folder, path_raw_sorted_decompressed)
        DICOM_decompress.decompress_folder(path_raw_sorted_decompressed)
        DICOM_convert.fix_series(path_raw_sorted_decompressed)
        logger.info("Sorted decompressed files Completed!")

    @staticmethod
    def nii(input_folder, output_folder):
        """
        Create a folder,
        :param input_folder:
        :param output_folder:
        :return:
        """
        os.chdir(output_folder)
        create("nii")
        logger = logging.getLogger(__name__)
        logger.info("Generating NII files:")
        path_nii = os.path.join(output_folder, "nii")
        DICOM_convert.to_nii(input_folder, path_nii)
        DICOM_convert.fix_series(path_nii)
        logger.info("Nii files generated!")


    @staticmethod
    def DICOMOBJ_finder(input_root_folder):
        """
        Run a system search of the root input folder, find ALL instance of DICOMOBJ typically representative of raw data received from scanner etc.
        :param input_root_folder:
        :param output_root_folder:
        :return:
        """
        os.chdir(input_root_folder)
        list_path = glob.glob('**/DICOMOBJ', recursive=True)
        list_full_path = []
        for path in list_path:
            list_full_path.append(os.path.abspath(path))
        return list_full_path

    @staticmethod
    def DICOMOBJ_converter(input_root_folder, default_folder=f"DICOM_UniversalConvert-{unique_name()}"):
        """
        Create a new folder with
        :param input_root_folder:
        :return:
        """
        logger = logging.getLogger(__name__)

        path_list = DICOM_converter.DICOMOBJ_finder(input_root_folder)
        for path in path_list:
            logger.info("Begin converting folder: "+path)
            # Get higher folder path.
            path_source = os.path.dirname(path)

            # Generate the potential name for the new path.
            path_result = os.path.join(path_source, default_folder)

            # intellgently create the folder if needed be.
            create(path_result)

            # Trigger the subject specific convertion.
            DICOM_converter.DICOM_universal_convert(path, path_result)
            logger.info(f"Finished converting: {path}")


if __name__ == "__main__":
    input_root_folder = r"/toshiba2/Mathieu's MRI/CHD_dTGA/NN_dTGA_011_3190535/MRI/ClinicalPACS"
    DICOM_converter.DICOMOBJ_converter(input_root_folder)
