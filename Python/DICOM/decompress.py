import logging
import os
import pydicom, subprocess
from PythonUtils.folder import recursive_list
from tqdm import tqdm


from pydicom.filereader import read_file_meta_info

from DICOM.validate import DICOM_validate

class DICOM_decompress:

    @staticmethod
    def save_as(input_file, out_put):
        """
        A wrapper for DCMDJPEG for decompression
        :param input_file:
        :param out_put:
        :return:
        """
        logger = logging.getLogger(__name__)

        if os.path.exists(out_put):
            return False, "Output_exist already."

        try:
            # SUPER IMPORTANT! MAKE SURE DCMDJPEG is in the system path!
            subprocess.check_output(['dcmdjpeg', input_file, out_put])

        # When dcmdjpeg has errors
        except subprocess.CalledProcessError as e:
            logger.info(e)
            ErrorMessage = "File type not compatible for " + input_file
            logger.info(ErrorMessage)
            return False, ErrorMessage
        except Exception as e:
            logger.info(e)
            ErrorMessage = "DCMDJPEG decompression call failed! Make sure DCMDJPEG is in your SYSTEMOS PATH and then check your input file:" + input_file
            logger.info(ErrorMessage)
            return False, ErrorMessage

        # Ensure that data is actually written out.
        if not os.path.exists(out_put):
            ErrorMessage = "Cannot write out final file for some reason " + input_file
            logger.info(ErrorMessage)
            return False, ErrorMessage

        # Test read the data after writing.
        try:
            pydicom.read_file(out_put)
        except Exception as e:
            ErrorMessage = "Exception encountered while verifying the proper writing out of the DICOM data. Contact author to investigate, attach " + input_file
            logger.info(e)
            logger.info(ErrorMessage)
            return False, ErrorMessage

        logger.info("Success written " + input_file + " to " + out_put)
        return True, "All good"

    @staticmethod
    def check_decompression(transfer_syntax):
        """
        Determine if the transfer syntax symbolize LEE or JPEG compressed!
        :param transfer_syntax:
        :return: whether the DICOM files are compressed.
        """

        if not ("1.2.840.10008.1.2" in transfer_syntax):
            raise ValueError
        elif transfer_syntax == "1.2.840.10008.1.2" or transfer_syntax[18] == '1' or transfer_syntax[18] == '2':
            return False
        elif transfer_syntax[18] == '4' or transfer_syntax[18] == '5' or transfer_syntax[18] == '6':
            return True
        else:
            raise ValueError

    @staticmethod
    def get_transferSyntax(file_path):
        """
        Used to find if a file is compressed
        :param file_path:
        :return:
        """

        # Validity check:
        success, _ = DICOM_validate.file(file_path)
        if not success:
            raise IOError

        # Now read the meta information.
        dicom_file = read_file_meta_info(file_path)
        transfer_syntax = dicom_file.TransferSyntaxUID

        return transfer_syntax

    @staticmethod
    def check_decompression_quick(file_path):
        # Validity check:
        success, DICOM = DICOM_validate.file(file_path)
        if not success:
            raise IOError
        import pydicom.uid

        # Now read the meta information.
        if DICOM.file_meta.TransferSyntaxUID in pydicom.uid.UncompressedPixelTransferSyntaxes:
            return True
        else:
            return False

    @staticmethod
    def filelist(file_list):
        """
        Decompress all compressed files in the list OVERWRITE the files.
        :param file_list:
        :return:
        """
        logger = logging.getLogger("Decompressing files")

        for file in tqdm(file_list):

            logger.info("Decompressing: " + file)

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
    def decompress_folder(input_folder):
        files_list = recursive_list(input_folder)
        DICOM_decompress.filelist(files_list)