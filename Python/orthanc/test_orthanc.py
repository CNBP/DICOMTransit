import os
from pydicom.data import get_testdata_files

from orthanc.query import getOrthanc, postOrthanc, deleteOrthanc, getPatientZipOrthanc, flatUnZip

from LORIS.helper import is_response_success, check_json


def uploadExamplesToOrthanc():
    file_list = get_testdata_files("[Ss][Mm][Aa][Ll][Ll]")
    for file in file_list:
        print(file)
        upload = {'upload_file': open(file, 'rb')}
        status, r = postOrthanc("instances/", upload)
        assert(is_response_success(status, 200))
        assert(check_json(r.json()))

    # Note that this will create several subjects.

def test_getSubjects():
    uploadExamplesToOrthanc()
    reseponse_code, list_subjects = getOrthanc("patients/")
    assert (is_response_success(reseponse_code, 200))
    return list_subjects


def test_deleteSubjects():
    list_subjects = test_getSubjects()
    for subject in list_subjects:
        reseponse_code, r = deleteOrthanc("patients/"+subject)
        assert (is_response_success(reseponse_code, 200))


def test_getSubjectZip():
    list_subjects = test_getSubjects()
    for subject in list_subjects:
        status, zip_file = getPatientZipOrthanc(subject)
        assert(is_response_success(status, 200))
        assert(os.path.exists(zip_file))
        my_dir = os.getcwd()
        flatUnZip(zip_file, my_dir)
        os.remove(zip_file)

if __name__ == "__main__":
    test_getSubjectZip()
