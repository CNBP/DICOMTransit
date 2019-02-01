
import unittest
import sys
import logging
from LORIS.API import check_online_status, check_status, get_all_timepoints, get_allUID, upload_visit_DICOM, new_trigger_insertion


logger = logging.getLogger()

class UT_LORISAPI(unittest.TestCase):

    def test_CheckLORISStatus(self):
        return check_online_status()


    def test_CheckNetworkStatus(self):
        return check_status()


    def test_GetTimePoint(self):
        return get_all_timepoints(605638)


    def test_GetAllVisitDICOMs(self):
        return get_allUID(605638)

    def test_upload_visit_DICOM(self):
        upload_visit_DICOM(r"C:\Users\Yang Ding\Desktop\CNBP0020001_605638_V1.zip", 605638, "V1", False)

    def test_trigger_insertion(self):
        new_trigger_insertion(605638, "V1", "CNBP0020001_605638_V1.zip", 102)