from pydicom.data import get_testdata_files
from orthanc.query import orthanc_query
from LORIS.helper import LORIS_helper
import unittest
import orthanc.API

class UT_Orthanc(unittest.TestCase):

    @staticmethod
    def uploadExamplesToOrthanc():
        file_list = get_testdata_files("[Ss][Mm][Aa][Ll][Ll]")
        for file in file_list:
            print(file)
            upload = {'upload_file': open(file, 'rb')}
            status, r = orthanc_query.postOrthanc("instances/", upload)
            assert(LORIS_helper.is_response_success(status, 200))
            assert(r.json())

        # Note that this will database several subjects.

    @staticmethod
    def test_getSubjects():
        UT_Orthanc.uploadExamplesToOrthanc()
        subject_list = orthanc.API.get_list_of_subjects()
        assert len(subject_list) > 0
        return subject_list


    @staticmethod
    def test_deleteSubjects():
        list_subjects = UT_Orthanc.test_getSubjects()
        for subject in list_subjects:
            reseponse_code, _ = orthanc_query.deleteOrthanc("patients/"+subject)
            assert (LORIS_helper.is_response_success(reseponse_code, 200))

    @staticmethod
    def test_getSubjectZip():
        list_subjects = UT_Orthanc.test_getSubjects()
        for subject in list_subjects:
            orthanc.API.get_subject_zip(subject)

if __name__ == "__main__":
    UT_Orthanc.test_getSubjectZip()
