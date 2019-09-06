from DICOMTransit.redcap.query_admission import admission_project
from typing import List

"""
Higher level wrapper of query_admission for simple to use API function calls against the admission tables 
"""


def get_admission_data(CNBPID: List[int]):
    """
    Use the list of CNBPID to obtain the necessary admission data
    :param CNBPID:
    :return:
    """
    project = admission_project()
    list_caseID = project.get_caseIDwithCNBPID(CNBPID)
    list_case_data = project.get_records_admission(list_caseID)
    return list_case_data
