from DICOMTransit.redcap.query_common import (
    filter_records,
    get_recordfields,
)
from DICOMTransit.redcap import development as environment
from redcap import Project  # note this is from PyCap.redcap
'''
These functions are used to retrieve the data from the MOTHERS table clusters.
'''

def createMotherProject(
    Token=environment.REDCAP_TOKEN_CNN_MOTHER, URL="https://redcap.cnbp.ca/api/"
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

def get_record_mother(MotherID: int)