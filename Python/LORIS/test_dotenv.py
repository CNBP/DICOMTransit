import unittest
from PythonUtils.env import load_validate_dotenv
from LocalDB.schema import CNBP_blueprint

class UT_envCheck(unittest.TestCase):

    @staticmethod
    def test_env():

        # Load the list of predefined variables as defined in the schema.
        list_variables = CNBP_blueprint.dotenv_variables

        # loop through each one and then attempt to load and validate them.
        for variable in list_variables:
            assert load_validate_dotenv(variable, CNBP_blueprint.dotenv_variables) is not None