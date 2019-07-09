from LORIS.candidates import LORIS_candidates
import os
from LORIS.helper import LORIS_helper
from LORIS.query import LORIS_query
from LORIS.timepoint import LORIS_timepoint
from LORIS.trigger_dicom_insert import trigger_dicom_insert
from typing import List
from settings import config_get
import logging
from urllib.parse import urljoin

logger = logging.getLogger()

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
    if not LORIS_helper.is_response(status_google, 200):
        return False

    # WWW check vs CNBP.ca
    status_cnbp = urllib.request.urlopen("http://www.cnbp.ca").getcode()
    if not LORIS_helper.is_response(status_cnbp, 200):
        return False
    else:
        return True


def old_trigger_insertion(zip_name: str):
    """
    Todo: refactor this crap made by Yang.
    :param zip_name:
    :return:
    """
    # zip_name = "VTXGL019996_206839_V1"

    # Form the JSON representing the scan.
    JSON_scan = {
        "file": f"/data/incoming/{zip_name}.zip",
        "phantom": "N",
        "candidate": zip_name,
    }
    # Concatenate the scan.
    scans = [JSON_scan]

    # Trigger its insertion by calling the API.
    trigger_dicom_insert(scans)


def new_trigger_insertion(
    DCCID: int, VisitLabel: str, filename: str, mri_upload_id: int
) -> int:
    """
    Trigger the insertion of the subject files and then return the process_id which can be checked later on.
    :param DCCID:
    :param VisitLabel:
    :param filename:
    :param mri_upload_id:
    :return:
    """
    # POST / candidates /$CandID /$VisitLabel / dicoms /$Filename /
    endpoint = f"candidates/{DCCID}/{VisitLabel}/dicoms/{filename}"

    # Get token.
    response_success, token = LORIS_query.login()
    if not response_success:
        raise ConnectionError

    import json

    request_dictionary = {
        "process_type": "mri_upload",
        "Filename": filename,
        "mri_upload_id": mri_upload_id,
    }

    # the request in json format ready for payload.
    request_json = json.dumps(request_dictionary)

    # Post the requests.
    status_code, response = LORIS_query.postCNBP(token, endpoint, request_json)

    process_id = None

    if LORIS_helper.is_response(status_code, 202):
        response_dict = response.json()
        if (
            "processes" in response_dict
            and "process_id" in response_dict["processes"][0]
        ):
            process_id = int(response_dict["processes"][0]["process_id"])

    return process_id


def increment_timepoint(DCCID: int):
    """
    Increament the existing timepoint for the subject, return the latest timepoint.
    :param DCCID:
    :return:
    """
    from LORIS.query import LORIS_query

    success, token = LORIS_query.login()
    if not success:
        raise ConnectionError("LORIS Login failed!")

    from LORIS.timepoint import LORIS_timepoint

    success, timepoint = LORIS_timepoint.increaseTimepoint(token, DCCID)
    if not success:
        raise ConnectionError(
            "LORIS not responsive while trying to increase timepoints!"
        )
    return timepoint


def create_candidate(project, birthday, gender) -> (bool, int, int):
    """
    Check both the creation and deletion of the subject for LORIS.
    :return:
    """

    response_success, token = LORIS_query.login()

    if not response_success:
        raise ConnectionError("LORIS Login failed!")

    success, DCCID = LORIS_candidates.createCandidate(token, project, birthday, gender)
    if not success:
        raise ConnectionError("LORIS not responsive while trying to create candidate")

    # responded, success = LORIS_candidates.checkDCCIDExist(token, DCCID)
    # assert responded
    # assert success

    success, PSCID = LORIS_candidates.checkDCCIDExist(token, DCCID)
    if not success:
        raise ConnectionError("LORIS not responsive while checking DCCID existencen.")

    success, timepoint = LORIS_timepoint.increaseTimepoint(token, DCCID)
    if not success:
        raise ConnectionError("LORIS not responsive while increasing timepoint.")
    return success, DCCID, PSCID


def get_all_timepoints(DCCID: int) -> List[str]:
    """
    Get a list of all possible timepoints associated with a DCCID.
    :param DCCID:
    :return:
    """

    # Get token.
    response_success, token = LORIS_query.login()
    if not response_success:
        raise ConnectionError

    # Get Candidate JSON.
    response_success, candidate_json = LORIS_query.getCNBP(
        token, "candidates/" + str(DCCID)
    )
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
    :return:
    """
    # Get token.
    response_success, token = LORIS_query.login()
    if not response_success:
        raise ConnectionError

    # Get Candidate JSON.
    visits = get_all_timepoints(DCCID)

    list_series_UID = []

    # Loop through all visits.
    if len(visits) > 0:

        # Get dicom series info and then make sure they have series UID and then return them.
        for visit in visits:

            response_success, dicom_info = LORIS_query.getCNBP(
                token, f"candidates/{str(DCCID)}/{visit}/dicoms"
            )

            if "DicomTars" in dicom_info:
                list_dicom_tars = dicom_info["DicomTars"]
                for dicom_tar in list_dicom_tars:
                    if "SeriesInfo" in dicom_tar:
                        list_seires = dicom_tar["SeriesInfo"]
                        for series in list_seires:
                            list_series_UID.append(series["SeriesUID"])
    return list_series_UID


def upload_visit_DICOM(local_path: str, DCCID: int, VisitLabel: str, isPhantom: bool):
    """
    A custom end point where we specify the information for the file to be uploaded.
    Note that header is VERY unique.
    :param local_path:
    :param DCCID:
    :param VisitLabel:
    :return:
    """
    from LORIS.validate import LORIS_validation
    from LORIS.timepoint import LORIS_timepoint

    # Validations:
    if not os.path.isfile(local_path):
        error_string = f"{local_path} is not a valid path to a file to be uploaded. "
        logger.error(error_string)
        raise FileNotFoundError(error_string)

    if not LORIS_validation.validate_DCCID(DCCID):
        error_string = f"Provided DCCID: {DCCID} is invalid."
        logger.error(error_string)
        return ValueError(error_string)

    if not LORIS_timepoint.check_timepoint_compliance(VisitLabel):
        error_string = f"Provided timepoint:{VisitLabel} is invalid."
        logger.error(error_string)
        return ValueError(error_string)

    filename = os.path.basename(local_path)

    # Get Endpoint: Generate the proper end point.
    endpoint = f"/candidates/{DCCID}/{VisitLabel}/dicoms/{filename}"

    # Get Data: Read file into filestream object data
    data = open(local_path, "rb")

    # Get token.
    response_success, token = LORIS_query.login()
    if not response_success:
        error_string = f"Failed to login to LORIS. Check internet connections."
        logger.error(error_string)
        raise ConnectionError(error_string)

    # Get the status code and process the atual
    status_code, response = LORIS_query.putCNBPDICOM(token, endpoint, data, isPhantom)

    # Close Data connection.
    data.close()

    # log the response code.
    logger.debug(response)

    return process_upload_response(response)


def process_upload_response(response):
    """
    Check the upload response and then try to extract the process ID and UploadID
    :param response:
    :return:
    """

    # Check if it is 403: permission error.
    if LORIS_helper.is_response(response.status_code, 403):
        warning_string = "The credential in the configuration for uploading to LORIS is incorrect, you do not have the credential to upload files!"
        logger.critical(warning_string)
        raise ValueError(warning_string)

    # Check for when the response is properly 200.
    elif LORIS_helper.is_response(response.status_code, 202):

        logger.info("Status Code: 202 received properly.")
        logger.info("Attempting to decode the JSON response:")

        # Convert to JSON.
        json_response = response.json()

        """
        The Keys Will return: 
            MRI upload ID
            Status
            Processes:
        """

        # If there is mri upload ID, return it, other wise, do not return.
        if "processes" in json_response:
            # fixme: should attempt ot extract not only MRI_upload ID but also the process ID to return
            return 0

        elif "mri_upload_id" in json_response:
            upload_id = json_response["mri_upload_id"]
            logger.debug(
                f"Successfully uploaded and server returned 202 with Upload ID of:{upload_id}"
            )
            return upload_id
        else:
            warning_string = "Successfully uploaded and server returned 202, but returned JSON does not contain 'mri_upload_id'"
            logger.error(warning_string)
            raise ValueError(warning_string)

    # other. non 200 response.
    elif not LORIS_helper.is_response(response.status_code, 202):
        warning_string = f"Upload process has returned a non-202 RESPONSE. Status code returned is {response.status_code}"
        logger.critical(warning_string)
        raise ValueError(warning_string)

    else:
        warning_string = "Unanticipated status code condition encountered."
        logger.error(warning_string)
        raise UnboundLocalError(warning_string)


def old_upload(local_path):
    """
    OBSOLETE Upload file to incoming folder.
    :param local_path:
    :return:
    """

    ProxyIP = config_get("ProxyIP")
    ProxyUsername = config_get("ProxyUsername")
    ProxyPassword = config_get("ProxyPassword")
    LORISHostIP = config_get("LORISHostIP")
    LORISHostUsername = config_get("LORISHostUsername")
    LORISHostPassword = config_get("LORISHostPassword")

    Client = LORIS_helper.getProxySSHClient(
        ProxyIP,
        ProxyUsername,
        ProxyPassword,
        LORISHostIP,
        LORISHostUsername,
        LORISHostPassword,
    )

    file_name = os.path.basename(local_path)
    LORIS_helper.uploadThroughClient(Client, "//data/incoming/" + file_name, local_path)


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
