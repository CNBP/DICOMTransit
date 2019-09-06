from requests import post
from DICOMTransit.redcap import development as environment
from redcap import Project  # note this is from PyCap.redcap
from typing import List


"""
These functions serves as the basis function used to query the variety of table groups in RedCap. It takes care of basic communications etc. 
"""


def createProject(
    Token=environment.REDCAP_TOKEN_CNN_ADMISSION, URL="https://redcap.cnbp.ca/api/"
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


def get_records(project) -> List[dict]:
    """
    Obtain all data from a project
    :param project:
    :return:
    """
    all_data = project.export_records()
    return all_data


def test_Post():
    """
    Very simple test of regular paylaad based approach to communicate with RedCap.
    :return:
    """
    # Two constants we'll use throughout
    TOKEN = environment.REDCAP_TOKEN_CNN_ADMISSION
    URL = "https://redcap.cnbp.ca/api/"

    payload = {"token": TOKEN, "format": "json", "content": "metadata"}

    response = post(URL, data=payload)
    print(response)


def filter_records(
    dataset: List[dict], filter_field: str, list_filtered_value: str or List[str]
):
    """
    Generic filtering method, by checking the list, only retain the relevant CNBPID interested.
    :param list_filtered_value & record ID correspondence list.
    :param CNBPID:
    :return:
    """
    if type(list_filtered_value) == "str":
        list_filtered_value = [list_filtered_value]
    list_filtered = list(
        filter(lambda person: person[filter_field] in list_filtered_value, dataset)
    )
    return list_filtered


def get_recordfields(field_data: str, field_filter: str, filter_value: str):
    """
    An attempt to produce generalized function to get records from RedCap filtering for the fieldvalue from field.
    :param targetted_project:
    :param field_data: the field name fo the data field.
    :param field_filter: the field used to filter the the entire database.
    :param filter_value: the values checked in field_filter used to remove the not needed records.
    :return: field_value: str,
    """
    project_admission = createProject()

    # Will need to return at least these two fields
    list_dict = project_admission.export_records(fields=[field_data, field_filter])
    list_filtered_dict = filter_records(list_dict, field_filter, filter_value)

    # Extract the actual data from the case.
    list_caseID = []
    for case in list_filtered_dict:
        list_caseID.append(case[field_data])
    return list_caseID


g
