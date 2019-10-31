
#############################
# State Naming Variables:
#############################

# Exists purely to ensure IDE can help mis spellings vs strings, which IDE DO NOT CHECK
ST_waiting = "ST_waiting"
ST_determined_orthanc_new_data_status = "ST_determined_orthanc_new_data_status"
ST_determined_orthanc_StudyUID_status = "ST_determined_orthanc_StudyUID_status"
ST_detected_new_data = "ST_detected_new_data"
ST_confirmed_new_data = "ST_confirmed_new_data"
ST_obtained_new_data = "ST_obtained_new_data"
ST_unpacked_new_data = "ST_unpacked_new_data"

# Old subject states
ST_obtained_MRN = "ST_obtained_MRN"
ST_determined_MRN_status = "ST_determined_MRN_status"
ST_processing_old_patient = "ST_processing_old_patient"
ST_processing_new_patient = "ST_processing_new_patient"
ST_found_insertion_status = "ST_found_insertion_status"
ST_ensured_only_new_subjects_remain = "ST_ensured_only_new_subjects_remain"
ST_obtained_DCCID_CNBPID = "ST_obtained_DCCID_CNBPID"
ST_crosschecked_seriesUID = "ST_crosschecked_seriesUID"
ST_updated_remote_timepoint = "ST_updated_remote_timepoint"

# New subject states
ST_obtained_new_subject_gender = "ST_obtained_new_subject_gender"
ST_obtained_new_subject_birthday = "ST_obtained_new_subject_birthday"
ST_created_remote_subject = "ST_created_remote_subject"
ST_harmonized_timepoints = "ST_harmonized_timepoints"

# Files states
ST_files_anonymized = "ST_files_anonymized"
ST_files_zipped = "ST_files_zipped"
ST_zip_uploaded = "ST_zip_uploaded"
ST_zip_inserted = "ST_zip_inserted"
ST_insertion_recorded = "ST_insertion_recorded"

# Error handling states.
ST_retry = "ST_retry"
ST_error_orthanc = "ST_error_orthanc"
ST_error_LORIS = "ST_error_LORIS"
ST_error_localDB = "ST_error_localDB"
ST_error_file_corruption = "ST_error_file_corruption"
ST_error_sqlite = "ST_error_sqlite"
ST_error_network = "ST_error_network"
ST_human_intervention_required = "ST_human_intervention_required"
