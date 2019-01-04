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

redcap_api_url = environment.redcap_api_url
redcap_token_cnn_admission = environment.redcap_token_cnn_admission
redcap_token_cnn_baby = environment.redcap_token_cnn_baby
redcap_token_cnn_mother = environment.redcap_token_cnn_mother
redcap_token_cnn_master = environment.redcap_token_cnn_master
redcap_token_cnfun_patient = environment.redcap_token_cnfun_patient
redcap_repeat_instrument_key_name = "redcap_repeat_instrument"
redcap_repeat_instance_key_name = "redcap_repeat_instance"
redcap_complete_status_suffix = "_complete"
redcap_complete_status_value = 2
cnn_connection_string = environment.cnn_connection_string
cnfun_connection_string = environment.cnfun_connection_string