from pydicom.data import get_testdata_files
from orthanc.query import orthanc_query
from LORIS.helper import LORIS_helper
import unittest
import orthanc.API
from PythonUtils.env import load_dotenv_var

class UT_ProdOrthanc(unittest.TestCase):

    @staticmethod
    def uploadExamples():
        file_list = get_testdata_files("[Ss][Mm][Aa][Ll][Ll]")
        for file in file_list:
            print(file)
            upload_files = {'upload_file': open(file, 'rb')}
            orthanc_url = load_dotenv_var("ProdOrthancIP")
            orthanc_user = load_dotenv_var("ProdOrthancUser")
            orthanc_password = load_dotenv_var("ProdOrthancPassword")
            orthanc_instance_url = orthanc_url + "instances/"

            status, r = orthanc_query.postOrthanc(orthanc_instance_url, orthanc_user, orthanc_password, upload_files)
            assert(LORIS_helper.is_response_success(status, 200))
            assert(r.json())

        # Note that this will database several subjects.

    @staticmethod
    def test_getSubjects():
        UT_ProdOrthanc.uploadExamples()
        subject_list = orthanc.API.get_list_of_subjects()
        assert len(subject_list) > 0
        return subject_list


    @staticmethod
    def test_deleteSubjects():
        list_subjects = UT_ProdOrthanc.test_getSubjects()
        for subject in list_subjects:
            reseponse_code, _ = orthanc_query.deleteOrthanc("patients/"+subject)
            assert (LORIS_helper.is_response_success(reseponse_code, 200))

    @staticmethod
    def test_getSubjectZip():
        list_subjects = UT_ProdOrthanc.test_getSubjects()
        for subject in list_subjects:
            orthanc.API.get_subject_zip(subject)

if __name__ == "__main__":
    UT_ProdOrthanc.test_getSubjectZip()
