from DICOMTransit.redcap.query_common import filter_records, get_fields
from DICOMTransit.redcap import development as environment
from redcap import Project  # note this is from PyCap.redcap
from typing import List

"""
This class of functions are responsible of retrieving relevant data structures from the CNFUN tables
"""


class CNFUN_project:
    """
    One baby can have many admissions CaseIDs.
    One hospital record can have many CaseIDs.
    One baby has only one hospital record number.
    """

    def __init__(
        self,
        Token=environment.REDCAP_TOKEN_CNFUN_PATIENT,
        URL="https://redcap.cnbp.ca/api/",
        get_all_field=False,
    ):
        """
        Create a project using PyCap
        :param Token:
        :param URL:
        :return:
        """
        # Several key properties we'll use throughout
        self.project = Project(URL, Token)
        # These are very important ID fields from the
        fields_keyid = ["patientID", "cf_p_cnnpatientui"]

        # For now, make sure to onyl get the data related to these key ids to reduce load time
        self.data = get_fields(self.project, fields_keyid)

        # if specified, get all the records.
        if get_all_field:
            self.data = self.project.export_records()

    def filter_with_CNNPatientUI(self, CNNPatientUI: str or List[str]):
        """
        Check the list, only retain the relevant records with matching PatientID are retained.
        :param dataset: CNBPIDs & record ID correspondence list.
        :param CNNPatientUI:
        :return:
        """
        list_filtered = None

        filtered_field = "cf_p_cnnpatientui"

        # Handling when babyIDs is string instead of list (allowing batch function).
        if type(CNNPatientUI) is str:
            CNNPatientUI = [CNNPatientUI]

        list_filtered = filter_records(self.data, filtered_field, CNNPatientUI)

        return list_filtered

    def get_PatientID_with_CNNPatientUI(self, CNNPatientUI: str or List[str]):
        """
        PatientID has 1:1 correspondence with CNNPatientUI which is the same as PatientUI from CNN Baby table.
        :return:
        """
        # Listify the CNNPatientUI
        if type(CNNPatientUI) is str:
            CNNPatientUI = [CNNPatientUI]

        # Filter with the information
        list_filtered_dict = self.filter_with_CNNPatientUI(CNNPatientUI)

        # Aggregate the list_PatientID
        list_PatientID = []
        for case in list_filtered_dict:
            list_PatientID.append(case["patientid"])
        return list_PatientID

    def get_records_CNFUN(self, PatientID: str or List[str]):
        """
        Retrieve the cases based on their INDEX which is the
        :param cases:
        :return:
        """
        if type(PatientID) is str:
            PatientID = [PatientID]
        cases_data = self.project.export_records(records=PatientID)
        return cases_data
