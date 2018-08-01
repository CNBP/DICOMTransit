import sys
import os

print(sys.executable)
print(sys.path)

# Get current path:
pwd = os.path.dirname(os.path.abspath(__file__))
print(pwd)

script_root = os.path.dirname(pwd)
print(script_root)
sys.path.append(script_root)
print(sys.path)
print("OKAY")

from DICOM.test_DICOM import test_DICOM_validator, test_DICOM_RequireDecompression, test_DICOM_anonymizer, test_DICOM_retrieveMRN, test_DICOM_update, test_DICOM_computerScanAge
test_DICOM_validator()
test_DICOM_RequireDecompression()
test_DICOM_anonymizer()
test_DICOM_retrieveMRN()
test_DICOM_update()
test_DICOM_computerScanAge()

from Integration.test_Integration import test_updateLocalTimepoint
test_updateLocalTimepoint()

from LocalDB.test_LocalDBCreate import test_LocalDBCreate, test_LocalDBCreate_CNBP
test_LocalDBCreate()
test_LocalDBCreate_CNBP()

from LocalDB.test_LocalDBQuery import test_CheckSubjectExist, test_CreateSubject, test_CreateSubjectCheckExist, test_SubjectUpdate
test_CheckSubjectExist()
test_CreateSubject()
test_CreateSubjectCheckExist()
test_SubjectUpdate()

from LORIS.test_LORIS_helper import test_number_extraction
test_number_extraction()

from LORIS.test_LORIS_Query import test_checkPSCIDExist, test_checkDCCIDExist, test_LORIS_get, test_LORIS_login
test_checkPSCIDExist()
test_checkDCCIDExist()
test_LORIS_get()
test_LORIS_login()

from LORIS.test_LORIS_timepoint import test_visit_number_extraction
test_visit_number_extraction()

from orthanc.test_orthanc import test_getSubjects, test_deleteSubjects
test_getSubjects()
test_deleteSubjects()

from oshelper.test_file_ops import test_recursive_load, test_copy_files_to_flat_folder
test_recursive_load()
test_copy_files_to_flat_folder()
