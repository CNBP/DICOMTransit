import base64
import sys

import requests
import logging
import os
import shutil
import zipfile
import collections
import urllib.parse
from PythonUtils.file import is_name_unique, unique_name
from requests.auth import HTTPBasicAuth


from settings import config_get
from tqdm import tqdm

logger = logging.getLogger()

orthanc_credential = collections.namedtuple("orthanc_credential", "url user password")


class orthanc_query:
    @staticmethod
    def authenticateOrthanc():
        # todo: all the get, set can be potentially using a decorator function to authenticate.
        raise NotImplementedError
        pass

    @staticmethod
    def getOrthanc_noauth(endpoint):
        """
        Get from a Orthanc endpoint
        :param endpoint:
        :return: bool on if such PSCID (INSTITUTIONID + PROJECTID + SUBJECTID) exist already.
        """

        logger.debug(f"Getting Orthanc endpoint: {endpoint}")

        with requests.Session() as s:
            r = s.get(endpoint)
            logger.debug(f"Get Result: {str(r.status_code)} {r.reason}")
            return r.status_code, r.json()

    @staticmethod
    def getOrthanc(endpoint, orthanc_credential):
        """
        Get from a Orthanc endpoint
        :param endpoint:
        :return: bool on if such PSCID (INSTITUTIONID + PROJECTID + SUBJECTID) exist already.
        """

        logger.debug("Getting Orthanc endpoint: " + endpoint)

        with requests.Session() as s:
            r = s.get(
                endpoint,
                auth=HTTPBasicAuth(
                    orthanc_credential.user, orthanc_credential.password
                ),
            )
            logger.debug(f"Get Result: {str(r.status_code)} {r.reason}")
            return r.status_code, r.json()

    @staticmethod
    def postOrthanc(endpoint, credential: orthanc_credential, data):
        """
        Get from a Orthanc endpoint
        :param endpoint:
        :param data
        :return: bool on if such PSCID (INSTITUTIONID + PROJECTID + SUBJECTID) exist already.
        """

        logger.debug("Post Orthanc endpoint: " + endpoint)
        with requests.Session() as s:
            r = s.post(
                endpoint,
                auth=HTTPBasicAuth(credential.user, credential.password),
                files=data,
            )
            logger.debug(f"Post Result: {str(r.status_code)} {r.reason}")
            return r.status_code, r

    @staticmethod
    def deleteOrthanc(endpoint, credential: orthanc_credential):
        """
        Delete from a Orthanc endpoint
        :param endpoint:
        :return: bool on if such PSCID (INSTITUTIONID + PROJECTID + SUBJECTID) exist already.
        """

        logger.debug(f"Deleting Orthanc endpoint: {endpoint} at")
        with requests.Session() as s:
            r = s.delete(
                # form the full path to the end point by combining the URL with the end point.
                urllib.parse.urljoin(credential.url, endpoint),
                auth=HTTPBasicAuth(credential.user, credential.password)
            )
            logger.debug(f"Deletion Result: {str(r.status_code)} {r.reason}")
        return r.status_code, r.json()

    @staticmethod
    def getZipFromOrthanc(endpoint, credential: orthanc_credential):
        """
        Get Orthanc endpoint archive ZIP files.
        :param endpoint:
        :return: status of the get requests, and the actual local file name saved in the process.
        """

        logger.debug(f"Downloading Orthanc endpoint: {endpoint}")

        zip_path = config_get("ZipPath")
        with requests.Session() as s:
            r = s.get(
                endpoint,
                stream=True,
                verify=False,
                auth=HTTPBasicAuth(credential.user, credential.password),
            )

            # Compute total size to be downloaded
            total_size = int(r.headers.get("content-length", 0))
            total_size_mb = round(total_size / 1024 / 1024, 3)
            # Generate the full output path
            local_file_full_path = os.path.join(zip_path, f"{unique_name()}.zip")

            progress_bar = tqdm(unit="Mb", total=total_size_mb, position=0)

            # NOTE the stream=True parameter
            with open(local_file_full_path, "wb") as f:
                for chunk in r.iter_content(chunk_size=1024):
                    if chunk:  # filter out keep-alive new chunks
                        chunk_mb = round(len(chunk) / 1024 / 1024, 3)
                        progress_bar.update(chunk_mb)
                        f.write(chunk)

        logger.debug(str(r.status_code) + r.reason)
        logger.info(f"Download to {local_file_full_path} is fully complete!")
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
            for member in tqdm(zip_file.namelist(), position=0):
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

    @staticmethod
    def upload(path, credential: orthanc_credential, data):
        """
        todo: should really bench mark this library vs the request library we typically use to upload for the rest of the project.
        A method to upload files to orthanc.

        # Orthanc - A Lightweight, RESTful DICOM Store
        # Copyright (C) 2012-2016 Sebastien Jodogne, Medical Physics
        # Department, University Hospital of Liege, Belgium
        # Copyright (C) 2017-2019 Osimis S.A., Belgium

        # This program is free software: you can redistribute it and/or
        # modify it under the terms of the GNU General Public License as
        # published by the Free Software Foundation, either version 3 of the
        # License, or (at your option) any later version.

        # This program is distributed in the hope that it will be useful, but
        # WITHOUT ANY WARRANTY; without even the implied warranty of
        # MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
        # General Public License for more details.

        # You should have received a copy of the GNU General Public License
        # along with this program. If not, see <http://www.gnu.org/licenses/>.

        :param path:
        :return:
        """

        # Try to upload
        try:


            response_code, response_ = orthanc_query.postOrthanc(
                urllib.parse.urljoin(credential.url, "instances"), credential, data
            )
            logger.debug("Importing %s" % path)

            if response_code == 200:
                logger.debug(" => success\n")
                return 1
            else:
                logger.warning(" => failure (Is it a DICOM file?)\n")
                return 0
        except Exception as e:
            logger.error(e)
            logger.error(
                " => unable to connect (Is Orthanc running? Is there a password?)\n"
            )
            return 0
