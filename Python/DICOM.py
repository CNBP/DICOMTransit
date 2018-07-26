import pydicom
import sys
import os
import argparse
import getpass
import logging
from pydicom.data import get_testdata_files

logging.basicConfig(stream=sys.stdout, level=logging.INFO)

def DICOM_decompressor(path):
    """
    Decompress the dicoms in case they are compressed.
    :param path:
    :return:
    """

    ds = pydicom.dcmread(path)

    ds.decompress()
    ds.save_as("Test.dcm")


def DICOM_anonymizer(path, PSCID):
    """
    Anonymize the DICOMS to remove any identifiable information
    :param path:
    :param PSCID:
    :return:
    """

    return DICOM_anonymizer_save_as(path, PSCID, path)


def DICOM_anonymizer_save_as(path, PSCID, out_path):
    """
    Anonymize the DICOMS to remove any identifiable information
    :param path:
    :param PSCID:
    :return:
    """

    success, dataset = DICOM_validator(path)
    if not success:
        return False

    dataset.PatientID = PSCID
    dataset.PatientName = PSCID
    dataset.save_as(out_path)

    return True


def DICOM_recursive_loader(path, action):
    """
    load all the files, validate and then pass to decompress or anonimize.
    :param path:
    :return:
    """


def DICOM_validator(file_path):
    """
    validate to check if the DICOM file is an actual DICOM file.
    :param file_path:
    :return:
    """
    logger = logging.getLogger(__name__)

    global dicom
    dicom = None

    from pydicom.filereader import InvalidDicomError
    from pydicom.filereader import read_file
    try:
        dicom = read_file(file_path)
    except InvalidDicomError:
        logger.info(file_path + " is not a DICOM file. Skipping")
        return False, None
    return True, dicom


def DICOM_batchValidator(dir_path):
    """
    Some basic information of the participants must be consistent across the files, such as the SCAN DATE (assuming they are not scanning across MIDNIGHT POINT)
    Birthday date, subject name, etc MUST BE CONSISTENT across a SINGLE subject's folder, RIGHT!

    :param dir_path:
    :return:
    """


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


def DICOM_computeScanAge(file_path):
    """
    Read the PatientID field which normally used as MRN number.
    :param file_path:
    :return: Age as a relative delta time object.
    """

    from dateutil.relativedelta import relativedelta

    success, DICOM = DICOM_validator(file_path)
    if not success:
        return False, None
    from datetime import datetime
    scan_date = datetime.strptime(DICOM.SeriesDate, "%Y%m%d")
    birthday = datetime.strptime(DICOM.PatientBirthDate, "%Y%m%d")
    age = relativedelta(scan_date, birthday)
    return True, age


def DICOM_retrieveMRN(file_path):
    """
    Read the PatientID field which normally used as MRN number.
    :param file_path:
    :return: MRN number, as a STRING
    """
    success, DICOM = DICOM_validator(file_path)
    if not success:
        return False, None

    MRN_number = DICOM.PatientID
    return True, MRN_number


def DICOM_TransferSyntaxCheck(transfer_syntax):
    """
    Determine if the transfer syntax symbolize LEE or JPEG compressed!
    :param transfer_syntax:
    :return: whether the DICOM files are compressed.
    """

    if not ("1.2.840.10008.1.2" in transfer_syntax):
        raise ValueError
    elif transfer_syntax == "1.2.840.10008.1.2" or transfer_syntax[18] == '1' or transfer_syntax[18] == '2':
        return True
    elif transfer_syntax[18] == '4' or transfer_syntax[18] == '5' or transfer_syntax[18] == '6':
        return False
    else:
        raise ValueError


if __name__ == '__main__':
    DICOM_decompressor("0000000A")


