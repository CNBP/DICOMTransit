import sys
import re
import json
import logging
from settings import config_get
from LORIS.query import LORIS_query
from LORIS.helper import LORIS_helper

from LocalDB.schema import CNBP_blueprint

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logger = logging.getLogger(__name__)




class LORIS_candidates:

    @staticmethod
    def parse_PSCID(PSCID: str) -> (bool, str, str):
        """
        Return two parts of the PSCID: institution, subject
        Example: 1 0000033

        :param PSCID:
        :return:
        """

        # fixme: old format VXG0000001 now, 10000022


        # Loading regular expression
        re_institution = CNBP_blueprint.PSCID_schema_institution
        #re_project = CNBP_blueprint.PSCID_schema_project
        re_subject = CNBP_blueprint.PSCID_schema_subject

        if re.search(re_institution, PSCID) is not None and re.search(re_subject, PSCID) is not None:
            # Use expression to extract from the inputted PSCID
            input_institution = re.search(re_institution, PSCID).group(0)
            # input_project = re.search(re_project, PSCID).group(0)
            input_subject = re.search(re_subject, PSCID).group(0)
            success = True
            return success, input_institution, input_subject
        else:
            return False, None, None


    @staticmethod
    def deleteCandidateCNBP(DCCID, PSCID):
        # todo: this should really be done through API. But Currently LORIS does not offer such API.
        # NOTE! If you EVER get NULL coalesce not recognized error, make sure that the PHP version being called from
        # the SSH session is 7+ or else. We had a major issue where the PHP version from SSH session being LOWER
        # than the .bashrc profile imported edition. Also keep in mind that EVEN if .bashrc import this, it MOST LIKELY
        # will not apply to the SSH session!


        ProxyIP = config_get("ProxyIP")
        ProxyUsername = config_get("ProxyUsername")
        ProxyPassword = config_get("ProxyPassword")
        LORISHostPassword = config_get("LORISHostPassword")
        LORISHostUsername = config_get("LORISHostUsername")
        LORISHostIP = config_get("LORISHostIP")
        DeletionScript = config_get("DeletionScript")

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
        Create a candidate with a provided project information. This assumes that the PSCID and DCCIDs are automaticly assigned!
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
        if not LORIS_validation.validate_birth_date_loris(birth_date) or \
           not LORIS_validation.validate_gender(gender): #not LORIS_validation.validate_project(project) or #todo fix this project validation part during creation.
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
            return False, None, None
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
        todo: mostly obsolete as now PSCID is completely generated server side.
        HOWEVER! THere are /candidate_list that can once for all get

        :param token:
        :param proposed_PSCID:
        :return: bool for connection, bool on if such PSCID (INSTITUTIONID + PROJECTID + SUBJECTID) exist already.
        """
        logger = logging.getLogger('LORIS_checkPSCIDExist')
        logger.info("Checking if PSCID exist: "+proposed_PSCID)
        institution_check = config_get("institutionID")

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
        :return: True/False on if DCCID exist, PSCID if it exist.
        """
        from LORIS.validate import LORIS_validation

        logger = logging.getLogger('LORIS_checkDCCIDExist')
        logger.info("Checking if DCCID exist: "+str(proposed_DCCID))

        assert (LORIS_validation.validate_DCCID(proposed_DCCID))

        #todo: This area has projects/loris dependency. Refactor to enable multiple projects handling.
        response, JSON = LORIS_query.getCNBP(token, r"candidates/"+str(proposed_DCCID))
        response_success = LORIS_helper.is_response_success(response, 200)

        if not response_success:
            logger.info("FAILED log response: " + str(response))
            return response_success, None


        if JSON is not None:  # only try to decode if response is not empty!
            meta = JSON.get('Meta')
            PSCID = meta.get('PSCID')
            return True, PSCID
        else:
            return False, None

if __name__ == "__main__":
    #LORIS_candidates.deleteCandidateCNBP(958607, "CNBP8881234")
    print(LORIS_validation.validate_projectID("GL01"))