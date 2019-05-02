import unittest
import orthanc.API
import pytest
import urllib.parse

from PythonUtils.env import is_travis

if is_travis():
    pytest.skip(
        "Skipping test requiring private database access", allow_module_level=True
    )


class UT_ProdOrthanc(unittest.TestCase):

    # MUST ensure TravisCI LORIS also deploy with the proper setting with regard to the ORTHANC authentication.
    # This attempts to access the production Orthanc from the local environment and then check if upupload and download work.

    url, user, password = orthanc.API.get_prod_orthanc_credentials()

    def test_getSubjects(self):
        subject_list = orthanc.API.get_list_of_studies(
            self.url, self.user, self.password
        )
        assert len(subject_list) > 0
        return subject_list

    def test_getSubjectZip(self):
        list_subjects = self.test_getSubjects()
        patients_url = urllib.parse.urljoin(UT_ProdOrthanc.url, "patients/")
        for subject in list_subjects:
            patient_url = urllib.parse.urljoin(patients_url, f"{subject}/")
            patient_archive_url = urllib.parse.urljoin(patient_url, "archive")
            orthanc.API.get_subject_zip(
                patient_archive_url, UT_ProdOrthanc.user, UT_ProdOrthanc.password
            )


if __name__ == "__main__":
    UT_ProdOrthanc.test_getSubjectZip()
