import os
import unittest
from LORIS.helper import LORIS_helper
from dotenv import load_dotenv
from pathlib import Path

class UT_LORISHelper(unittest.TestCase):

    @staticmethod
    def test_number_extraction():
        Prefix = "V"
        numbers = [1, 2, 3, 9, 10, 11, 12, 100, 101, 102]

        timepoints = []

        for number in numbers:
            timepoints.append(Prefix + str(number))

        DualList = zip(numbers, timepoints)

        for tupleItem in DualList:
            assert str(tupleItem[0]) == LORIS_helper.number_extraction(tupleItem[1])[0]


    @staticmethod
    def test_ProxyUpload():
        assert load_dotenv()

        ProxyIP = os.getenv("ProxyIP")
        ProxyUsername = os.getenv("ProxyUsername")
        ProxyPassword = os.getenv("ProxyPassword")
        LORISHostPassword = os.getenv("LORISHostPassword")
        LORISHostUsername = os.getenv("LORISHostUsername")
        LORISHostIP = os.getenv("LORISHostIP")
        Client = LORIS_helper.getProxySSHClient(ProxyIP, ProxyUsername, ProxyPassword,
                                                LORISHostIP, LORISHostUsername, LORISHostPassword)

        testFile = "test_file.txt"
        Path(testFile).touch()

        LORIS_helper.uploadThroughClient(Client, testFile, testFile)
        sftp = Client.open_sftp()
        sftp.remove(testFile)
        os.remove(testFile)
        sftp.close()
        Client.close()

if __name__ == '__main__':
    UT_LORISHelper.test_number_extraction()