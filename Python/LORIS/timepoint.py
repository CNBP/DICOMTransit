import json
import logging
import sys

from LORIS.candidates import LORIS_candidates
from LORIS.validate import LORIS_validation
from LORIS.helper import LORIS_helper
from LORIS.query import LORIS_query
from LocalDB.schema import CNBP_blueprint
from settings import get
from PythonUtils.intmath import int_incrementor

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logger = logging.getLogger(__name__)

class LORIS_timepoint:

    @staticmethod
    def check_timepoint_compliance(input_string: str) -> bool:
        """
        Validate if the given string is compliant with the timepoint format specified in the .env
        :param input_string:
        :return:
        """

        # Get config defined prefix.
        timepoint_prefix = get("timepoint_prefix")

        # Check it against first letter.
        if timepoint_prefix != input_string[0]:
            return False

        timepoint_number = input_string[1:]

        # number should not have alphabet.
        if timepoint_number.isalpha():
            return False

        if timepoint_number.isnumeric() and timepoint_number.isdigit(): # be wary of edge case like ³
            return True
        return False


    @staticmethod
    def visit_number_extraction(string: str):
        """
        A wrapper for number_extraction by calling it on a string and then return the latest one.
        Used to deal with visitnumber list.
        :param string:
        :return:
        """
        number_extracted = LORIS_helper.number_extraction(string)

        #return last number from the timepoint string: usually it should be V2 or T3 things like that.
        if len(number_extracted) > 1:
            return number_extracted[len(number_extracted)-1]
        else:
            return number_extracted[0]

    @staticmethod
    def findLatestTimePoint(token: str, DCCID: int) -> str:
        """
        Find and return the latest timepoint. Note that since DCCID exist, the record MUST ALREADY exist within the local SQLite database!
        :param token: the token used to authenticate API actions.
        :param DCCID: DCCID to retrieve the last timepoint of
        :return: a string representation of the last time point.
        """
        assert(LORIS_validation.validate_DCCID(DCCID)) # Ensure it actually first exist.

        response_success, candidate_json = LORIS_query.getCNBP(token, r"candidates/" + str(DCCID)) # should exist as earlier check revealed.

        # preliminary exit condition
        if not response_success:
            return None

        candidate_visits_list = candidate_json.get("Visits")

        if len(candidate_visits_list) > 0:
            return candidate_visits_list[len(candidate_visits_list)-1] # return the LAST TIME POINT!
        return None

    @staticmethod
    def increaseTimepoint(token: str, DCCID: int) -> (bool, str):
        """
        Increment the existing timepoint by check if DCCID existed, then get the latest one, then increment its number by creating a new timepoint.
        :param token: auth token
        :param DCCID: the DCCID of the existing subject.
        :return: if creation request is successful, and what label is actually created.
        """
        #todo: must handle the special edge case where timepoint reach V10 etc where two or three more digits are there!

        timepoint_label = ""

        # ensure valid input and subject actually exist.
        assert (LORIS_validation.validate_DCCID(DCCID))
        subject_exist, _ = LORIS_candidates.checkDCCIDExist(token, DCCID)
        if not subject_exist:
            return False, None

        latest_timepoint = LORIS_timepoint.findLatestTimePoint(token, DCCID)

        if latest_timepoint is None:
            success = LORIS_timepoint.createTimepoint(token, DCCID, "V1")
            timepoint_label = "V1"
        else:
            visit_number = LORIS_timepoint.visit_number_extraction(latest_timepoint)
            new_visit_number = int_incrementor(visit_number)


            prefix = get("timepoint_prefix")

            timepoint_label = prefix + str(new_visit_number)

            success = LORIS_timepoint.createTimepoint(token, DCCID, timepoint_label)

        return success, timepoint_label

    @staticmethod
    def createTimepoint(token, DCCID, time_point) -> bool:
        """
        Create a timepoint of the given DCCID subject based on the timepoint provided.
        :param token:
        :param DCCID:
        :param time_point:
        :return:
        """
        endpoint = r"/candidates/"+str(DCCID)+r"/"+time_point
        MetaData = {"CandID": DCCID, "Visit": time_point, "Battery":"CNBP"} # default to CNBP for NOW
        Meta = {"Meta": MetaData}
        JSON = json.dumps(Meta)
        status_code, _ = LORIS_query.putCNBP(token, endpoint, JSON)
        success = LORIS_helper.is_response_success(status_code, 201) # 201 signify successufl subject timepoint creation!

        # response should be null!
        return success


# Only executed when running directly.
if __name__ == '__main__':
    # print(login())
    # getCNBP("projects")
    # assert(checkPSCIDExist("CNBP0020002"))
    Success, token = LORIS_query.login()
    # createTimePoint(token, 559776, "V9")
    success, latest_timepoint = LORIS_timepoint.increaseTimepoint(token, 635425)
    print (success)
    print (latest_timepoint)
    # print("Test complete")