from pydicom.data import get_testdata_files
from orthanc.query import orthanc_query
from LORIS.helper import LORIS_helper
from orthanc.API import get_dev_orthanc_credentials
import unittest
import pytest
import orthanc.API
from PythonUtils.env import is_travis
import urllib.parse

if is_travis():
    pytest.skip("Skipping test requiring private database access", allow_module_level=True)

class UT_DevOrthanc(unittest.TestCase):

    url, user, password = orthanc.API.get_dev_orthanc_credentials()

    @staticmethod
    def uploadExamples():
        file_list = get_testdata_files("[Ss][Mm][Aa][Ll][Ll]")
        for file in file_list:
            print(file)
            upload_files = {'upload_file': open(file, 'rb')}
            orthanc_instance_url = urllib.parse.urljoin(UT_DevOrthanc.url, "instances")

            status, r = orthanc_query.postOrthanc(orthanc_instance_url, UT_DevOrthanc.user, UT_DevOrthanc.password, upload_files)
            assert (LORIS_helper.is_response_success(status, 200))
            assert (r.json())

        # Note that this will database several subjects.

    def test_getSubjects(self):
        UT_DevOrthanc.uploadExamples()

        subject_list = orthanc.API.get_list_of_subjects(self.url, self.user, self.password)
        assert len(subject_list) > 0
        return subject_list

    def test_deleteSubjects(self):
        list_subjects = self.test_getSubjects()

        patients_url = urllib.parse.urljoin(UT_DevOrthanc.url, "patients/")

        for subject in list_subjects:
            patient_url = urllib.parse.urljoin(patients_url, f"{subject}")
            reseponse_code, _ = orthanc_query.deleteOrthanc(patient_url, self.user, self.password)
            assert (LORIS_helper.is_response_success(reseponse_code, 200))

    def test_getSubjectZip(self):
        url, user, password = orthanc.API.get_prod_orthanc_credentials()
        list_subjects = self.test_getSubjects()
        patients_url = urllib.parse.urljoin(UT_DevOrthanc.url, "patients/")
        for subject in list_subjects:
            patient_url = urllib.parse.urljoin(patients_url, f"{subject}/")
            patient_file_url = urllib.parse.urljoin(patient_url, "archive")
            orthanc.API.get_subject_zip(patient_file_url, user, password)


if __name__ == "__main__":
    UT_DevOrthanc.test_getSubjectZip()
