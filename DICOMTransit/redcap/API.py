from DICOMTransit.redcap.query_pycap import (
    filter_records,
    get_recordfields,
    createProject,
)
from DICOMTransit.redcap import development as environment
from redcap import Project  # note this is from PyCap.redcap
from typing import List


def get_caseIDwithCNBPID(dataset: List[dict], CNBPID: str or List[str]):
    """
    Get a list of CaseD using data provided list of CNBPID.
    :param dataset: the indexing list of dictionary showing correspondence
    :param list_CNBPID:
    :return:
    """
    list_filtered_dict = filter_basedon_CNBPID(dataset, CNBPID)
    list_caseID = []
    for case in list_filtered_dict:
        list_caseID.append(case["caseid"])
    return list_caseID


def filter_basedon_CNBPID(dataset: list, CNBPID: str or List[str]):
    """
    Check the list, only retain the relevant CNBPID interested.
    :param dataset: CNBPID & record ID correspondence list.
    :param CNBPID:
    :return:
    """
    list_filtered = None
    cnbpid = []
    filtered_field = "cnbpid"
    # Hnadling when CNBPID is string instead of list (allowing batch function).
    if type(CNBPID) == "str":
        cnbpid = [CNBPID]
    elif type(CNBPID) == "list":
        list_filtered = filter_records(dataset, filtered_field, cnbpid)
    return list_filtered


def get_babyIDwithCNBPID(dataset: List[dict], CNBPID: str or List[str]):
    """
    Get a list of CaseD using data provided list of CNBPID.
    :param dataset: the indexing list of dictionary showing correspondence
    :param list_CNBPID:
    :return:
    """
    list_filtered_dict = filter_basedon_CNBPID(dataset, CNBPID)
    list_caseID = []
    for case in list_filtered_dict:
        list_caseID.append(case["caseid"])
    return list_caseID


def get_all_CNBPIDs():
    """
    Obtain all the CNBPIDs from the RedCap database.
    :return: CNBPID & record ID correspondence list.
    """
    get_recordfields()

    # Two constants we'll use throughout
    TOKEN = environment.REDCAP_TOKEN_CNN_ADMISSION
    URL = "https://redcap.cnbp.ca/api/"
    project_admission = Project(URL, TOKEN)
    subset = project_admission.export_records(fields=["cnbpid"])

    return subset


if __name__ == "__main__":
    # def test_get_all_CNBPIDs():
    output = get_all_CNBPIDs()
    # test = filter_basedon_CNBPID(output, "VXS0000003")
    test = filter_basedon_CNBPID(output, ["VXS0000003", "VXS0000015"])
    print(test[1]["caseid"])
    print(test[1]["cnbpid"])
