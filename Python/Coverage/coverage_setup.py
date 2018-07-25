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

from test_Intermediate_Server import test_updateLocalTimepoint
from test_LocalDBCreate import test_LocalDBCreate, test_LocalDBCreate_CNBP
from test_LocalDBQuery import test_CheckSubjectExist, test_CreateSubject, test_CreateSubjectCheckExist, test_SubjectUpdate
from test_LORIS_Query import test_checkPSCIDExist, test_checkDCCIDExist, test_LORIS_get, test_LORIS_login

test_updateLocalTimepoint()
test_LocalDBCreate()
test_LocalDBCreate_CNBP()
test_CheckSubjectExist()
test_CreateSubject()
test_CreateSubjectCheckExist()
test_SubjectUpdate()
test_checkPSCIDExist()
test_checkDCCIDExist()
test_LORIS_get()
test_LORIS_login()
