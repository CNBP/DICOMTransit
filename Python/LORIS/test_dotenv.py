from dotenv import load_dotenv
import unittest
import os

class UT_envCheck(unittest.testcases):

    def test_env():
        success= load_dotenv()
        if not success:
            raise ImportError("Credential .env NOT FOUND! Please ensure .env is set with all the necessary credentials!")


        assert os.getenv("LORISurl") is not None
        assert os.getenv("LORISusername") is not None
        assert os.getenv("LORISpassword") is not None

        assert os.getenv("timepoint_prefix") is not None
        assert os.getenv("projectID_dictionary") is not None
        assert os.getenv("LocalDatabase") is not None

        assert os.getenv("OrthancURL") is not None

        assert os.getenv("ProxyIP") is not None
        assert os.getenv("ProxyUsername") is not None
        assert os.getenv("ProxyPassword") is not None

        assert os.getenv("LORISHostPassword") is not None
        assert os.getenv("LORISHostUsername") is not None
        assert os.getenv("LORISHostIP") is not None

        assert os.getenv("DeletionScript") is not None
