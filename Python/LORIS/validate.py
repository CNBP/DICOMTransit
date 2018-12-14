import sys
import json
import logging
from PythonUtils.env import load_validate_dotenv
from LocalDB.schema import CNBP_blueprint
from PythonUtils.file import dictionary_search
from LORIS.candidates import LORIS_candidates
from datetime import datetime
import math

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logger = logging.getLogger(__name__)


class LORIS_validation:

    @staticmethod
    def validate_MRN(input_string):
        """
        This validate and check if the MRN is of the proper valid format based on the hospital specification.
        :param input_string:
        :return:
        """
        string=str(input_string)
        if not string.isdigit():
            return False
        try:
            MRN = int(string)
            if 0 < MRN < 9999999:
                return True
            else:
                return False
        except ValueError:
            return False

    @staticmethod
    def validate_project(project):
        """
        Methods to validate the project is indeed a current santioned project in the .ENV file.
        :param project:
        :return:
        """
        #todo need to implement project validation.
        pass

    @staticmethod
    def validate_birth_date_dicom(birth_date):
        """
        Check if the birth_date is normal
        :param birth_date:
        :return:
        """
        # Sanity check for scan date within the past 100 years.
        birth_date = datetime.strptime(birth_date, "%Y%m%d")
        current_date = datetime.now()

        if 0 < math.fabs((current_date-birth_date).days) < 54750:
            return True
        elif math.fabs((current_date-birth_date).days) < 0:
            logger.info("Patient is less than 0 years old. YOU FAILED.")
            return False
        elif math.fabs((current_date-birth_date).days) > 54750:
            logger.info("Patient is more than 150 years old. YOU FAILED.")
            return False
        else:  # Generic catchall false condition
            return False

    @staticmethod
    def validate_birth_date_loris(birth_date):
        """
        Check if the birth_date is normal
        :param birth_date:
        :return:
        """
        # Sanity check for scan date within the past 100 years.
        birth_date = datetime.strptime(birth_date, "%Y-%m-%d")
        current_date = datetime.now()

        if 0 < math.fabs((current_date - birth_date).days) < 54750:
            return True
        elif math.fabs((current_date - birth_date).days) < 0:
            logger.info("Patient is less than 0 years old. YOU FAILED.")
            return False
        elif math.fabs((current_date - birth_date).days) > 54750:
            logger.info("Patient is more than 150 years old. YOU FAILED.")
            return False
        else:  # Generic catchall false condition
            return False


    @staticmethod
    def validate_sex(sex):
        """
        DICOM only permit THREE types: M, F, O capital.
        :param sex:
        :return:
        """
        if sex.lower() == "M".lower() or sex.lower() == "O".lower() or sex.lower() == "F".lower():
            return True
        else:
            return False

    @staticmethod
    def validate_gender(gender):
        if gender == "Male" or gender == "Female":
            return True
        else:
            return False

    @staticmethod
    def validate_instutitionID(input_institutionID: str):
        """
        Check if the institution ID is compliant per the .env specification. String must STRICTLY match.
        :param input_institutionID:
        :return:
        """
        # Parse from the .env standardization
        InsitituionID = load_validate_dotenv("institutionID", CNBP_blueprint.dotenv_variables)

        # Check if institution ID matches
        if not (input_institutionID == InsitituionID):
            return False
        else:
            return True


    @staticmethod
    def validate_projectID(input_projectID: str):
        """
        Provide any string, and it checkss again he dotenv for the proper project KEY which correspond to the ID.
        DICOM/API has the function to actually retrieve the relevant key, after calling this function.
        :param input_projectID:
        :return:
        """

        # Load ProjectIDs from the environment.
        projectID_dictionary_json: str = load_validate_dotenv("projectID_dictionary", CNBP_blueprint.dotenv_variables)
        projectID_list = json.loads(projectID_dictionary_json)

        # check if project ID is in the projectID list via a dictionary search
        key = dictionary_search(projectID_list, input_projectID)

        if key is not None:
            return True
        else:
            return False


    @staticmethod
    def validate_subjectID(input_subjectID: str):
        if not input_subjectID.isdigit():
            return False

        if int(input_subjectID) < 9999999 or int(input_subjectID) > 0:
            return True
        else:
            return False


    @staticmethod
    def validate_CNBPID(CNBPID: str):
        """
        Checks CNBPID inputed for 1) InstitionID format, 2) ProjectID format, 3) SubjectID format.
        :param CNBPID:
        :return:
        """
        logger = logging.getLogger(__name__)

        # Parse from input CNBPID
        success, input_institution, input_subject = LORIS_candidates.parse_PSCID(CNBPID)

        '''Guard Block'''
        # Ensure parsing success
        if not success:
            return False

        # Check institution ID to ensure that
        if not LORIS_validation.validate_instutitionID(input_institution):
            logger.info("InstitutionID portion of the CNBPID is not compliant")
            return False

        # Check last four digits: make sure the last four characters are digits.
        if not LORIS_validation.validate_subjectID(str(input_subject)):
            logger.info("SubjectID portion of the CNBPID is not compliant")
            return False

        return True

    @staticmethod
    def validate_DCCID(DCCID):
        """
        Check if DCCID id conform.
        :param DCCID:
        :return:
        """
        if not len(str(DCCID)) == 6:
            return False
        if not str(DCCID).isnumeric():
            return False
        if DCCID > 999999:
            return False
        if DCCID < 0:
            return False
        return True
