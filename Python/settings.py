from PythonUtils.env import validate_dotenv_var


"""
This class has no set because that is done via the frontend configurator. Setting should be only updated on the frontend.
Alternatively, the database can be manually edited on the backend but they are NEVER modified by the DICOMTransit itself.
"""

def config_get(variable_name):
    """
    Validate to see if the variable exist, before loading it into the environment from the database.
    :param variable_name:
    :param possible_variables:
    :return:
    """
    from LocalDB.schema import CNBP_blueprint
    from LocalDB.API import get_setting

    # Check if variable is an anticipated variable.
    if validate_dotenv_var(variable_name, CNBP_blueprint.dotenv_variables):

        # Use local databse API to load the variable.
        env_variable = get_setting(variable_name)

        return env_variable

    else:
        raise ValueError(
            f"The variable name provided: {variable_name} is NOT a sanctioned variable as defined by the schema")

