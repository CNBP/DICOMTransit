import json
import logging
import requests

from DICOMTransit.LORIS.helper import LORIS_helper
from DICOMTransit.settings import config_get
from urllib.parse import urljoin
from furl import furl

logger = logging.getLogger()


class LORIS_query:
    @staticmethod
    def login():
        """
        Logs into LORIS using the stored credential. Must use PyCurl as Requests is not working.
        :return: BOOL if or not it is successful. also, the JSON token that is necessary to conduct further transactions.
        """

        from DICOMTransit.settings import config_get

        username = config_get("LORISusername")
        password = config_get("LORISpassword")

        data = json.dumps({"username": username, "password": password})

        # Login URL
        url = config_get("LORISurl")

        if type(url) is furl:
            updated_url = url.url + "login"
        else:
            updated_url = url + "login"

        # requests style login # NOT WORKING!
        r = requests.post(updated_url, data=data)

        logger.debug(str(r.status_code) + r.reason)

        response_json = r.json()

        return LORIS_helper.is_response(r.status_code, 200), response_json.get("token")

    @staticmethod
    def getCNBP(token, endpoint):
        """
        Get from a CNBP LORIS database endpoint
        :param token:
        :param endpoint:
        :return: bool on if such PSCID (INSTITUTIONID + PROJECTID + SUBJECTID) exist already.
        """

        logger.debug(f"Getting LORIS endpoint: {endpoint} at")
        url = config_get("LORISurl")
        updatedurl = urljoin(url, endpoint)
        logger.debug(updatedurl)
        HEADERS = {"Authorization": "token {}".format(token)}

        with requests.Session() as s:
            s.headers.update(HEADERS)
            r = s.get(updatedurl)
            logger.debug(f"Get Result: {str(r.status_code)} {r.reason}")

            return r.status_code, r.json()

    @staticmethod
    def postCNBP(token, endpoint, data):
        """
        post some data to a LORIS end point.
        :param token:
        :param endpoint:
        :param data:
        :return: bool on if request is successful, r for the request (CAN BE NULL for 201 based requests)
        """

        logger.debug("Posting data to: " + endpoint)
        logger.debug("Data: " + data)
        url = config_get("LORISurl")
        updatedurl = urljoin(url, endpoint)
        updatedurl = url + endpoint

        HEADERS = {"Authorization": "token {}".format(token)}

        with requests.Session() as s:
            s.headers.update(HEADERS)
            r = s.post(updatedurl, data=data)
            logger.debug(f"Post Result: {str(r.status_code)} {r.reason}")

            return r.status_code, r

    @staticmethod
    def putCNBP(token, endpoint, data):
        """
        Put some data to a LORIS end point.
        :param token:
        :param endpoint:
        :param data:
        :return: bool on if request is successful, r for the request (CAN BE NULL for 201 based requests)
        """

        logger.debug("Putting data to: " + endpoint)
        logger.debug("Data: " + data)

        url = config_get("LORISurl")

        updatedurl = url + endpoint

        HEADERS = {"Authorization": "token {}".format(token)}

        with requests.Session() as s:
            s.headers.update(HEADERS)
            r = s.put(updatedurl, data=data)
            logger.debug(f"Put Result: {str(r.status_code)} {r.reason}")
            return r.status_code, r

    @staticmethod
    def putCNBPDICOM(token, endpoint, imaging_data, isPhantom: bool = False):
        """
        Put some data to a LORIS end point.
        :param token:
        :param endpoint:
        :param imaging_data:
        :param isPhantom: whether the upload is a phantom data or not.
        :return: bool on if request is successful, r for the request (CAN BE NULL for 201 based requests)
        """

        logger.debug(f"Uploading Imaging data to: {endpoint}")

        url = config_get("LORISurl")
        updatedurl = url + endpoint

        if isPhantom:
            HEADERS = {"Authorization": f"token {token}", "X-Is-Phantom": "1"}
        else:
            HEADERS = {"Authorization": f"token {token}", "X-Is-Phantom": "0"}

        with requests.Session() as s:
            s.headers.update(HEADERS)
            r = s.put(updatedurl, data=imaging_data)
            logger.debug(f"Put Result: {str(r.status_code)} {r.reason}")

            return r.status_code, r


# Only executed when running directly.
if __name__ == "__main__":
    # print(login())
    # getCNBP("projects")
    Success, token = LORIS_query.login()
    # print("Test complete")
