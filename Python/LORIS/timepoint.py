import sys
import os
import json
import logging
from dotenv import load_dotenv
from LORIS.helper import number_extraction
from LORIS.query import getCNBP, putCNBP, login
from LORIS.candidates import check_DCCID, checkDCCIDExist

logging.basicConfig(stream=sys.stdout, level=logging.INFO)


def visit_number_extraction(string):
    """
    A wrapper for number_extraction by calling it on a string and then return the latest one.
    Used to deal with visitnumber list.
    :param string:
    :return:
    """
    logger = logging.getLogger('visit_number_extraction')

    number_extracted = number_extraction(string)

    #return last number from the timepoint string: usually it should be V2 or T3 things like that.
    if len(number_extracted) > 1:
        return number_extracted[len(number_extracted)-1]
    else:
        return number_extracted[0]


def findLatestTimePoint(token, DCCID):
    '''
    Find and return the latest timepoint. Note that since DCCID exist, the record MUST ALREADY exist within the local SQLite database!
    :param DCCID:
    :return:
    '''
    logger = logging.getLogger('')
    assert(check_DCCID(DCCID)) # Ensure it actually first exist.

    response_success, candidate_json = getCNBP(token, r"candidates/" + str(DCCID)) # should exist as earlier check revealed.

    # preliminary exit condition
    if not response_success:
        return response_success, None

    candidate_visits_list = candidate_json.get("Visits")

    if len(candidate_visits_list) > 0:
        return candidate_visits_list[len(candidate_visits_list)-1] # return the LAST TIME POINT!
    return None

def increaseTimepoint(token, DCCID):
    """
    Increment the existing timepoint by check if DCCID existed, then get the latest one, then increment its number by creating a new timepoint.
    :param token: auth token
    :param DCCID: the DCCID of the existing subject.
    :return: if creation request is successful, and what label is actually created.
    """
    #todo: must handle the special edge case where timepoint reach V10 etc where two or three more digits are there!

    # ensure valid input and subject actually exist.
    assert (check_DCCID(DCCID))
    success, subject_exist = checkDCCIDExist(token, DCCID)
    if not subject_exist or not success:
        return False, None

    latest_timepoint = findLatestTimePoint(token, DCCID)

    if latest_timepoint is None:
        success = createTimepoint(token, DCCID, "V1")
    else:
        visit_number = visit_number_extraction(latest_timepoint)
        new_visit_number = int(visit_number) + 1

        load_dotenv()
        prefix = os.getenv("timepoint_prefix")

        timepoint_label = prefix + str(new_visit_number)

        success = createTimepoint(token, DCCID, timepoint_label)

    return success, timepoint_label


def createTimepoint(token, DCCID, time_point):
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
    success, response = putCNBP(token, endpoint, JSON)
    # response should be null!
    return success


# Only executed when running directly.
if __name__ == '__main__':
    # print(login())
    # getCNBP("projects")
    # assert(checkPSCIDExist("CNBP0020002"))
    Success, token = login()
    # createTimePoint(token, 559776, "V9")
    success, latest_timepoint = increaseTimepoint(token, 635425)
    print (success)
    print (latest_timepoint)
    # print("Test complete")