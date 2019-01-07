import json
import requests
from settings import get


def trigger_dicom_insert(scans):
    """ 
    Triggers insertion of uploaded dicom files that are not yet inserted into
    Loris.
    :param scans: An array of dictionaries that represent the params for each
    dicom file to insert
    :returns:
    """
    # todo: 2018-11-30T133155EST should clean up here and ensure loading the URL using .env.
    # Create a dictionary with the required key 'dicoms'. Key value is scans
    p = {
        'dicoms' : scans
    }

    # Convert to json.
    # See https://pythonspot.com/json-encoding-and-decoding-with-python/
    tmp = json.dumps(p, ensure_ascii=False)

    # Put json into dictionary as a value of the required key 'file_data'
    payload = {"file_data": tmp}
    print(payload)

    # Need to fix the load_dotenv call. Currently not getting trigger url

    trigger_dicom_insertion_url = get("InsertionAPI")

    # Trigger insertion by doing HTTP POST of payload to endpoint
    s = requests.post(trigger_dicom_insertion_url, data=payload)
    # print(trigger_dicom_insertion_url)

    print(s.text)

if __name__ == "__main__":
    zip_name = "VTXGL019996_206839_V1"


    f1={
        'file' : "/data/incoming/" + zip_name + ".zip",
        'phantom' : "N",
        'candidate' : zip_name
    }
    scans = [f1]
    trigger_dicom_insert(scans)