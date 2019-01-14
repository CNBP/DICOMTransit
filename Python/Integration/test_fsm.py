import unittest
from Integration.fsm import DICOMTransitImport
class UT_FSM(unittest.TestCase):

    # Instantiate transaction object
    test_import = DICOMTransitImport("Test")

    def test_CheckLORIS(self):
        self.test_import.CheckLORIS()

    def test_CheckNetwork(self):
        self.test_import.CheckNetwork()

    def test_CheckLocalDB(self):
        self.test_import.CheckLocalDB()

    def test_CheckFile(self):
        self.test_CheckLORIS()

    def test_CheckOrthanc(self):
        self.test_import.CheckOrthanc()

