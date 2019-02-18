import unittest
from Integration.fsm import DICOMTransitImport
class UT_FSM(unittest.TestCase):

    # Instantiate transaction object
    test_import = DICOMTransitImport()

    def test_CheckLORIS(self):
        self.test_import.UpdateLORISStatus()
        self.test_import.is_LORIS_Unavailable()

    def test_CheckNetwork(self):
        self.test_import.UpdateNetworkStatus()
        self.test_import.is_Network_Unavailable()

    def test_CheckLocalDB(self):
        self.test_import.UpdateLocalDBStatus()
        self.test_import.is_LocalDB_Unavailable()

    def test_CheckFile(self):
        raise NotImplementedError


    def test_CheckOrthanc(self):
        self.test_import.UpdateOrthancStatus()
        self.test_import.is_Orthanc_Unavailable()

