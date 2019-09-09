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
    Upon initialization, it will then get any information based on needed.
    """

    def __init__(self, CNBPID: str or List[str]):

        # Initialize the CNBPID and then create the respective projects using default credentials (without retrieving bulk of the data)
        self.CNBPIDs = CNBPID
        self.admission_project = admission_project()
        self.baby_project = baby_project()
        self.mother_project = mother_project()
        self.CNFUN_project = CNFUN_project()

        # Use CNBPID to retrieve the other two key IDs.
        self.caseIDs = self.admission_project.get_caseIDwithCNBPID(CNBPID)
        self.babyIDs = self.admission_project.get_babyIDwithCNBPID(CNBPID)

        # Use the babyIDs to help retrieve the two other IDs.
        self.motherIDs = self.baby_project.get_MotherID_with_BabyID(self.babyIDs)
        self.CNNPatientUIs = self.baby_project.get_PatientUI_with_BabyID(self.babyIDs)

        # Finally, use CNNPatientUI to get PatientIDs
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
        list_case_data = self.mother_project.get_records_mother(self.motherIDs)
        return list_case_data

    def get_CNFUN_data(self):
        list_case_data = self.CNFUN_project.get_records_CNFUN(self.PatientIDs)
        return list_case_data


def test_CNNCNFUN_data_retrieval():
    retrieval = CNNCNFUN_data_retrieval("VXS0000007")
    a = retrieval.get_admission_data()
    assert len(a) > 0
    b = retrieval.get_baby_data()
    assert len(b) > 0
    c = retrieval.get_CNFUN_data()
    # note that currently, CNFUN has mostly empty data because... babies are not old enough to have follow up data about.
    d = retrieval.get_mother_data()
    assert len(d) > 0
    print("Completed")
