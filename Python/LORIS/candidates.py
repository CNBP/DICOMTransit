import sys
import re
import json
import logging
from PythonUtils.env import load_validate_dotenv
from LORIS.query import LORIS_query
from LORIS.helper import LORIS_helper

from LocalDB.schema import CNBP_blueprint

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logger = logging.getLogger(__name__)




class LORIS_candidates:

    @staticmethod
    def parse_PSCID(PSCID: str):
        """
        Return three parts of the PSCID: project, subject
        Example: VTX GL01 9999

        :param PSCID:
        :return:
        """

        # Loading regular expression
        re_institution = CNBP_blueprint.PSCID_schema_institution
        #re_project = CNBP_blueprint.PSCID_schema_project
        re_subject = CNBP_blueprint.PSCID_schema_subject

        # Use expression to extract from the inputted PSCID
        input_institution = re.search(re_institution, PSCID).group(0)
        #input_project = re.search(re_project, PSCID).group(0)
        input_subject = re.search(re_subject, PSCID).group(0)

        if input_subject is None or input_institution is None:
            success = False
        else:
            success = True

        return success, input_institution, input_subject



    @staticmethod
    def deleteCandidateCNBP(DCCID, PSCID):
        # todo: this should really be done through API. But Currently LORIS does not offer such API.
        # NOTE! If you EVER get NULL coalesce not recognized error, make sure that the PHP version being called from
        # the SSH session is 7+ or else. We had a major issue where the PHP version from SSH session being LOWER
        # than the .bashrc profile imported edition. Also keep in mind that EVEN if .bashrc import this, it MOST LIKELY
        # will not apply to the SSH session!


        ProxyIP = load_validate_dotenv("ProxyIP", CNBP_blueprint.dotenv_variables)
        ProxyUsername = load_validate_dotenv("ProxyUsername", CNBP_blueprint.dotenv_variables)
        ProxyPassword = load_validate_dotenv("ProxyPassword", CNBP_blueprint.dotenv_variables)
        LORISHostPassword = load_validate_dotenv("LORISHostPassword", CNBP_blueprint.dotenv_variables)
        LORISHostUsername = load_validate_dotenv("LORISHostUsername", CNBP_blueprint.dotenv_variables)
        LORISHostIP = load_validate_dotenv("LORISHostIP", CNBP_blueprint.dotenv_variables)
        DeletionScript = load_validate_dotenv("DeletionScript", CNBP_blueprint.dotenv_variables)

        # NOTE! If you EVER get NULL coalesce not recognized error, make sure that the PHP version being called from
        # the SSH session is 7+ or else. We had a major issue where the PHP version from SSH session being LOWER
        # than the bashrc profile imported edition. Also keep in mind that EVEN if .bashrc import this, it MOST LIKELY
        # will not apply to the SSH session!

        command_string = "/opt/rh//rh-php70/root/usr/bin/php " + DeletionScript + " delete_candidate " + str(DCCID) + " " + PSCID + " confirm"



        logger.info(command_string)

        # Establish connection to client.
        Client = LORIS_helper.getProxySSHClient(ProxyIP, ProxyUsername, ProxyPassword, LORISHostIP, LORISHostUsername,
                                                LORISHostPassword)

        # Execute the command
        LORIS_helper.triggerCommand(Client, command_string)

        # Close the client.
        Client.close()


    @staticmethod
    def createCandidate(token, project, birth_date, gender):
        """
        Create a candidate using the given PSCID
        :param token
        :param birth_date: Birth date MUST Be in YYYY-MM-DD format!
        :param gender: Gender must be Male or Female!
        :param project:
        :return: DCCID
        """
        logger = logging.getLogger('LORIS_CreateCNBPCandidates')
        logger.info("Creating CNBP Candidates belong to project: " + project)

        Candidate = {}
        from LORIS.validate import LORIS_validation
        if not LORIS_validation.validate_project(project) or not LORIS_validation.validate_birth_date(birth_date) or not LORIS_validation.validate_gender(gender):
            logger.info("Non-compliant PSCID component detected. Aborting PSCID creation ")
            return False, None

        Candidate['Project'] = project
        #Candidate['PSCID'] = proposed_PSCID Now auto sequence.
        Candidate['DoB'] = birth_date
        Candidate['Gender'] = gender

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
        institution_check = load_validate_dotenv("institutionID", CNBP_blueprint.dotenv_variables)

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
        from LORIS.validate import LORIS_validation

        logger = logging.getLogger('LORIS_checkDCCIDExist')
        logger.info("Checking if DCCID exist: "+str(proposed_DCCID))

        assert (LORIS_validation.validate_DCCID(proposed_DCCID))

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
    #LORIS_candidates.deleteCandidateCNBP(958607, "CNBP8881234")
    print(LORIS_validation.validate_projectID("GL01"))