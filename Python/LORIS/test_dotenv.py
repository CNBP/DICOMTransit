import unittest
from settings import config_get
from LocalDB.schema import CNBP_blueprint
from dotenv import load_dotenv
import os

class UT_envCheck(unittest.TestCase):

    def test_env_basic(self):
        load_dotenv()
        variable_a = os.getenv("Variable_A")
        print(variable_a)


    def test_env(self):
        """
        This unit test ensures that the variables in .env is the same as the ones specified in the blueprint of the schema
        :return:
        """
        # Load the list of predefined variables as defined in the schema.
        list_variables = CNBP_blueprint.dotenv_variables

        # loop through each one and then attempt to load and validate them.
        for variable in list_variables:
            assert config_get(variable) is not None
