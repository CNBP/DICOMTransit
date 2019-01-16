import unittest
from settings import get
from LocalDB.schema import CNBP_blueprint
from dotenv import load_dotenv
import os

class UT_envCheck(unittest.TestCase):

    @staticmethod
    def test_env_basic():
        load_dotenv()
        variable_a = os.getenv("Variable_A")
        print(variable_a)

    @staticmethod
    def test_env():
        """
        This unit test ensures that the variables in .env is the same as the ones specified in the blueprint of the schema
        :return:
        """
        # Load the list of predefined variables as defined in the schema.
        list_variables = CNBP_blueprint.dotenv_variables

        # loop through each one and then attempt to load and validate them.
        for variable in list_variables:
            assert get(variable) is not None


if __name__ == "__main__":
    UT_envCheck.test_env_basic()