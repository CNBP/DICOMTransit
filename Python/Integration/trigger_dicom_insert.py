import sys
import requests
import json

def trigger_dicom_insert(scans):
    """ 
    Triggers insertion of uploaded dicom files that are not yet inserted into
    Loris.
    :param scans: An array of dictionaries that represent the params for each
    dicom file to insert
    :returns:
    """
    # Create a dictionary with the required key 'dicoms'. Key value is scans
    p = {}
    p['dicoms'] = scans

    # Convert to json.
    # See https://pythonspot.com/json-encoding-and-decoding-with-python/
    tmp = json.dumps(p, ensure_ascii=False)

    # Put json into dictionary as a value of the required key 'file_data'
    payload = {"file_data": tmp}
    print(payload)

    # Need to fix the load_dotenv call. Currently not getting trigger url
    #from dotenv import load_dotenv
    #trigger_dicom_insertion_url = load_dotenv("triggerDicomInsertionURL")

    # Trigger insertion by doing HTTP POST of payload to endpoint
    s = requests.post("https://dev.cnbp.ca/cnbp/upload_dicoms.php",
                      data=payload)
    # Disable use of dotenv value because i can't make it work for now
    #s = requests.post(trigger_dicom_insertion_url, data=payload)
    #print(trigger_dicom_insertion_url)
    print(s.text)

if __name__ == "__main__":
    zip_name = "VTXGL019996_206839_V1"

    f1={}
    f1['file'] = "/data/incoming/" + zip_name + ".zip"
    f1['phantom'] = "N"
    f1['candidate'] = zip_name
    scans =[f1]
    trigger_dicom_insert(scans)