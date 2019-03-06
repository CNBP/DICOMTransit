from pydicom.data import get_testdata_files
from orthanc.query import orthanc_query
from LORIS.helper import LORIS_helper
from orthanc.API import get_dev_orthanc_credentials
import unittest
import orthanc.API



class UT_DevOrthanc(unittest.TestCase):

    url, user, password = orthanc.API.get_dev_orthanc_credentials()

    @staticmethod
    def uploadExamples():
        file_list = get_testdata_files("[Ss][Mm][Aa][Ll][Ll]")


        for file in file_list:
            print(file)
            files_upload = {'upload_file': open(file, 'rb')}
            endpoint = UT_DevOrthanc.url + "instances/"

            status, r = orthanc_query.postOrthanc(endpoint, UT_DevOrthanc.user, UT_DevOrthanc.password, files_upload)
            assert(LORIS_helper.is_response_success(status, 200))
            assert(r.json())

        # Note that this will database several subjects.


    @staticmethod
    def test_getSubjects():
        UT_DevOrthanc.uploadExamples()

        subject_list = orthanc.API.get_list_of_subjects(UT_DevOrthanc.url, UT_DevOrthanc.user, UT_DevOrthanc.password)
        assert len(subject_list) > 0
        return subject_list


    @staticmethod
    def test_deleteSubjects():
        list_subjects = UT_DevOrthanc.test_getSubjects()
        for subject in list_subjects:
            endpoint = UT_DevOrthanc.url + "patients/"+subject
            reseponse_code, _ = orthanc_query.deleteOrthanc(endpoint, UT_DevOrthanc.user, UT_DevOrthanc.password)
            assert (LORIS_helper.is_response_success(reseponse_code, 200))


    @staticmethod
    def test_getSubjectZip():
        list_subjects = UT_DevOrthanc.test_getSubjects()
        for subject in list_subjects:
            endpoint = f"{UT_DevOrthanc.url}patients/{subject}/archive"
            orthanc.API.get_subject_zip(endpoint, UT_DevOrthanc.user, UT_DevOrthanc.password)


if __name__ == "__main__":
    UT_DevOrthanc.test_getSubjectZip()
