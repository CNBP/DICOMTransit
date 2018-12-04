import os
import unittest
from pathlib import Path

from LORIS.helper import LORIS_helper
from LocalDB.schema import CNBP_blueprint
from PythonUtils.env import load_validate_dotenv


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


        ProxyIP = load_validate_dotenv("ProxyIP", CNBP_blueprint.dotenv_variables)
        ProxyUsername = load_validate_dotenv("ProxyUsername", CNBP_blueprint.dotenv_variables)
        ProxyPassword = load_validate_dotenv("ProxyPassword", CNBP_blueprint.dotenv_variables)
        LORISHostPassword = load_validate_dotenv("LORISHostPassword", CNBP_blueprint.dotenv_variables)
        LORISHostUsername = load_validate_dotenv("LORISHostUsername", CNBP_blueprint.dotenv_variables)
        LORISHostIP = load_validate_dotenv("LORISHostIP", CNBP_blueprint.dotenv_variables)
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