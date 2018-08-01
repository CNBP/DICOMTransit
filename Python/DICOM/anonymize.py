from DICOM.validate import DICOM_validator
from DICOM.elements import DICOM_updateElement


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

    success1, _ = DICOM_updateElement(path, "PatientID", PSCID, out_path)
    success2, _ = DICOM_updateElement(path, "PatientName", PSCID, out_path)

    if success1 and success2:
        return True
    else:
        return False
    return True