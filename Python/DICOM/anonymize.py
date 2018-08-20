from DICOM.validate import DICOM_validate
from DICOM.elements import DICOM_elements


class DICOM_anonymize:

    @staticmethod
    def save(path, PSCID):
        """
        Anonymize the DICOMS to remove any identifiable information
        :param path:
        :param PSCID:
        :return:
        """

        return DICOM_anonymize.save_as(path, PSCID, path)

    @staticmethod
    def save_as(path, PSCID, out_path):
        """
        Anonymize the DICOM to remove any identifiable information
        :param path:
        :param PSCID:
        :param out_path:
        :return:
        """

        success, dataset = DICOM_validate.file(path)
        if not success:
            return False

        success1, _ = DICOM_elements.update(path, "PatientID", PSCID, out_path)
        success2, _ = DICOM_elements.update(path, "PatientName", PSCID, out_path)

        if success1 and success2:
            return True
        else:
            return False
