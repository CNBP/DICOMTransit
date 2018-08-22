from DICOM.sort import DICOM_sort
from DICOM.convert import DICOM_convert
import os
from oshelper.folder_operation import oshelper_folder
from oshelper.file_operation import oshelper_files
from DICOM.convert import DICOM_convert

class DICOM_converter:

    @staticmethod
    def DICOM_universal_convert(input_folder, output_folder):
        """

        :param input_folder:
        :param output_folder:
        :return:
        """

        if not os.path.exists(output_folder):
            return False
        else:
            os.chdir(output_folder)

        #DICOM_converter.raw(input_folder, output_folder)
        #DICOM_converter.raw_sorted(input_folder, output_folder)
        DICOM_converter.raw_sorted_decompressed(input_folder, output_folder)
        DICOM_converter.nii(input_folder, output_folder)

    @staticmethod
    def raw(input_folder, output_folder):
        os.chdir(output_folder)
        os.mkdir("raw")
        path_raw = os.path.join(output_folder, "raw")
        file_list = oshelper_files.recursive_list(input_folder)
        oshelper_files.copy_files_to_flat_folder(file_list, path_raw)
        # Raw_BIDS

    @staticmethod
    def raw_sorted(input_folder, output_folder):
        os.chdir(output_folder)
        os.chdir(output_folder)
        oshelper_folder.create("raw_sorted")
        path_raw_sorted = os.path.join(output_folder, "raw_sorted")
        DICOM_sort.into_folder(input_folder, path_raw_sorted)
        DICOM_convert.fix_series(path_raw_sorted)

    @staticmethod
    def raw_sorted_decompressed(input_folder, output_folder):
        os.chdir(output_folder)
        oshelper_folder.create("raw_sorted_decompressed")
        path_raw_sorted_decompressed = os.path.join(output_folder, "raw_sorted_decompressed")
        DICOM_sort.into_folder(input_folder, path_raw_sorted_decompressed)
        oshelper_folder.decompress(path_raw_sorted_decompressed)
        DICOM_convert.fix_series(path_raw_sorted_decompressed)

    @staticmethod
    def nii(input_folder, output_folder):
        os.chdir(output_folder)
        oshelper_folder.create("nii")
        path_nii = os.path.join(output_folder, "nii")
        DICOM_convert.to_nii(input_folder, path_nii)
        DICOM_convert.fix_series(path_nii)


if __name__ == "__main__":
    DICOM_converter.DICOM_universal_convert(r'C:\FullyAnonymizedSubjects\2018-08-22_TestSubject3', r'C:\FullyAnonymizedSubjects\Wed3ConvertResult')
