from pydicom.data import get_testdata_files
from orthanc.query import orthanc_query
from LORIS.helper import LORIS_helper
from orthanc.API import get_dev_orthanc_credentials, get_all_subject_StudyUIDs
import unittest
import pytest
import orthanc.API
from PythonUtils.env import is_travis
import urllib.parse

if is_travis():
    pytest.skip(
        "Skipping test requiring private database access", allow_module_level=True
    )


class UT_DevOrthanc(unittest.TestCase):

    credential = orthanc.API.get_dev_orthanc_credentials()

    def uploadExamples(self):
        file_list = get_testdata_files("[Ss][Mm][Aa][Ll][Ll]")
        for file in file_list:
            print(file)
            upload_files = {"upload_file": open(file, "rb")}
            orthanc_instance_url = urllib.parse.urljoin(
                UT_DevOrthanc.credential.url, "instances"
            )

            status, r = orthanc_query.postOrthanc(
                orthanc_instance_url, UT_DevOrthanc.credential, upload_files
            )
            assert LORIS_helper.is_response_success(status, 200)
            assert r.json()

        # Note that this will database several subjects.

    def test_getStudies(self):
        self.uploadExamples()

        subject_list = orthanc.API.get_all_subject_StudyUIDs(self.credential)
        assert len(subject_list) > 0
        return subject_list

    def test_deleteStudies(self):
        list_subjects = self.test_getStudies()

        patients_url = urllib.parse.urljoin(UT_DevOrthanc.credential.url, "studies/")

        for subject in list_subjects:
            patient_url = urllib.parse.urljoin(patients_url, f"{subject}")
            reseponse_code, _ = orthanc_query.deleteOrthanc(
                patient_url, self.credential
            )
            assert LORIS_helper.is_response_success(reseponse_code, 200)

    def test_get_all_subject_StudyUID(self):
        get_all_subject_StudyUIDs(UT_DevOrthanc.credential)

    def test_getSubjectZip(self):
        url, user, password = orthanc.API.get_prod_orthanc_credentials()
        list_subjects = self.test_getStudies()
        patients_url = urllib.parse.urljoin(UT_DevOrthanc.credential.url, "patients/")
        for subject in list_subjects:
            patient_url = urllib.parse.urljoin(patients_url, f"{subject}/")
            patient_file_url = urllib.parse.urljoin(patient_url, "archive")
            orthanc.API.get_StudyUID_zip(patient_file_url, self.credential)


if __name__ == "__main__":
    UT_DevOrthanc.test_getSubjectZip()
