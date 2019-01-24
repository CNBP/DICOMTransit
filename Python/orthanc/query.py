import requests
import logging
import os
import shutil
import zipfile
import sys
from PythonUtils.file import is_name_unique, unique_name
from requests.auth import HTTPBasicAuth
from settings import config_get

logging.basicConfig(stream=sys.stdout, level=logging.INFO)

class orthanc_query:

    @staticmethod
    def authenticateOrthanc():
        #todo: all the get, set can be potentially using a decorator function to authenticate.
        raise NotImplementedError
        pass

    @staticmethod
    def getOrthanc_noauth(endpoint):
        """
        Get from a Orthanc endpoint
        :param endpoint:
        :return: bool on if such PSCID (INSTITUTIONID + PROJECTID + SUBJECTID) exist already.
        """
        logger = logging.getLogger('Orthanc_get')
        logger.debug("Getting Orthanc endpoint: "+ endpoint)

        with requests.Session() as s:
            r = s.get(endpoint)
            logger.debug(f"Get Result: {str(r.status_code)} {r.reason}")
            return r.status_code, r.json()


    @staticmethod
    def getOrthanc(endpoint, orthanc_user, orthanc_password):
        """
        Get from a Orthanc endpoint
        :param endpoint:
        :return: bool on if such PSCID (INSTITUTIONID + PROJECTID + SUBJECTID) exist already.
        """
        logger = logging.getLogger('Orthanc_get')
        logger.debug("Getting Orthanc endpoint: "+ endpoint)

        with requests.Session() as s:
            r = s.get(endpoint, auth=HTTPBasicAuth(orthanc_user, orthanc_password))
            logger.debug(f"Get Result: {str(r.status_code)} {r.reason}")
            return r.status_code, r.json()


    @staticmethod
    def postOrthanc(endpoint, orthanc_user, orthanc_password, data):
        """
        Get from a Orthanc endpoint
        :param endpoint:
        :param data
        :return: bool on if such PSCID (INSTITUTIONID + PROJECTID + SUBJECTID) exist already.
        """
        logger = logging.getLogger('Orthanc_post')
        logger.debug("Post Orthanc endpoint: "+ endpoint)
        with requests.Session() as s:
            r = s.post(endpoint, auth=HTTPBasicAuth(orthanc_user, orthanc_password), files=data)
            logger.debug(f"Post Result: {str(r.status_code)} {r.reason}")
            return r.status_code, r

    @staticmethod
    def deleteOrthanc(endpoint, orthanc_user, orthanc_password):
        """
        Delete from a Orthanc endpoint
        :param endpoint:
        :return: bool on if such PSCID (INSTITUTIONID + PROJECTID + SUBJECTID) exist already.
        """
        logger = logging.getLogger('Orthanc_delete')
        logger.debug(f"Deleting Orthanc endpoint: {endpoint} at")
        with requests.Session() as s:
            r = s.delete(endpoint, auth=HTTPBasicAuth(orthanc_user, orthanc_password))
            logger.debug(f"Deletion Result: {str(r.status_code)} {r.reason}")
        return r.status_code, r.json()

    @staticmethod
    def getPatientZipOrthanc(endpoint, orthanc_user, orthanc_password):
        """
        Get Orthanc endpoint archive ZIP files.
        :param endpoint:
        :return: status of the get requests, and the actual local file name saved in the process.
        """

        logger = logging.getLogger('Orthanc_getzip')
        logger.debug("Downloading Orthanc endpoint: {endpoint}")

        zip_path = config_get("zip_storage_location")
        with requests.Session() as s:
            r = s.get(endpoint, stream=True, verify=False, auth=HTTPBasicAuth(orthanc_user, orthanc_password))

            local_file_full_path = f"{zip_path}{unique_name()}.zip"
            # NOTE the stream=True parameter
            with open(local_file_full_path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=1024):
                    if chunk:  # filter out keep-alive new chunks
                        f.write(chunk)
                        # f.flush() commented by recommendation from J.F.Sebastian
        logger.debug(str(r.status_code) + r.reason)
        return r.status_code, local_file_full_path

    @staticmethod
    def flatUnZip(input_zip, out_dir):
        """
        Inspired by https://stackoverflow.com/questions/4917284/extract-files-from-zip-without-keeping-the-structure-using-python-zipfile
        Added function to hanlde non-unique file names which are probably standarderized by Orthanc.
        :param input_zip:
        :param out_dir:
        :return:
        """

        with zipfile.ZipFile(input_zip) as zip_file:
            for member in zip_file.namelist():
                filename = os.path.basename(member)
                # skip directories
                if not filename:
                    continue

                # copy file (taken from zipfile's extract)
                source = zip_file.open(member)

                proposed_filename = os.path.join(out_dir, filename)
                # handle duplicate names!
                _, unique_output_filename = is_name_unique(proposed_filename)
                target = open(unique_output_filename, "wb")
                with source, target:
                    shutil.copyfileobj(source, target)
