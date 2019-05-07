import unittest
import logging
from LORIS.API import check_online_status, check_status, get_all_timepoints, get_allUID, upload_visit_DICOM, new_trigger_insertion


logger = logging.getLogger()

class UT_LORISAPI(unittest.TestCase):

    def test_CheckLORISStatus(self):
        return check_online_status()


    def test_CheckNetworkStatus(self):
        return check_status()


    def test_GetTimePoint(self):
        return get_all_timepoints(471400)


    def test_GetAllVisitDICOMs(self):
        return get_allUID(471400)

    def test_upload_visit_DICOM(self):
        upload_visit_DICOM(r"C:\Users\Yang Ding\Desktop\VXS0000057_229523_V1.zip", 229523, "V1", False)

    def test_trigger_insertion(self):
        new_trigger_insertion(229523, "V1", "VXS0000057_229523_V1.zip", 59)
