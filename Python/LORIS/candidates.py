from subprocess import check_call
import sys
import os
import re
import json
import logging
from dotenv import load_dotenv
from LORIS.query import LORIS_query
from LORIS.helper import LORIS_helper
from LocalDB.schema import CNBP_blueprint
logging.basicConfig(stream=sys.stdout, level=logging.INFO)
#logger = logging.getLogger('LORISQuery')

class LORIS_candidates:

    @staticmethod
    def parse_PSCID(PSCID):
        """
        Return three parts of the PSCID: institution, project, subject
        :param PSCID:
        :return:
        """
        success = load_dotenv()
        if not success:
            raise ImportError("Credential .env NOT FOUND! Please ensure .env is set with all the necessary credentials!")

        # Loading regular expression
        re_institution = CNBP_blueprint.PSCID_schema_institution
        re_project = CNBP_blueprint.PSCID_schema_project
        re_subject = CNBP_blueprint.PSCID_schema_subject

        # Use expression to extract from the inputted PSCID
        input_institution = re.search(re_institution, PSCID).group(0)
        input_project = re.search(re_project, PSCID).group(0)
        input_subject = re.search(re_subject, PSCID).group(0)

        if input_subject is None or input_project is None or input_institution is None:
            success = False
        else:
            success = True

        return success, input_institution, input_project, input_subject

    @staticmethod
    def check_instutitionID_compliance(input_institutionID):
        # Parse from the .env standardization
        InsitituionID = os.getenv("institutionID")

        # Check if institution ID matches
        if not (input_institutionID == InsitituionID):
            return False
        else:
            return True

    @staticmethod
    def check_projectID_compliance(input_projectID):

        # Load ProjectIDs from the environment.
        success = load_dotenv()
        if not success:
            raise ImportError("Credential .env NOT FOUND! Please ensure .env is set with all the necessary credentials!")

        projectID_dictionary_json: str = os.getenv("projectID_dictionary")
        projectID_list = json.loads(projectID_dictionary_json)

        # check if project ID is in the projectID list.
        isRecognized = input_projectID in projectID_list

        return isRecognized

    @staticmethod
    def check_subjectID_compliance(input_subjectID):
        if not input_subjectID.isdigit():
            return False

        if int(input_subjectID) < 9999 or int(input_subjectID) > 0:
            return True
        else:
            return False

    @staticmethod
    def check_PSCID_compliance(PSCID):
        """
        Checks PSCID inputed for 1) InstitionID format, 2) ProjectID format, 3) SubjectID format.
        :param PSCID:
        :return:
        """
        logger = logging.getLogger(__name__)

        # Parse from input PSCID
        success, input_institution, input_project, input_subject = LORIS_candidates.parse_PSCID(PSCID)

        # Ensure parsing success
        if not success:
            return False

        # Check institution ID to ensure that
        if not LORIS_candidates.check_instutitionID_compliance(input_institution):
            logger.info("Institution not compliant")
            return False

        # Check if projectID already exist
        if not LORIS_candidates.check_projectID_compliance(input_project):
            logger.info("ProjectID not recognized")
            return False

        # Check last four digits: make sure the last four characters are digits.
        if not LORIS_candidates.check_subjectID_compliance(str(input_subject)):
            logger.info("SubjectID not standardized")
            return False

        return True

    @staticmethod
    def check_DCCID(DCCID):
        """
        Check if DCCID id conform.
        :param DCCID:
        :return:
        """
        if not len(str(DCCID)) == 6:
            return False
        elif not str(DCCID).isnumeric():
            return False
        elif DCCID > 999999:
            return False
        elif DCCID < 0:
            return False
        else:
            return True

    @staticmethod
    def deleteCandidateCNBP(token, DCCID, PSCID):
        logger = logging.getLogger('UT_LORIS_delete_subject')

        # Load the hard coded variables.
        success = load_dotenv()
        if not success:
            raise ImportError("Credential .env NOT FOUND! Please ensure .env is set with all the necessary credentials!")
        ProxyIP = os.getenv("ProxyIP")
        ProxyUsername = os.getenv("ProxyUsername")
        ProxyPassword = os.getenv("ProxyPassword")
        LORISHostPassword = os.getenv("LORISHostPassword")
        LORISHostUsername = os.getenv("LORISHostUsername")
        LORISHostIP = os.getenv("LORISHostIP")
        DeletionScript = os.getenv("DeletionScript")

        # Export some variables for subsequent deletion clean script against production database (yes... because we could not automate LORIS development...):
        command_string = ["sshpass", "-p", ProxyPassword, "ssh", ProxyUsername + "@" + ProxyIP, "-t", "sshpass", "-p",
                          LORISHostPassword, "ssh", "-L", "3001:localhost:22",
                          LORISHostUsername + "@" + LORISHostIP, "php", DeletionScript, "delete_candidate", str(DCCID),
                          PSCID, "confirm"]

        logger.info(command_string)
        if 'TRAVIS' in os.environ:
            logger.info("Running LORIS delete candidate that was created for: " + PSCID)
            check_call(command_string)

    @staticmethod
    def createCandidateCNBP(token, proposed_PSCID):
        """
        Create a candidate using the given PSCID
        :param token
        :param proposed_PSCID:
        :return: DCCID
        """
        logger = logging.getLogger('LORIS_CreateCNBPCandidates')
        logger.info("Creating CNBP Candidates: " + proposed_PSCID)

        PSCID_exist = LORIS_candidates.checkPSCIDExist(token, proposed_PSCID)
        if PSCID_exist:
            logger.info("PSCID already exist. Quitting.")
            return False

        Candidate = {}
        Candidate['Project'] = 'loris'
        Candidate['PSCID'] = proposed_PSCID
        Candidate['DoB'] = '2018-05-04'
        Candidate['Gender'] = 'Female'

        data = {"Candidate":Candidate}

        data_json = json.dumps(data)

        response_code, response = LORIS_query.postCNBP(token, "candidates/", data_json)
        if not LORIS_helper.is_response_success(response_code, 201):
            return False, None
        elif response is not None:  # only try to decode if response is not empty!
            response_json = response.json()
            meta = response_json.get('Meta')
            CandID = meta.get('CandID')
            return True, CandID
        else:
            return False, None

    @staticmethod
    def checkPSCIDExist(token, proposed_PSCID):
        """
        Check if Site/Study already contain the PSCID
        :param token:
        :param proposed_PSCID:
        :return: bool for connection, bool on if such PSCID (INSTITUTIONID + PROJECTID + SUBJECTID) exist already.
        """
        logger = logging.getLogger('LORIS_checkPSCIDExist')
        logger.info("Checking if PSCID exist: "+proposed_PSCID)
        success = load_dotenv()
        if not success:
            raise ImportError("Credential .env NOT FOUND! Please ensure .env is set with all the necessary credentials!")
        institution_check = os.getenv("institutionID")


        #Get list of projects
        response_success, loris_project = LORIS_query.getCNBP(token, r"projects/loris")
        if not response_success:
            return response_success, None

        #Get list of candidates (Candidates in v0.0.1)
        candidates = loris_project.get("Candidates")
        logger.info(candidates)

        for DCCID in candidates: #these candidates should really be only from the same ID regions.
            response_success, candidate_json = LORIS_query.getCNBP(token, r"candidates/"+DCCID)
            if not response_success:
                return response_success, False
            # Each site following the naming convention should have SITE prefix and PI prefix and PROJECT prefix to avoid collision

            # A site check here.
            candidate_meta = candidate_json.get("Meta")
            candidate_pscID = candidate_meta.get("PSCID")

            # Not gonna check is institution ID doesn't even match.
            if candidate_pscID[0:3] != institution_check:
                continue

            elif candidate_pscID == proposed_PSCID:
                return response_success, True

                #latest_timepoint = findLatestTimePoint(DCCID)

        return True, False

    @staticmethod
    def checkDCCIDExist(token, proposed_DCCID):
        """
        Check if Site/Study already contain the PSCID
        :param token:
        :param proposed_DCCID:
        :return:
        """
        logger = logging.getLogger('LORIS_checkDCCIDExist')
        logger.info("Checking if DCCID exist: "+str(proposed_DCCID))
        success = load_dotenv()
        if not success:
            raise ImportError("Credential .env NOT FOUND! Please ensure .env is set with all the necessary credentials!")
        institution_check = os.getenv("institutionID")

        assert (LORIS_candidates.check_DCCID(proposed_DCCID))

        #Get list of projects
        response, loris_project = LORIS_query.getCNBP(token, r"projects/loris")
        response_success = LORIS_helper.is_response_success(response, 200)

        if not response_success:
            logger.info("FAILED log response: " + str(response))
            return response_success, None

        #Get list of candidates (Candidates in v0.0.1)
        candidates = loris_project.get("Candidates")
        logger.info(candidates)

        for DCCID in candidates:
            if str(proposed_DCCID) == DCCID:
                return response_success, True
            else:
                continue
        return response_success, False

if __name__ == "__main__":
    print(LORIS_candidates.check_projectID_compliance("GL01"))