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

    from dotenv import load_dotenv
    # Need to fix the load_dotenv call. Currently not getting trigger url
    trigger_dicom_insertion_url = load_dotenv("triggerDicomInsertionURL")
    # Trigger insertion by doing HTTP POST of payload to endpoint
    # Disable complaints about SSL for now by passing verify=False param
    s = requests.post("https://dev.cnbp.ca/cnbp/upload_dicoms.php",
                      data=payload)
    #s = requests.post(trigger_dicom_insertion_url, data=payload)
    print(trigger_dicom_insertion_url)
    #print(s.text)

