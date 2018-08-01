from pydicom.data import get_testdata_files

from orthanc.query import getOrthanc, postOrthanc, deleteOrthanc

from LORIS.helper import is_response_success, check_json


def uploadExamplesToOrthanc():

    file_list = get_testdata_files("[Mm][Rr][Ii]")
    for file in file_list:
        upload = {'upload_file': open(file, 'rb')}
        status, r = postOrthanc("instances/", upload)
        assert(is_response_success(status, 200))
        assert(check_json(r.json()))

    # Note that this will create several subjects.

def test_getSubjects():
    uploadExamplesToOrthanc()
    reseponse_code, list_subjects = getOrthanc("patients/")
    assert (is_response_success(reseponse_code, 200))

    print(len(list_subjects))


def test_deleteSubjects():
    uploadExamplesToOrthanc()
    reseponse_code, list_subjects = getOrthanc("patients/")
    assert (is_response_success(reseponse_code, 200))

    print(len(list_subjects))

    for subject in list_subjects:
        reseponse_code, r = deleteOrthanc("patients/"+subject)
        assert (is_response_success(reseponse_code, 200))


if __name__ is "__main__":
    test_deleteSubjects()