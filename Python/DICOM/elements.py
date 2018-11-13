import logging
from DICOM.validate import DICOM_validate
from PythonUtils.file import current_funct_name
from datetime import datetime
import math

logging.basicConfig(stream=sys.stdout, level=logging.INFO)


class DICOM_elements:

    @staticmethod
    def retrieve(file_path, data_element):
        """
        A low level function used to retrieve elements from DICOM and return a LIST of matching element. ACCEPT PARTIAL MATCH
        :param file_path:
        :param data_element:
        :return: LIST of all data elements that match the pattern provided in the data_element and their value.  NO Regular EXPRESSION.
        """
        success, DICOM = DICOM_validate.file(file_path)

        if not success:
            return False, None

        # Get a list of all data elements that can have element label.
        element_values = DICOM.data_element(data_element).value

        return True, element_values

    @staticmethod
    def update(file_path, data_element, element_value, out_path):
        """
        Update a particular data_element to the desired value, then write back to the SOURCE FILE!
        :param file_path:
        :param data_element:
        :param element_value:
        :param  out_path
        :return: bool on operation success, and string on reason.
        """

        """BE AWARE that if the key does not exist, it will not be created currently!"""
        logger = logging.getLogger(__name__)

        success, DICOM = DICOM_validate.file(file_path)
        if not success:
            return False, "DICOM not valid."

        try:
            DICOM.data_element(data_element).value = element_value
        except KeyError:
            logger.info("Key " + data_element + " does not exist, creating the key.")
            return False, "DICOM key field does not exist. Not sure how to database one yet. "
        DICOM.save_as(out_path)
        return True, "Data element update completed."

    @staticmethod
    def retrieveMRN(file_path):
        """
        Read the PatientID field which normally used as MRN number.
        :param file_path:
        :return: MRN number, as a STRING
        """
        success, value = DICOM_elements.retrieve(file_path, "PatientID")

        if not success:
            return False, None
        else:
            return True, value

    @staticmethod
    def retrieveStudy(file_path):
        """
        Read the StudyDescription field which normally used to identify the specific PROJECT.
        :param file_path:
        :return: MRN number, as a STRING
        """
        logger = logging.getLogger(current_funct_name)
        success, value = DICOM_elements.retrieve(file_path, "StudyDescription")

        if value=="":
            logger.info("Optional study not specified, it is EMPTY! Handle with care with project inference")
            return True, value
        elif not success or value is None:
            logger.info("Retrieval of study value failed. Invalid value.")
            return False, None
        else:
            return True, value

    @staticmethod
    def retrieveBirthday(file_path):
        """
        Read the birthdate PatientID field required for CNBPID LORIS generation.
        :param file_path:
        :return: MRN number, as a STRING
        """
        logger = logging.getLogger(current_funct_name)
        success, value = DICOM_elements.retrieve(file_path, "PatientBirthDate")

        if not success or value == "" or value is None:
            logger.info("Retrieval of birthday value failed. Empty/invalid value.")
            return False, None
        else:
            # Sanity check for scan date within the past 100 years.
            birth_date = datetime.strptime(value, "%Y%m%d")
            current_date = datetime.now()

            if math.fabs((current_date-birth_date).days) < 36500:
                return True, value
            else:
                logger.info("Patient birthday is more than 100 years in the past? YOU FAILED.")
                return False, None

    @staticmethod
    def retrieveSex(file_path):
        """
        Read the Sex field which normally used as MRN number.
        :param file_path:
        :return: MRN number, as a STRING
        """
        logger = logging.getLogger(current_funct_name)

        success, value = DICOM_elements.retrieve(file_path, "PatientSex")

        if not success or value == "" or value is None:
            logger.info("Retrieval of sex value failed. Empty/invalid value.")
            return False, None
        elif value == "M" or value == "O" or value == "F":
            return True, value
        else:
            logger.info("Retrieval of sex value failed. Unexpected value. Should be M, F, O")
            return False, None



    @staticmethod
    def computeScanAge(file_path):
        """
        Read the PatientID field which normally used as MRN number.
        :param file_path:
        :return: Age as a relative delta time object.
        """

        from dateutil.relativedelta import relativedelta

        success, DICOM = DICOM_validate.file(file_path)
        if not success:
            return False, None
        from datetime import datetime
        scan_date = datetime.strptime(DICOM.SeriesDate, "%Y%m%d")
        birthday = datetime.strptime(DICOM.PatientBirthDate, "%Y%m%d")
        age = relativedelta(scan_date,birthday)
        # age = scan_date - birthday
        return True, age

if __name__ == "__main__":
    from pydicom.data import get_testdata_files
    file_names = get_testdata_files("[Jj][Pp][Ee][Gg]")
    for file in file_names:
        retri