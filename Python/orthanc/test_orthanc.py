import os
from pydicom.data import get_testdata_files

from orthanc.query import orthanc_query

from LORIS.helper import LORIS_helper


def uploadExamplesToOrthanc():
    file_list = get_testdata_files("[Ss][Mm][Aa][Ll][Ll]")
    for file in file_list:
        print(file)
        upload = {'upload_file': open(file, 'rb')}
        status, r = orthanc_query.postOrthanc("instances/", upload)
        assert(LORIS_helper.is_response_success(status, 200))
        assert(r.json())

    # Note that this will database several subjects.

def test_getSubjects():
    uploadExamplesToOrthanc()
    reseponse_code, list_subjects = orthanc_query.getOrthanc("patients/")
    assert (LORIS_helper.is_response_success(reseponse_code, 200))
    return list_subjects


def test_deleteSubjects():
    list_subjects = test_getSubjects()
    for subject in list_subjects:
        reseponse_code, r = orthanc_query.deleteOrthanc("patients/"+subject)
        assert (LORIS_helper.is_response_success(reseponse_code, 200))


def test_getSubjectZip():
    list_subjects = test_getSubjects()
    for subject in list_subjects:
        status, zip_file = orthanc_query.getPatientZipOrthanc(subject)
        assert(LORIS_helper.is_response_success(status, 200))
        assert(os.path.exists(zip_file))
        os.mkdir("temp")
        temp_dir = os.path.join(os.getcwd(), "temp")
        orthanc_query.flatUnZip(zip_file, temp_dir)
        os.remove(zip_file)
        import shutil
        shutil.rmtree(temp_dir)

if __name__ == "__main__":
    test_getSubjectZip()
