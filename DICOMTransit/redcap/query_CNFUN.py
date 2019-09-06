from DICOMTransit.redcap.query_common import (
    filter_records,
    get_recordfields,
)
from DICOMTransit.redcap import development as environment
from redcap import Project  # note this is from PyCap.redcap
'''
This class of functions are responsible of retrieving relevant data structures from the CNFUN tables
'''

def createCNFUNProject(
    Token=environment.REDCAP_TOKEN_CNFUN_PATIENT, URL="https://redcap.cnbp.ca/api/"
):
    """
    Create a project using PyCap
    :param Token:
    :param URL:
    :return:
    """

    # Two constants we'll use throughout
    project_admission = Project(URL, Token)
    return project_admission

def get_CNFUNPatientID_with_PatientUI(PatientUI: int):



def get_record_CNFUN(PatientUI: int):
