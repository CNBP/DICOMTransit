# ----------------------------------------------------------------------------------------------------------------------
#  Imports
# ----------------------------------------------------------------------------------------------------------------------

# Note: You may use the development or the production constants simply by commenting out
#       one of the two lines below.
from DICOMTransit.settings import config_get

# from redcap import production as environment


# ----------------------------------------------------------------------------------------------------------------------
#  Constants
# ----------------------------------------------------------------------------------------------------------------------

cnn_connection_string = config_get("CNN_CONNECTION_STRING")
cnfun_connection_string = config_get("CNFUN_CONNECTION_STRING")

redcap_export_enabled = config_get("REDCAP_EXPORT_ENABLED")
redcap_api_url = config_get("REDCAP_API_URL")

redcap_record_id_field_name_cnn_admission = "caseid"
redcap_record_id_field_name_cnn_baby = "babyid"
redcap_record_id_field_name_cnn_mother = "motherid"
redcap_record_id_field_name_cnn_master = "masterid"
redcap_record_id_field_name_cnfun_patient = "patientid"

redcap_token_cnn_admission = config_get("REDCAP_TOKEN_CNN_ADMISSION")
redcap_token_cnn_baby = config_get("REDCAP_TOKEN_CNN_BABY")
redcap_token_cnn_mother = config_get("REDCAP_TOKEN_CNN_MOTHER")
redcap_token_cnn_master = config_get("REDCAP_TOKEN_CNN_MASTER")
redcap_token_cnfun_patient = config_get("REDCAP_TOKEN_CNFUN_PATIENT")
redcap_repeat_instrument_key_name = "redcap_repeat_instrument"
redcap_repeat_instance_key_name = "redcap_repeat_instance"
redcap_complete_status_suffix = "_complete"
redcap_complete_status_value = 2
redcap_form_holding_ids_directly_linked_to_hospital_record_numbers = "admission"
redcap_fields_to_ignore_process_field_warnings = ["masterid", "cnbpid"]

mysql_export_enabled = config_get("MYSQL_EXPORT_ENABLED")
mysql_export_host = config_get("MYSQL_EXPORT_HOST")
mysql_export_port = config_get("MYSQL_EXPORT_PORT")
mysql_export_database = config_get("MYSQL_EXPORT_DATABASE")
mysql_export_user = config_get("MYSQL_EXPORT_USER")
mysql_export_password = config_get("MYSQL_EXPORT_PASSWORD")

# Column indexes used in the import configuration table.
# -> See initialization.py initialize_import_configuration function
IMPORT_SEQUENCE = 0
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
