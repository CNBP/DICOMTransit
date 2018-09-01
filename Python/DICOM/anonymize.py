from DICOM.validate import DICOM_validate
from DICOM.elements import DICOM_elements
import logging
from tqdm import tqdm
from PythonUtils.folder import recursive_list

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

    @staticmethod
    def filelist(file_list, new_ID):
        """
        :param file_list:
        :return:
        """
        logger = logging.getLogger("Anonymizing files")

        exception_count = 0
        exception_files = []

        for file in tqdm(file_list):
            logger.info("Decompressing: " + file)
            is_DICOM_file, _ = DICOM_validate.file(file)
            if not is_DICOM_file:
                continue

            if False == DICOM_anonymize.save(file, new_ID):
                exception_count =+ 1
                exception_files = exception_files.append(file)

        logger.info("Total exception encountered uring anonymization: " + str(exception_count))
        return exception_files


    @staticmethod
    def folder(input_folder, new_ID):
        files_list = recursive_list(input_folder)
        DICOM_anonymize.filelist(files_list, new_ID)