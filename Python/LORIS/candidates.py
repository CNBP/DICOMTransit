import sys
import os
import json
import logging
from dotenv import load_dotenv
from LORIS.query import getCNBP, postCNBP
from LORIS.helper import is_response_success

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
#logger = logging.getLogger('LORISQuery')


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


def createCandidateCNBP(token, proposded_PSCID):
    """
    Create a candidate using the given PSCID
    :param proposded_PSCID:
    :return: DCCID
    """
    logger = logging.getLogger('LORIS_CreateCNBPCandidates')
    logger.info("Creating CNBP Candidates")
    logger.info(proposded_PSCID)
    PSCID_exist = checkPSCIDExist(token, proposded_PSCID)
    if PSCID_exist:
        return False

    Candidate = {}
    Candidate['Project'] = 'loris'
    Candidate['PSCID'] = proposded_PSCID
    Candidate['DoB'] = '2018-05-04'
    Candidate['Gender'] = 'Female'

    data = {"Candidate":Candidate}

    data_json = json.dumps(data)

    response_code, response = postCNBP(token, "candidates/", data_json)
    if not is_response_success(response_code, 201):
        return False, None
    elif response is not None:  # only try to decode if response is not empty!
        response_json = response.json()
        meta = response_json.get('Meta')
        CandID = meta.get('CandID')
        return True, CandID
    else:
        return False, None


def checkPSCIDExist(token, proposed_PSCID):
    '''
    Check if Site/Study already contain the PSCID
    :param site:
    :param study:
    :return: bool for connection, bool on if such PSCID (INSTITUTIONID + PROJECTID + SUBJECTID) exist already.
    '''
    logger = logging.getLogger('LORIS_checkPSCIDExist')
    logger.info("Checking if PSCID exist: "+proposed_PSCID)
    load_dotenv()
    institution_check = os.getenv("institutionID")


    #Get list of projects
    response_success, loris_project = getCNBP(token, r"projects/loris")
    if not response_success:
        return response_success, None

    #Get list of candidates (Candidates in v0.0.1)
    candidates = loris_project.get("Candidates")
    logger.info(candidates)

    for DCCID in candidates: #these candidates should really be only from the same ID regions.
        response_success, candidate_json = getCNBP(token, r"candidates/"+DCCID)
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

    return False


def checkDCCIDExist(token, proposed_DCCID):
    """
    Check if Site/Study already contain the PSCID
    :param token: 
    :param proposed_DCCID: 
    :return: 
    """
    logger = logging.getLogger('LORIS_checkDCCIDExist')
    logger.info("Checking if DCCID exist: "+str(proposed_DCCID))
    load_dotenv()
    institution_check = os.getenv("institutionID")

    assert (check_DCCID(proposed_DCCID))

    #Get list of projects
    response, loris_project = getCNBP(token, r"projects/loris")
    response_success = is_response_success(response, 200)

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