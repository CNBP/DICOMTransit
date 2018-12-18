from DICOM.sort import DICOM_sort
from DICOM.decompress import DICOM_decompress
import os
from PythonUtils.folder import create, recursive_list
from PythonUtils.file import flatcopy
from DICOM.convert import DICOM_convert
from DICOM.validate import DICOM_validate

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
        os.chdir(output_folder)
        os.mkdir("raw")
        path_raw = os.path.join(output_folder, "raw")
        file_list = recursive_list(input_folder)
        flatcopy(file_list, path_raw, DICOM_validate.file)
        # Raw_BIDS

    @staticmethod
    def raw_sorted(input_folder, output_folder):
        os.chdir(output_folder)
        os.chdir(output_folder)
        create("raw_sorted")
        path_raw_sorted = os.path.join(output_folder, "raw_sorted")
        DICOM_sort.into_folder(input_folder, path_raw_sorted)
        DICOM_convert.fix_series(path_raw_sorted)

    @staticmethod
    def raw_sorted_decompressed(input_folder, output_folder):
        os.chdir(output_folder)
        create("raw_sorted_decompressed")
        path_raw_sorted_decompressed = os.path.join(output_folder, "raw_sorted_decompressed")
        DICOM_sort.into_folder(input_folder, path_raw_sorted_decompressed)
        DICOM_decompress.decompress_folder(path_raw_sorted_decompressed)
        DICOM_convert.fix_series(path_raw_sorted_decompressed)

    @staticmethod
    def nii(input_folder, output_folder):
        os.chdir(output_folder)
        create("nii")
        path_nii = os.path.join(output_folder, "nii")
        DICOM_convert.to_nii(input_folder, path_nii)
        DICOM_convert.fix_series(path_nii)


if __name__ == "__main__":
    DICOM_converter.DICOM_universal_convert(r"//ubuntudev.local/toshiba2/Mathieu's%20MRI/CHD_dTGA/NN_dTGA_001_3143750/MRI", r'C:\Users\Yang Ding\Downloads\3216279 DUMAIS BB DE MARIECLAUDE\Test')
