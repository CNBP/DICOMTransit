from LORIS.candidates import LORIS_candidates
from dotenv import load_dotenv
import os
from LORIS.helper import LORIS_helper
from LORIS.query import LORIS_query
from LORIS.timepoint import LORIS_timepoint
"""
Everything here, should have its own login sessions as tokens are not shared at this high level function.  

"""

def create_new(CNBPID):
    """
    Check both the creation and deletion of the subject for LORIS.
    :return:
    """

    response_success, token = LORIS_query.login()

    if not response_success:
        raise ConnectionError

    # Example PSC ID.
    PSCID = CNBPID

    success, DCCID = LORIS_candidates.createCandidateCNBP(token, PSCID)

    success, timepoint = LORIS_timepoint.increaseTimepoint(token, DCCID)

    return success, DCCID


def upload(local_path):
    """
    Upload file to incoming folder.
    :param local_path:
    :return:
    """
    assert load_dotenv()
    ProxyIP = os.getenv("ProxyIP")
    ProxyUsername = os.getenv("ProxyUsername")
    ProxyPassword = os.getenv("ProxyPassword")
    LORISHostIP = os.getenv("LORISHostIP")
    LORISHostUsername = os.getenv("LORISHostUsername")
    LORISHostPassword = os.getenv("LORISHostPassword")

    Client = LORIS_helper.getProxySSHClient(ProxyIP, ProxyUsername, ProxyPassword, LORISHostIP, LORISHostUsername,
                                            LORISHostPassword)

    file_name = os.path.basename(local_path)
    LORIS_helper.uploadThroughClient(Client, "//data/incoming/"+file_name, local_path)

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
            # r = s.post(r"http://dev.cnbp.ca/cnbp/upload_dicoms.php", data=data_json)

            # todo: Non-secure version until we fix the SSL issue
            r = requests.api.request('post', "https://dev.cnbp.ca/cnbp/upload_dicoms.php", data=data_json, verify=False)

            print("Post Result:" + str(r.status_code) + r.reason)


if __name__ == "__main__":
    import DICOM.API

    #CNBPID = "VTXGL019998"

    #create new PSCID:, get DCCID
    #success, DCCID = create_new("VTXGL019998")

    # Create Timepoint 1.
    # Manually Done for now.

    #Generate new string with everything.
    #zip_name = "VTXGL019998"+"_"+DCCID+"_"+"V1"
    zip_name = "VTXGL019998"+"_"+"671603"+"_"+"V1"

    # Anonymize to Zip
    #DICOM.API.anonymize_to_zip(r"C:\Users\dyt81\Downloads\TestAnonymize", zip_name)

    # Upload
    #upload(os.path.join(r"C:\GitHub\DICOMTransit\Python\data_archives", zip_name+".zip"))

    # Trigger insertion.
    trigger_insertion(zip_name)