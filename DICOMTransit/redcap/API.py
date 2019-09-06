from DICOMTransit.redcap.query_admission import admission_project
from DICOMTransit.redcap.query_baby import baby_project
from DICOMTransit.redcap.query_mother import mother_project
from DICOMTransit.redcap.query_CNFUN import CNFUN_project
from typing import List

"""
Higher level wrapper of query_admission for simple to use API function calls against the admission tables 
"""


class CNNCNFUN_data_retrieval:
    """
    This class attempt to retrieve everything from the RedCap based on the CNBPIDs provided.
    """

    def __init__(self, CNBPID: str or List[str]):
        self.CNBPIDs = CNBPID
        self.admission_project = admission_project()
        self.baby_project = baby_project()
        self.mother_project = mother_project()
        self.CNFUN_project = CNFUN_project()
        self.caseIDs = self.admission_project.get_caseIDwithCNBPID(CNBPID)
        self.babyIDs = self.admission_project.get_babyIDwithCNBPID(CNBPID)
        self.motherIDs = self.baby_project.get_MotherID_with_BabyID(self.babyIDs)
        self.CNNPatientUIs = self.baby_project.get_PatientUI_with_BabyID(self.babyIDs)
        self.PatientIDs = self.CNFUN_project.get_PatientID_with_CNNPatientUI(
            self.CNNPatientUIs
        )

    def get_admission_data(self):
        """
        Use the list of CNBPIDs to obtain the necessary admission data
        :param CNBPID:
        :return:
        """
        list_case_data = self.admission_project.get_records_admission(self.caseIDs)
        return list_case_data

    def get_baby_data(self):
        """
        Use the list of CNBPIDs to obtain the necessary admission data
        :param CNBPID:
        :return:
        """
        list_case_data = self.baby_project.get_records_baby(self.babyIDs)
        return list_case_data

    def get_mother_data(self):
        """
        Use the list of CNBPIDs to obtain the necessary admission data
        :param CNBPID:
        :return:
        """
        list_case_data = self.mother_project.get_records_mother(self.babyIDs)
        return list_case_data

    def get_CNFUN_data(self):
        list_case_data = self.CNFUN_project.get_records_CNFUN(self.PatientIDs)
        return list_case_data
