import pydicom

from DICOM.validate import DICOM_validator


def DICOM_decompressor(path):
    """
    Decompress the dicoms in case they are compressed.
    :param path:
    :return:
    """

    ds = pydicom.dcmread(path)

    ds.decompress()
    ds.save_as("Test.dcm")


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
    from pydicom.filereader import read_file_meta_info

    # Validity check:
    success, DICOM = DICOM_validator(file_path)
    if not success:
        raise IOError

    # Now read the meta information.
    dicom_file = read_file_meta_info(file_path)
    transfer_syntax = dicom_file.TransferSyntaxUID

    return transfer_syntax