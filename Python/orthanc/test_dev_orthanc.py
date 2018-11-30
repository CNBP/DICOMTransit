from pydicom.data import get_testdata_files
from orthanc.query import orthanc_query
from LORIS.helper import LORIS_helper
from orthanc.API import get_local_orthanc_credentials
import unittest
import orthanc.API
from PythonUtils.env import load_dotenv_var



class UT_LocalOrthanc(unittest.TestCase):


    @staticmethod
    def uploadExamples():
        file_list = get_testdata_files("[Ss][Mm][Aa][Ll][Ll]")


        for file in file_list:
            print(file)
            upload_files = {'upload_file': open(file, 'rb')}
            orthanc_url = load_dotenv_var("TestOrthancIP")
            orthanc_instance_url = orthanc_url + "instances/"

            status, r = orthanc_query.postOrthanc(orthanc_instance_url, upload_files)
            assert(LORIS_helper.is_response_success(status, 200))
            assert(r.json())

        # Note that this will database several subjects.

    @staticmethod
    def test_getSubjects():
        UT_LocalOrthanc.uploadExamples()
        url, user, password = orthanc.API.get_local_orthanc_credentials()
        subject_list = orthanc.API.get_list_of_subjects(url, user, password)
        assert len(subject_list) > 0
        return subject_list


    @staticmethod
    def test_deleteSubjects():
        list_subjects = UT_LocalOrthanc.test_getSubjects()
        for subject in list_subjects:
            reseponse_code, _ = orthanc_query.deleteOrthanc("patients/"+subject)
            assert (LORIS_helper.is_response_success(reseponse_code, 200))

    @staticmethod
    def test_getSubjectZip(): # todo: review this in unit test
        url, user, password = orthanc.API.get_local_orthanc_credentials()
        list_subjects = UT_LocalOrthanc.test_getSubjects()
        for subject in list_subjects:
            endpoint = url + "patients/" + subject
            orthanc.API.get_subject_zip(endpoint, user, password)

if __name__ == "__main__":
    UT_LocalOrthanc.test_getSubjectZip()
