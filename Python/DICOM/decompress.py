import logging
import os
import pydicom, subprocess
import platform
from DICOM.validate import DICOM_validator
from pydicom.filereader import read_file_meta_info


def DICOM_decompress(input_file, out_put):
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
        subprocess.check_output(['dcmdjpeg', input_file, out_put])

    # When dcmdjpeg has errors
    except subprocess.CalledProcessError as e:
        logger.info(e.output)
        ErrorMessage = "File type not compatible for " + input_file
        logger.info(ErrorMessage)
        return False, ErrorMessage

    # all other unanticipated errors:
    except:
        ErrorMessage = "Exception encountered while calling DCMDJPEG. Contact author to investigate, attach " + input_file
        logger.info(ErrorMessage)
        return False, ErrorMessage

    # Ensure that data is actually written out.
    if not os.path.exists(out_put):
        ErrorMessage = "Cannot write out final file for some reason " + input_file
        logger.info(ErrorMessage)
        return False, ErrorMessage

    # Test read the data after writing.
    try:
        data = pydicom.read_file(out_put)
    except:
        ErrorMessage = "Exception encountered while verifying the proper writing out of the DICOM data. Contact author to investigate, attach " + input_file
        logger.info(ErrorMessage)
        return False, ErrorMessage

    logger.info("Success writen " + input_file + " to " + out_put)
    return True, "All good"

def DICOM_RequireDecompression(transfer_syntax):
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


def DICOM_TransferSyntax(file_path):
    """
    Used to find if a file is compressed
    :param file_path:
    :return:
    """

    # Validity check:
    success, DICOM = DICOM_validator(file_path)
    if not success:
        raise IOError

    # Now read the meta information.
    dicom_file = read_file_meta_info(file_path)
    transfer_syntax = dicom_file.TransferSyntaxUID

    return transfer_syntax

def DICOM_QuickTransferSyntaxCheck(file_path):
    # Validity check:
    success, DICOM = DICOM_validator(file_path)
    if not success:
        raise IOError
    import dicom

    # Now read the meta information.
    if DICOM.file_meta.TransferSyntaxUID in dicom.dataset.NotCompressedPixelTransferSyntaxes:
        return False
    else:
        return True