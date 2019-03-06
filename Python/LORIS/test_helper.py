import os
import unittest
from pathlib import Path

from LORIS.helper import LORIS_helper
from LocalDB.schema import CNBP_blueprint
from settings import config_get


class UT_LORISHelper(unittest.TestCase):

    def test_number_extraction(self):
        Prefix = "V"
        numbers = [1, 2, 3, 9, 10, 11, 12, 100, 101, 102]

        timepoints = []

        for number in numbers:
            timepoints.append(Prefix + str(number))

        DualList = zip(numbers, timepoints)

        for tupleItem in DualList:
            assert str(tupleItem[0]) == LORIS_helper.number_extraction(tupleItem[1])[0]


    # Obsolete.

    """
    def test_ProxyUpload(self):


        ProxyIP = config_get("ProxyIP")
        ProxyUsername = config_get("ProxyUsername")
        ProxyPassword = config_get("ProxyPassword")
        LORISHostPassword = config_get("LORISHostPassword")
        LORISHostUsername = config_get("LORISHostUsername")
        LORISHostIP = config_get("LORISHostIP")
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
    """