import unittest
import os
from DICOMTransit.Integration.fsm import DICOMTransitImport


class UT_FSM(unittest.TestCase):

    # Instantiate transaction object
    test_import = DICOMTransitImport()

    def test_CheckLORIS(self):
        self.test_import.UpdateLORISStatus()
        assert not self.test_import.is_LORIS_Unavailable()

    def test_CheckNetwork(self):
        self.test_import.UpdateNetworkStatus()
        assert not self.test_import.is_Network_Unavailable()

    def test_CheckLocalDB(self):
        self.test_import.UpdateLocalDBStatus()
        assert not self.test_import.is_LocalDB_Unavailable()

    def test_CheckFile(self):
        self.test_import.files = [os.path.abspath(__file__)]
        self.test_import.UpdateFileStatus()
        assert self.test_import.STATUS_FILE is True

    def test_CheckOrthanc(self):
        self.test_import.UpdateOrthancStatus()
        assert not self.test_import.is_Orthanc_Unavailable()
