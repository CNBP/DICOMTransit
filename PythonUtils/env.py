from dotenv import load_dotenv
import os


def is_travis():
    """
    Detect if current environment is travis. Mainly used to disable underiable unit tests which cannot run on Travis (i.e. private database access)
    :return:
    """
    is_travis_in_OS_env = "TRAVIS" in os.environ
    return is_travis_in_OS_env


def validate_dotenv_var(variable_name: str, possible_variables: list):
    """
    Validate to see if the variable is in the list of the valid variable provided.
    :param variable_name:
    :param possible_variables:
    :return:
    """
    if variable_name in possible_variables:
        return True
    else:
        return False


def load_dotenv_var(variable_name: str):
    """
    A wrapper for the load_DotENV function from the DICOMTransit .Env framework
    :param variable_name:
    :return:
    """

    success = load_dotenv()
    if not success:
        raise ImportError(
            "Credential .env NOT FOUND! Please ensure .env is set with all the necessary credentials!"
        )
    return os.getenv(variable_name)


def load_validate_dotenv(variable_name: str, possible_variables: list):
    """
    Validate to see if the file exist, before loading it into the enviroment.
    :param variable_name:
    :param possible_variables:
    :return:
    """
    if validate_dotenv_var(variable_name, possible_variables):
        env_variable = load_dotenv_var(variable_name)
        return env_variable
    else:
        raise ValueError(
            f"The variable name provided: {variable_name } is NOT a sanctioned variable as defined by the schema"
        )
