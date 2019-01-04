from redcap import development as environment
# ----------------------------------------------------------------------------------------------------------------------
#  Constants
# ----------------------------------------------------------------------------------------------------------------------
# Setting index in the table_configuration, see initialization.py initialize_data_import_configuration_matrix function
IS_IMPORT_ENABLED = 1
IS_REFERENCE_TABLE = 2
REDCAP_PROJECT = 3
DATABASE_TABLE_NAME = 4
DATABASE = 5
PRIMARY_KEY_NAME = 6
PRIMARY_KEY_VALUE = 7
AUTHORITY_ON_IDS = 8
IS_REPEATABLE_INSTRUMENT = 9
REDCAP_FORM_NAME = 10

redcap_api_url = environment.REDCAP_API_URL
redcap_token_cnn_admission = environment.REDCAP_TOKEN_CNN_ADMISSION
redcap_token_cnn_baby = environment.REDCAP_TOKEN_CNN_BABY
redcap_token_cnn_mother = environment.REDCAP_TOKEN_CNN_MOTHER
redcap_token_cnn_master = environment.REDCAP_TOKEN_CNN_MASTER
redcap_token_cnfun_patient = environment.REDCAP_TOKEN_CNFUN_PATIENT
redcap_repeat_instrument_key_name = "redcap_repeat_instrument"
redcap_repeat_instance_key_name = "redcap_repeat_instance"
redcap_complete_status_suffix = "_complete"
redcap_complete_status_value = 2
cnn_connection_string = environment.CNN_CONNECTION_STRING
cnfun_connection_string = environment.CNFUN_CONNECTION_STRING