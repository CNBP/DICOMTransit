from LORIS.candidates import LORIS_candidates
import os
from LORIS.helper import LORIS_helper
from LORIS.query import LORIS_query
from LORIS.timepoint import LORIS_timepoint
from LORIS.trigger_dicom_insert import trigger_dicom_insert
from typing import List
from settings import config_get
"""
Everything here, should have its own login sessions as tokens are not shared at this high level function.  
"""


def check_status() -> bool:
    """
    Quick check if the LORIS is online via a login request.
    :return:
    """
    from LORIS.query import LORIS_query
    status_LORIS, _ = LORIS_query.login()
    return status_LORIS


def check_online_status() -> bool:
    """
    Quck to see if the online connection exist
    :return:
    """

    import socket
    from LORIS.helper import LORIS_helper

    """
    # DNS check vs Google DNS
    host = "http://8.8.8.8"
    port = 53
    timeout = 3
    try:
        socket.setdefaulttimeout(timeout)
        test_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        test_socket.close()
    except:
        return False
    """

    # WWW check vs Google
    import urllib.request
    status_google = urllib.request.urlopen("https://google.com").getcode()
    if not LORIS_helper.is_response_success(status_google, 200):
        return False

    # WWW check vs CNBP.ca
    status_cnbp = urllib.request.urlopen("http://www.cnbp.ca").getcode()
    if not LORIS_helper.is_response_success(status_cnbp, 200):
        return False
    else:
        return True


def trigger_insertion(zip_name: str):
    """
    Todo: refactor this crap made by Yang.
    :param zip_name:
    :return:
    """
    #zip_name = "VTXGL019996_206839_V1"

    # Form the JSON representing the scan.
    JSON_scan = {
        'file' : "/data/incoming/" + zip_name + ".zip",
        'phantom' : "N",
        'candidate': zip_name
    }
    # Concatenate the scan.
    scans = [JSON_scan]

    # Trigger its insertion by calling the API.
    trigger_dicom_insert(scans)


def increment_timepoint(DCCID):
    """
    Increament the existing timepoint for the subject, return the latest timepoint.
    :param DCCID:
    :return:
    """
    from LORIS.query import LORIS_query
    token = LORIS_query.login()

    from LORIS.timepoint import LORIS_timepoint
    success, timepoint = LORIS_timepoint.increaseTimepoint(token, DCCID)
    assert success
    return timepoint


def create_candidate(project, birthday, gender) -> (bool, int, int):
    """
    Check both the creation and deletion of the subject for LORIS.
    :return:
    """

    response_success, token = LORIS_query.login()

    if not response_success:
        raise ConnectionError

    success, DCCID = LORIS_candidates.createCandidate(token, project, birthday, gender)
    assert success

    #responded, success = LORIS_candidates.checkDCCIDExist(token, DCCID)
    #assert responded
    #assert success

    success, PSCID = LORIS_candidates.checkDCCIDExist(token, DCCID)
    assert success

    success, timepoint = LORIS_timepoint.increaseTimepoint(token, DCCID)
    assert success
    return success, DCCID, PSCID


def get_all_timepoints(DCCID:int) -> List[str]:
    """
    Get a list of all possible timepoints associated with a UUID.
    :param DCCID:
    :return:
    """

    # Get token.
    response_success, token = LORIS_query.login()
    if not response_success:
        raise ConnectionError

    # Get Candidate JSON.
    response_success, candidate_json = LORIS_query.getCNBP(token, "candidates/"+str(DCCID))
    if not response_success:
        raise ConnectionError

    # Return a potentially empty visits.
    if "Visits" in candidate_json:
        timepoints = candidate_json["Visits"]
    else:
        timepoints = None

    return timepoints

def get_allUID(DCCID: int) -> List[str]:
    """
    Return the query results from /candidates/$CandID/$Visit/dicoms
    :param DCCID:
    :param timepoint:
    :return:
    """
    # Get token.
    response_success, token = LORIS_query.login()
    if not response_success:
        raise ConnectionError

    # Get Candidate JSON.
    visits = get_all_timepoints(DCCID)

    list_series_UID=[]

    # Loop through all visits.
    if len(visits) > 0:

        # Get dicom series info and then make sure they have series UID and then return them.
        for visit in visits:

            response_success, dicom_info = LORIS_query.getCNBP(token, "candidates/" + str(DCCID)+"/"+visit+"/dicoms")

            if "DicomTars" in dicom_info:
                list_dicom_tars = dicom_info["DicomTars"]
                for dicom_tar in list_dicom_tars:
                    if "SeriesInfo" in dicom_tar:
                        list_seires = dicom_tar["SeriesInfo"]
                        for series in list_seires:
                            list_series_UID.append(series["SeriesUID"])
    return list_series_UID


def upload(local_path):
    """
    Upload file to incoming folder.
    :param local_path:
    :return:
    """

    ProxyIP = config_get("ProxyIP")
    ProxyUsername = config_get("ProxyUsername")
    ProxyPassword = config_get("ProxyPassword")
    LORISHostIP = config_get("LORISHostIP")
    LORISHostUsername = config_get("LORISHostUsername")
    LORISHostPassword = config_get("LORISHostPassword")

    Client = LORIS_helper.getProxySSHClient(ProxyIP, ProxyUsername, ProxyPassword, LORISHostIP, LORISHostUsername,
                                            LORISHostPassword)

    file_name = os.path.basename(local_path)
    LORIS_helper.uploadThroughClient(Client, "//data/incoming/"+file_name, local_path)

"""
def trigger_insertion(file_name):
        import json, requests

        file_data = {"dicoms": [
                                {"file": "//data/incoming/"+file_name,
                                 "phantom": "N",
                                 "candidate": file_name
                                 },
                                ]
                    }

        os.path.splitext(file_name)
        dicoms = {}
        dicoms['file_data'] = "//data/incoming/"+file_name
        dicoms['phantom'] = "N"
        dicoms['candidate'] = file_name
        dicoms['Gender'] = 'Female'
        data = {"dicoms": dicoms}


        data_json = json.dumps(data)


        # temporarily disable warnings:


        with requests.Session() as s:
            # Secure version.
             r = s.post(r"http://dev.cnbp.ca/cnbp/upload_dicoms.php", data=data_json)

            # todo: Non-secure version until we fix the SSL issue
            # r = requests.api.request('post', "https://dev.cnbp.ca/cnbp/upload_dicoms.php", data=data_json)

            print("Post Result:" + str(r.status_code) + r.reason)

if __name__ ==
"""