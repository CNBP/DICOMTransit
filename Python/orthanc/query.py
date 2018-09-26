import requests
import logging
import os
import shutil
import zipfile
import sys
from dotenv import load_dotenv
from PythonUtils.file import is_name_unique


logging.basicConfig(stream=sys.stdout, level=logging.INFO)

class orthanc_query:

    @staticmethod
    def getOrthanc(endpoint):
        """
        Get from a Orthanc endpoint
        :param endpoint:
        :return: bool on if such PSCID (INSTITUTIONID + PROJECTID + SUBJECTID) exist already.
        """
        logger = logging.getLogger('Orthanc_get')
        logger.info("Getting Orthanc endpoint: "+ endpoint + "at")
        success = load_dotenv()
        if not success:
            raise ImportError("Credential .env NOT FOUND! Please ensure .env is set with all the necessary credentials!")
        url = os.getenv("OrthancURL")
        updatedurl = url + endpoint
        logger.info(updatedurl)

        with requests.Session() as s:
            r = s.get(updatedurl)
            logger.info("Get Result:" + str(r.status_code) + r.reason)

            return r.status_code, r.json()

    @staticmethod
    def postOrthanc(endpoint, data):
        """
        Get from a Orthanc endpoint
        :param endpoint:
        :param data
        :return: bool on if such PSCID (INSTITUTIONID + PROJECTID + SUBJECTID) exist already.
        """
        logger = logging.getLogger('Orthanc_post')
        logger.info("Post Orthanc endpoint: "+ endpoint + "at")
        success = load_dotenv()
        if not success:
            raise ImportError("Credential .env NOT FOUND! Please ensure .env is set with all the necessary credentials!")
        url = os.getenv("OrthancURL")
        updatedurl = url + endpoint
        logger.info(updatedurl)

        with requests.Session() as s:
            r = s.post(updatedurl, files=data)

            logger.info("Post Result:" + str(r.status_code) + r.reason)

            return r.status_code, r

    @staticmethod
    def deleteOrthanc(endpoint):
        """
        Delete from a Orthanc endpoint
        :param endpoint:
        :return: bool on if such PSCID (INSTITUTIONID + PROJECTID + SUBJECTID) exist already.
        """
        logger = logging.getLogger('Orthanc_delete')
        logger.info("Deleting Orthanc endpoint: "+ endpoint + "at")
        success = load_dotenv()
        if not success:
            raise ImportError("Credential .env NOT FOUND! Please ensure .env is set with all the necessary credentials!")
        url = os.getenv("OrthancURL")
        updatedurl = url + endpoint
        logger.info(updatedurl)

        with requests.Session() as s:
            r = s.delete(updatedurl)
            logger.info("Deletion Result:" + str(r.status_code) + r.reason)

        return r.status_code, r.json()

    @staticmethod
    def getPatientZipOrthanc(endpoint):
        """
        Get Orthanc endpoint archive ZIP files.
        :param endpoint:
        :return: status of the get requests, and the actual local file name saved in the process.
        """
        logger = logging.getLogger('Orthanc_getzip')
        logger.info("Downloading Orthanc endpoint: " + endpoint + " at")
        success = load_dotenv()
        if not success:
            raise ImportError("Credential .env NOT FOUND! Please ensure .env is set with all the necessary credentials!")
        url = os.getenv("OrthancURL")

        # endpiont should be something like /studies/SUTDY_UUID/
        query = url + "patients/" + endpoint + '/archive'
        logger.info(query)

        with requests.Session() as s:
            r = s.get(query, stream=True, verify=False)  # auth=(orthanc_user, orthanc_password)

            local_filename = endpoint + ".zip"
            # NOTE the stream=True parameter
            with open(local_filename, 'wb') as f:
                for chunk in r.iter_content(chunk_size=1024):
                    if chunk:  # filter out keep-alive new chunks
                        f.write(chunk)
                        # f.flush() commented by recommendation from J.F.Sebastian
        logger.info(str(r.status_code) + r.reason)
        return r.status_code, local_filename

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
