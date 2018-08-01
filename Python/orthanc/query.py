import requests
import logging
import os
import sys
from dotenv import load_dotenv

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logger = logging.getLogger('Orthanc Query:')


def getOrthanc(endpoint):
    """
    Get from a Orthanc endpoint
    :param endpoint:
    :return: bool on if such PSCID (INSTITUTIONID + PROJECTID + SUBJECTID) exist already.
    """
    logger = logging.getLogger('Orthanc_get')
    logger.info("Getting Orthanc endpoint: "+ endpoint + "at")
    load_dotenv()
    url = os.getenv("OrthancURL")
    updatedurl = url + endpoint
    logger.info(updatedurl)

    with requests.Session() as s:
        r = s.get(updatedurl)
        logger.info("Get Result:" + str(r.status_code) + r.reason)

        return r.status_code, r.json()

def postOrthanc(endpoint, data):
    """
    Get from a Orthanc endpoint
    :param endpoint:
    :return: bool on if such PSCID (INSTITUTIONID + PROJECTID + SUBJECTID) exist already.
    """
    logger = logging.getLogger('Orthanc_post')
    logger.info("Post Orthanc endpoint: "+ endpoint + "at")
    load_dotenv()
    url = os.getenv("OrthancURL")
    updatedurl = url + endpoint
    logger.info(updatedurl)

    with requests.Session() as s:
        r = s.post(updatedurl, files=data)

        logger.info("Post Result:" + str(r.status_code) + r.reason)

        return r.status_code, r


def deleteOrthanc(endpoint):
    """
    Delete from a Orthanc endpoint
    :param endpoint:
    :return: bool on if such PSCID (INSTITUTIONID + PROJECTID + SUBJECTID) exist already.
    """
    logger = logging.getLogger('Orthanc_delete')
    logger.info("Deleting Orthanc endpoint: "+ endpoint + "at")
    load_dotenv()
    url = os.getenv("OrthancURL")
    updatedurl = url + endpoint
    logger.info(updatedurl)

    with requests.Session() as s:
        r = s.delete(updatedurl)
        logger.info("Deletion Result:" + str(r.status_code) + r.reason)

        return r.status_code, r.json()

"""
def zipOrthanc(endpoint):
    query = orthanc_url + '/studies/' + orthanc_study_id + '/archive'
    response_study = requests.get(query, verify=False, \
                                  auth=(orthanc_user, orthanc_password))
    if response_study.status_code != 200:
        print
        'Problem retrieving study: ' + orthanc_study_id
        print
        response_study.status, response_study.reason
        continue
    print
    '   Retrieved: %s' % orthanc_study_id
    zip_content = response_study.content

    file_like_object = io.BytesIO(zip_content)
    zip_object = zipfile.ZipFile(file_like_object)
    for zip_name in zip_object.namelist():
        zip_object.extract(zip_name, some_destination_dir)
"""