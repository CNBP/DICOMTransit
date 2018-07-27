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

from tests.test_Intermediate_Server import test_updateLocalTimepoint
test_updateLocalTimepoint()

from tests.test_LocalDBCreate import test_LocalDBCreate, test_LocalDBCreate_CNBP
test_LocalDBCreate()
test_LocalDBCreate_CNBP()

from tests.test_LORIS_Query import test_checkPSCIDExist, test_checkDCCIDExist, test_LORIS_get, test_LORIS_login
test_checkPSCIDExist()
test_checkDCCIDExist()
test_LORIS_get()
test_LORIS_login()

from tests.test_LocalDBQuery import test_CheckSubjectExist, test_CreateSubject, test_CreateSubjectCheckExist, test_SubjectUpdate
test_CheckSubjectExist()
test_CreateSubject()
test_CreateSubjectCheckExist()
test_SubjectUpdate()

from tests.test_file_ops import *
test_recursive_load()
test_copy_files_to_flat_folder()

from tests.test_DICOM import *

test_DICOM_validator()
test_DICOM_RequireDecompression()
test_DICOM_anonymizer()
test_DICOM_retrieveMRN()
test_DICOM_update()
test_DICOM_computerScanAge()

from tests.test_LORIS_timepoint import *
test_visit_number_extraction()

from tests.test_LORIS_helper import *
test_number_extraction()