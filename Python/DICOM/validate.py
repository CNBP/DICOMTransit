import sys
import logging

logging.basicConfig(stream=sys.stdout, level=logging.INFO)

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


#if __name__ == '__main__':
