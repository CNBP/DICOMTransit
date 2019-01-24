from pydicom.data import get_testdata_files
from orthanc.query import orthanc_query
from LORIS.helper import LORIS_helper
import unittest
import orthanc.API
import pytest

if True:
#if not is_travis():
    pytest.skip("Skipping test requiring private database access", allow_module_level=True)

class UT_ProdOrthanc(unittest.TestCase):

    # MUST ensure TravisCI LORIS also deploy with the proper setting with regard to the ORTHANC authentication.
    # This attempts to access the production Orthanc from the local environment and then check if upupload and download work.

    url, user, password = orthanc.API.get_prod_orthanc_credentials()


    def uploadExamples(self):
        file_list = get_testdata_files("[Ss][Mm][Aa][Ll][Ll]")
        for file in file_list:
            print(file)
            upload_files = {'upload_file': open(file, 'rb')}
            orthanc_instance_url = self.url + "instances/"

            status, r = orthanc_query.postOrthanc(orthanc_instance_url, self.user, self.password, upload_files)
            assert(LORIS_helper.is_response_success(status, 200))
            assert(r.json())

        # Note that this will database several subjects.


    def test_getSubjects(self):
        UT_ProdOrthanc.uploadExamples()

        subject_list = orthanc.API.get_list_of_subjects(self.url, self.user, self.password)
        assert len(subject_list) > 0
        return subject_list



    def test_deleteSubjects(self):
        list_subjects = UT_ProdOrthanc.test_getSubjects()
        for subject in list_subjects:
            reseponse_code, _ = orthanc_query.deleteOrthanc(f"patients/{subject}", self.user, self.password)
            assert (LORIS_helper.is_response_success(reseponse_code, 200))


    def test_getSubjectZip(self):
        url, user, password = orthanc.API.get_prod_orthanc_credentials()
        list_subjects = UT_ProdOrthanc.test_getSubjects()
        for subject in list_subjects:
            endpoint = f"{url}patients/{subject}"
            orthanc.API.get_subject_zip(endpoint, user, password)

if __name__ == "__main__":
    UT_ProdOrthanc.test_getSubjectZip()
