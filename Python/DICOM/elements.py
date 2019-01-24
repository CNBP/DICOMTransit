import logging
from DICOM.validate import DICOM_validate
from PythonUtils.file import current_funct_name
from LORIS.validate import LORIS_validation

class DICOM_elements:

    @staticmethod
    def retrieve(file_path, data_element):
        """
        A low level function used to retrieve elements from DICOM and return a LIST of matching element. ACCEPT PARTIAL MATCH
        :param file_path:
        :param data_element:
        :return: LIST of all data elements that match the pattern provided in the data_element and their value.  NO Regular EXPRESSION.
        """
        logger = logging.getLogger(current_funct_name())
        success, DICOM = DICOM_validate.file(file_path)

        if not success:
            return False, None

        try:
            # Get a list of all data elements that can have element label.
            element_values = DICOM.data_element(data_element).value
            return True, element_values
        except KeyError:
            #todo: dicomdir situation most likely ends here.
            logger.error("Key Not exist")
            return False, "Key Not exist"
        except Exception:
            logger.error("General catch all exception reached. Contact author with the file to debug")
            return False, "General catch all exception reached. Contact author with the file to debug"

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
        logger = logging.getLogger(current_funct_name())

        success, DICOM = DICOM_validate.file(file_path)
        if not success:
            return False, "DICOM not valid."

        try:
            DICOM.data_element(data_element).value = element_value
        except KeyError:
            logger.error(f"Key {data_element } does not exist, creating the key.")
            return False, "DICOM key field does not exist. Not sure how to database one yet. "
        DICOM.save_as(out_path)
        return True, "Data element update completed."


    @staticmethod
    def retrieve_MRN(file_path):
        """
        Read the PatientID field which normally used as MRN number.
        :param file_path:
        :return: MRN number, as a STRING
        """
        logger = logging.getLogger(current_funct_name())
        success, MRN = DICOM_elements.retrieve(file_path, "PatientID")

        if not success:
            logger.error("Was not able to access/read the file!")
            return False, None
        elif LORIS_validation.validate_MRN(MRN):
            return True, MRN
        else:
            logger.error("Was not able to validate the MRN number. Invalid format perhaps? Expected SEVEN digis, got "+MRN)
            return False, None


    @staticmethod
    def retrieve_patient_id(file_path):
        """
        Read the PatientName field. No checking. Used for validation post anonymization.
        :param file_path:
        :return: MRN number, as a STRING
        """
        logger = logging.getLogger(current_funct_name())
        success, name = DICOM_elements.retrieve(file_path, "PatientID")

        if not success:
            logger.error("Was not able to access/read the file!")
            return False, None

        else:
            return True, name

    @staticmethod
    def retrieve_name(file_path):
        """
        Read the PatientName field. No checking. Used for validation post anonymization.
        :param file_path:
        :return: MRN number, as a STRING
        """
        logger = logging.getLogger(current_funct_name())
        success, name = DICOM_elements.retrieve(file_path, "PatientName")

        if not success:
            logger.error("Was not able to access/read the file!")
            return False, None

        else:
            return True, name

    @staticmethod
    def retrieve_seriesUID(file_path):
        """
        Read the PatientName field. No checking. Used for validation post anonymization.
        :param file_path:
        :return: MRN number, as a STRING
        """
        logger = logging.getLogger(current_funct_name())
        success, SeriesUID = DICOM_elements.retrieve(file_path, "SeriesInstanceUID")

        if not success:
            logger.error("Was not able to access/read the file!")
            return False, None

        else:
            return True, SeriesUID

    @staticmethod
    def retrieve_scan_date(file_path):
        """
        Lower level function to Read the StudyDescription field which normally used to identify the specific PROJECT.
        :param file_path:
        :return: MRN number, as a STRING
        """
        # todo see if there are ways to validate this part vs study before returning. s

        # todo: to be debugged. Check detailed conditions.
        from datetime import datetime
        logger = logging.getLogger(current_funct_name())

        # Retrieve the data element.
        success, SeriesDate = DICOM_elements.retrieve(file_path, "SeriesDate")

        if not success:
            logger.error("File failed.")
            return False, None
        elif SeriesDate is None:  # null check.
            logger.error("Date not specified, it is EMPTY! Handle with care with project inference")
            return False, None
        elif SeriesDate == "":
            logger.error("Retrieval of study value failed. Invalid value.")
            return False, SeriesDate
        else:
            # Convert it to date.
            return True, datetime.strptime(SeriesDate, "%Y%m%d")


    @staticmethod
    def retrieve_study(file_path):
        """
        Lower level function to Read the StudyDescription field which normally used to identify the specific PROJECT.
        :param file_path:
        :return: MRN number, as a STRING
        """
        logger = logging.getLogger(current_funct_name())
        success, value = DICOM_elements.retrieve(file_path, "StudyDescription")

        if value=="":
            logger.error("Optional study not specified, it is EMPTY! Handle with care with project inference")
            return True, value
        elif not success or value is None:
            logger.error("Retrieval of study value failed. Invalid value.")
            return False, None
        else: #todo see if there are ways to validate this part vs study
            return True, value


    @staticmethod
    def retrieve_birthday(file_path):
        """
        Lower level function to Read the birthdate PatientID field required for CNBPID LORIS generation.
        :param file_path:
        :return: MRN number, as a STRING
        """
        logger = logging.getLogger(current_funct_name())
        success, value = DICOM_elements.retrieve(file_path, "PatientBirthDate")

        if not success or value == "" or value is None:
            logger.error("Retrieval of birthday value failed. Empty/invalid value.")
            return False, None
        elif LORIS_validation.validate_birth_date_dicom(value):

            # Import stirng to datetime, convert to compliant date time
            import datetime
            birthdate = datetime.datetime.strptime(value,'%Y%m%d')
            birthdate_loris_format = birthdate.strftime('%Y-%m-%d')

            return True, birthdate_loris_format
        else:
            logger.error("Birthdate failed validation. Bad date.")
            return False, None



    @staticmethod
    def retrieve_sex(file_path):
        """
        Lower level function to Read the Sex field.
        :param file_path:
        :return: MRN number, as a STRING
        """
        logger = logging.getLogger(current_funct_name())

        success, value = DICOM_elements.retrieve(file_path, "PatientSex")

        if not success or value == "" or value is None:
            logger.error("Retrieval of sex value failed. Empty/invalid value.")
            return False, None
        elif LORIS_validation.validate_sex(value):
            return True, value
        else:
            logger.error("Unexpected value. Should be M, F, O")
            return False, None



    @staticmethod
    def compute_age(file_path):
        """
        Read the PatientID field which normally used as MRN number.
        :param file_path:
        :return: Age as a relative delta time object.
        """
        # todo: refactor using existing functions.

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
    #for file in file_names:
    #    retri