
import unittest
import sys
import logging
from LORIS.API import check_online_status, check_status, get_all_timepoints, get_allUID, get_allUID

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logger = logging.getLogger(__name__)

class UT_LORISAPI(unittest.TestCase):

    def test_CheckLORISStatus(self):
        return check_online_status()


    def test_CheckNetworkStatus(self):
        return check_status()


    def test_GetTimePoint(self):
        return get_all_timepoints(605638)

    def test_GetAllVisitDICOMs(self):
        return get_allUID(605638)