from redcap.enums import Field


class RedcapTransaction:
    """
    This is an abstract class that contain all the information necessary to complete a transaction with RedCAP system to update it.
    """

    data_import_configuration = []
    redcap_metadata = []
    redcap_fields = {}
    database_column_names = {}
    hospital_record_numbers = []
    redcap_queue = []


    # Case specific temporary variable.
    HospitalRecordNumber = -1
    CaseId = -1
    BabyId = -1
    MotherId = -1
    PatientUI = -1
    CNNPatientUI = -1
    PatientId = -1
    MasterId = -1

    def initialize_ids(self, index_hospital_record_number):
        """
        Sets the hospital record number and reset all ids related to this hospital record number.
        :param index_hospital_record_number: Hospital Record Number
        :return: None
        """
        self.HospitalRecordNumber = self.hospital_record_numbers[index_hospital_record_number]
        self.CaseId = -1
        self.BabyId = -1
        self.MotherId = -1
        self.PatientUI = -1
        self.CNNPatientUI = -1
        self.PatientId = -1
        self.MasterId = -1

    def add_redcap_queue(self, record_text, project):
        """
        Adds a record to the list of records to send to REDCap.
        :param record_text: Record data
        :param project: Project Configuration Number where this record belongs
        :return: None
        """
        self.redcap_queue.append([record_text, project])

    def clear_redcap_queue(self):
        """
        Erase all records in the queue.
        :return: None
        """
        self.redcap_queue = []


    def get_primary_key_value(self, primary_key):
        """
        Get Primary Key Value
        :param primary_key: Primary Key Configuration Number
        :return: Primary Key Value
        """
        if primary_key == Field.BabyId.value:
            return self.BabyId
        elif primary_key == Field.CaseId.value:
            return self.CaseId
        elif primary_key == Field.CNNPatientUI.value:
            return self.CNNPatientUI
        elif primary_key == Field.HospitalRecordNumber.value:
            return self.HospitalRecordNumber
        elif primary_key == Field.MotherId.value:
            return self.MotherId
        elif primary_key == Field.PatientId.value:
            return self.PatientId
        elif primary_key == Field.PatientUI.value:
            return self.PatientUI
        elif primary_key == Field.MasterId.value:
            return self.MasterId
        else:
            return -1
