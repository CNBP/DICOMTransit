# ----------------------------------------------------------------------------------------------------------------------
#  Imports
# ----------------------------------------------------------------------------------------------------------------------

from redcap.enums import Field


# ----------------------------------------------------------------------------------------------------------------------
#  RedcapTransaction
# ----------------------------------------------------------------------------------------------------------------------

class RedcapTransaction:

    data_import_configuration = []
    redcap_metadata = []
    redcap_fields = {}
    database_column_names = {}
    hospital_record_numbers = []
    redcap_queue = []

    # Temporary Ids.
    HospitalRecordNumber = -1
    CaseId = -1
    BabyId = -1
    MotherId = -1
    PatientUI = -1
    CNNPatientUI = -1
    PatientId = -1
    MasterId = -1

    def set_hospital_record_number(self, index_hospital_record_number) -> None:
        """
        Sets the hospital record number and resets all other temporary ids.
        :param index_hospital_record_number: Index of Hospital Record Number
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

    def set_case_id(self, case_id) -> None:
        """
        Sets the case id and resets all temporary ids related to a case.
        :return: None
        """
        self.CaseId = case_id
        self.BabyId = -1
        self.MotherId = -1
        self.PatientUI = -1
        self.CNNPatientUI = -1
        self.PatientId = -1
        self.MasterId = -1

    def add_redcap_queue(self, record_text, project) -> None:
        """
        Adds a record to the list of records to send to REDCap.
        :param record_text: Record data
        :param project: Project Configuration Number where this record belongs
        :return: None
        """
        self.redcap_queue.append([record_text, project])

    def get_primary_key_value(self, primary_key) -> int:
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
