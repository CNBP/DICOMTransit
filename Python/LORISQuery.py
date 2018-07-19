import sys
import os
import json
import argparse
import getpass
import logging
import requests
import pycurl
import certifi
from io import BytesIO
from dotenv import load_dotenv

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logger = logging.getLogger('LORISQuery')


def is_response_success(status_code):
    """
    A simple function to determine the success of the status code
    :param status_code:
    :return: boolean value
    """
    if status_code == 200:
        return True
    elif status_code ==201:
        return True
    else:
        return False


def check_json(data):
    """
    Check if the data input is JSON format compatible.
    :param data:
    :return:
    """
    try:
        JSON = json.loads(data)
        return True, JSON
    except ValueError:
        return False, None
    except:
        return False, None


def login():
    """
    Logs into LORIS using the stored credential. Must use PyCurl as Requests is not working.
    :return: BOOL if or not it is successful. also, the JSON token that is necessary to conduct further transactions.
    """
    logger = logging.getLogger('LORIS_login')

    #Load environmental variables.
    load_dotenv()
    username = os.getenv("LORISusername")
    password = os.getenv("LORISpassword")

    data = json.dumps({"username":username, "password":password})

    #Login URL
    url = os.getenv("LORISurl")
    updated_url = url + 'login'


    # requests style login # NOT WORKING!
    r = requests.post(updated_url, data=data)
    logger.info(r.status_code)
    logger.info(r.reason)

    response_json = r.json()

    return is_response_success(r.status_code), response_json.get('token')


def getCNBP(token, endpoint):
    """
    Get from a CNBP LORIS database endpoint
    :param endpoint:
    :return: bool on if such PSCID (INSTITUTIONID + PROJECTID + SUBJECTID) exist already.
    """
    logger = logging.getLogger('LORIS_get')
    logger.info("Getting LORIS endpoing: "+endpoint)
    load_dotenv()
    url = os.getenv("LORISurl")
    updatedurl = url + endpoint

    HEADERS = {'Authorization': 'token {}'.format(token)}

    with requests.Session() as s:
        s.headers.update(HEADERS)
        r = s.get(updatedurl)
        logger.info(r.status_code)
        logger.info(r.reason)

        return is_response_success(r.status_code), r.json()


def postCNBP(token, endpoint, data):
    """
    post some data to a LORIS end point.
    :param endpoint:
    :param data:
    :return: bool on if such PSCID (INSTITUTIONID + PROJECTID + SUBJECTID) exist already.
    """
    logger = logging.getLogger('LORIS_post')
    logger.info("Posting data to: "+endpoint)
    logger.info("Data: "+data)
    load_dotenv()
    url = os.getenv("LORISurl")
    updatedurl = url + endpoint

    HEADERS = {'Authorization': 'token {}'.format(token)}

    with requests.Session() as s:
        s.headers.update(HEADERS)
        r = s.post(updatedurl, data=data)
        logger.info(r.status_code)
        logger.info(r.reason)
        return is_response_success(r.status_code)


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
    print(candidates)

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

            #latest_timepoint = findlatestTimePoint(DCCID)

    return False


def checkDCCIDExist(token, proposed_DCCID):
    '''
    Check if Site/Study already contain the PSCID
    :param site:
    :param study:
    :return: bool on if such PSCID (INSTITUTIONID + PROJECTID + SUBJECTID) exist already.
    '''
    logger = logging.getLogger('LORIS_checkDCCIDExist')
    logger.info("Checking if DCCID exist: "+proposed_DCCID)
    load_dotenv()
    institution_check = os.getenv("institutionID")

    #Get list of projects
    response_success, loris_project = getCNBP(token, r"projects/loris")
    if not response_success:
        return response_success, None

    #Get list of candidates (Candidates in v0.0.1)
    candidates = loris_project.get("Candidates")
    print(candidates)

    for DCCID in candidates: #todo: these candidates should really be only from the same ID regions.
        if proposed_DCCID != DCCID:
            continue
        else:
            return response_success, True
    return response_success, False


def findlatestTimePoint(DCCID):
    '''
    Find and return the latest timepoint.
    :param DCCID:
    :return:
    '''
    load_dotenv()
    response_success, candidate_json = getCNBP(r"candidates/" + DCCID) #should exist as earlier check revealed.
    if not response_success:
        return response_success, None
    candidate_visits = candidate_json.get("Visits")
    if len(candidate_visits) > 0:
        return candidate_visits[len(candidate_visits)]
    return None


def createCandidateCNBP(proposded_PSCID):
    """
    Create a candidate using the given PSCID
    :param proposded_PSCID:
    :return:
    """
    logger = logging.getLogger('LORIS_CreateCNBPCandidates')
    logger.info("Creating CNBP Candidates")
    logger.info(proposded_PSCID)
    PSCID_exist = checkPSCIDExist(proposded_PSCID)
    if PSCID_exist:
        return False

    Candidate = {}
    Candidate['Project']='loris'
    Candidate['PSCID'] = proposded_PSCID
    Candidate['DOB'] = '2018-05-04'
    Candidate['Gender'] = 'Female'

    data = {"Candidate":Candidate}

    data_json = json.dumps(data)

    response_success, JSON = postCNBP("candidates", data_json)

    return response_success

def incrementTimepoint(DCCID):
    subject_exist = checkDCCIDExist(DCCID)
    if not subject_exist: return None
    latest_timepoint = findlatestTimePoint(DCCID)



'''
//Create a new candidate
$candidate = array(
  'Project' => 'loris',
  'DoB' => '2018-05-06',
  'Gender' => 'Female'
);
$data = array('Candidate' => $candidate);
$result = $loris->createCandidate($token, $data);
if($result && $result->Meta && $result->Meta->CandID){
  $CandID = $result->Meta->CandID;
  $Battery="Experimental";
  //Create Candidate Visit data for this new candidate
  PUT /candidates/$CandID/$VisitLabel
  
  $result = $loris->createCandidateVisit($token, $CandID, $Visit, $Battery);

  //Get Candidate visit data
  //GET /candidates/$CandID/$VisitLabel
  $result = $loris->getCandidateVisit($token, $CandID, $Visit);
  
  
  public function createCandidate($token, $data){
    $endpoint = "candidates/";

    $params = array($token);
    if(($is_valid = $this->isValidParams($params)) !== TRUE){
      return $is_valid;
    }

    if(!isset($data['Candidate'],$data['Candidate']['Project'],$data['Candidate']['Gender'],$data['Candidate']['DoB'])){
      echo $data['Project'], $data['Gender'], $data['DoB'];
      return "Error: Invalid parametres. Verify that Project, Gender , DoB are set";
    }

    return $this->makePostRequest($token, $endpoint, $data);
  }
  
}
'''


# Only executed when running directly.
if __name__ == '__main__':
    #print(login())
    #getCNBP("projects")
    #assert(checkPSCIDExist("CNBP0020002"))
    createCandidateCNBP("Test123")
    #print("Test complete")