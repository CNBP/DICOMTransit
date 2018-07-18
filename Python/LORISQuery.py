import sys
import os
import json
import argparse
import getpass
import logging
import requests
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logger = logging.getLogger('LORISQuery')


def is_response_success(status_code):
    if status_code == 200:
        return True
    else:
        return False


def login():
    '''
    Logs into LORIS using the stored credential.
    :return: BOOL if or not it is successful. also, the JSON token that is necessary to conduct further transactions.
    '''
    logger = logging.getLogger('LORIS_login')

    #Load environmental variables.
    load_dotenv()
    username = os.getenv("LORISusername")
    password = os.getenv("LORISpassword")

    #Login URL
    url = os.getenv("LORISurl")
    updatedurl = url+"login"

    r = requests.post(updatedurl, data={'username': username, 'password': password})
    print(r.status_code, r.reason)

    return is_response_success(r.status_code), r.json().get('token')


def getCNBP(endpoint):
    '''
    Get from a CNBP LORIS database endpoint
    :param site:
    :param study:
    :return: bool on if such PSCID (INSTITUTIONID + PROJECTID + SUBJECTID) exist already.
    '''
    load_dotenv()
    url = os.getenv("LORISurl")
    updatedurl = url + endpoint

    response_success, token = login()

    # return early false if failed to login
    if not response_success:
        return response_success, None

    HEADERS = {'Authorization': 'token {}'.format(token)}

    with requests.Session() as s:
        s.headers.update(HEADERS)
        r = s.get(updatedurl)
        print(r.status_code, r.reason)
        print(r.json())

        return is_response_success(r.status_code), r.json()


def postCNBP(endpoint, data):
    '''
    post some data to a LORIS end point.
    :param endpoint:
    :param data:
    :return: bool on if such PSCID (INSTITUTIONID + PROJECTID + SUBJECTID) exist already.
    '''
    load_dotenv()
    url = os.getenv("LORISurl")
    updatedurl = url + endpoint

    response_success, token = login()

    HEADERS = {'Authorization': 'token {}'.format(token)}

    with requests.Session() as s:
        s.headers.update(HEADERS)
        r = s.post(updatedurl, data)
        print(r.status_code, r.reason)
        print(r.json())
        return is_response_success(r.status_code), r.json()

def checkPSCIDExist(proposed_PSCID):
    '''
    Check if Site/Study already contain the PSCID
    :param site:
    :param study:
    :return: bool for connection, bool on if such PSCID (INSTITUTIONID + PROJECTID + SUBJECTID) exist already.
    '''

    load_dotenv()
    institution_check = os.getenv("institutionID")


    #Get list of projects
    response_success, loris_project = getCNBP(r"projects/loris")
    if not response_success:
        return response_success, None

    #Get list of candidates (Candidates in v0.0.1)
    candidates = loris_project.get("Candidates")
    print(candidates)

    for DCCID in candidates: #these candidates should really be only from the same ID regions.
        response_success, candidate_json = getCNBP(r"candidates/"+DCCID)
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

def checkDCCIDExist(proposed_DCCID):
    '''
    Check if Site/Study already contain the PSCID
    :param site:
    :param study:
    :return: bool on if such PSCID (INSTITUTIONID + PROJECTID + SUBJECTID) exist already.
    '''

    load_dotenv()
    institution_check = os.getenv("institutionID")

    #Get list of projects
    response_success, loris_project = getCNBP(r"projects/loris")
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
    load_dotenv()
    response_success, candidate_json = getCNBP(r"candidates/" + DCCID) #should exist as earlier check revealed.
    if not response_success:
        return None
    candidate_visits = candidate_json.get("Visits")
    if len(candidate_visits) > 0:
        return candidate_visits[len(candidate_visits)]
    return None

def createCandidateCNBP(proposded_PSCID):

    PSCID_exist = checkPSCIDExist(proposded_PSCID)
    if PSCID_exist: return False

    data = {}
    data['Project']='loris'
    data['DOB'] = '2018-05-04'
    data['Gender'] = 'Female'

    data_json = json.dumps(data)

    response_success, r = postCNBP("Candidates", data_json)
    if not response_success:
        return False

    print (r.text)

    return True

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
    #login()
    #getCNBP("projects")
    assert(checkPSCIDExist("CNBP0020002"))
    createCandidateCNBP("Test123")
    print("Test complete")