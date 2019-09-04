import unittest
import DICOMTransit.orthanc.API
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

    credential = DICOMTransit.orthanc.API.get_prod_orthanc_credentials()

    def test_getSubjects(self):
        list_StudyUIDs = DICOMTransit.orthanc.API.get_all_subject_StudyUIDs(
            self.credential
        )
        if len(list_StudyUIDs) == 0:
            return []
        assert len(list_StudyUIDs) > 0
        return list_StudyUIDs

    def test_getSubjectZip(self):
        list_StudyUIDs = self.test_getSubjects()
        if len(list_StudyUIDs) == 0:
            return
        patients_url = urllib.parse.urljoin(self.credential.url, "patients/")
        for subject in list_StudyUIDs:
            patient_url = urllib.parse.urljoin(patients_url, f"{subject}/")
            patient_archive_url = urllib.parse.urljoin(patient_url, "archive")
            DICOMTransit.orthanc.API.get_StudyUID_zip(
                patient_archive_url, self.credential
            )


if __name__ == "__main__":
    UT_ProdOrthanc.test_getSubjectZip()
