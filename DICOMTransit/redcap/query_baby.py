from typing import List
from DICOMTransit.redcap.query_common import (
    filter_records,
    get_recordfields_common,
    get_fields,
    get_records,
)
from DICOMTransit.redcap import development as environment
from redcap import Project  # note this is from PyCap.redcap

"""
These functions deal with the accessing and basic interaction with the BABY table clusters from RedCap
"""


class baby_project:
    """
    One baby can have many admissions CaseIDs.
    One hospital record can have many CaseIDs.
    One baby has only one hospital record number.
    """

    def __init__(
        self,
        Token=environment.REDCAP_TOKEN_CNN_BABY,
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
        fields_keyid = ["babyid", "motherid", "baby_patieui"]

        # For now, make sure to onyl get the data related to these key ids to reduce load time
        self.data = get_fields(self.project, fields_keyid)

        # if specified, get all the records.
        if get_all_field:
            self.data = self.project.export_records()

    def filter_with_BabyID(self, babyID: str or List[str]):
        """
        Check the list, only retain the relevant CNBPIDs interested.
        :param dataset: CNBPIDs & record ID correspondence list.
        :param babyID:
        :return:
        """
        list_filtered = None

        filtered_field = "babyid"

        # Handling when babyIDs is string instead of list (allowing batch function).
        if type(babyID) is str:
            babyID = [babyID]

        list_filtered = filter_records(self.data, filtered_field, babyID)

        return list_filtered

    def get_recordfields(self, field_data: str, field_filter: str, filter_value: str):
        """
        Wrap around teh common get record fields, tailer it to the current project.
        :param field_data:
        :param field_filter:
        :param filter_value:
        :return:
        """
        self.data = get_recordfields_common(
            self.project, field_data, field_filter, filter_value
        )

    def get_PatientUI_with_BabyID(self, BabyID: str or List[str]):
        """
        Baby ID has 1:1 correspondence with PatientUI
        :return:
        """

        if type(BabyID) is str:
            BabyID = [BabyID]
        list_filtered_dict = self.filter_with_BabyID(BabyID)
        list_PatientUI = []
        for case in list_filtered_dict:
            list_PatientUI.append(case["baby_patieui"])
        return list_PatientUI

    def get_MotherID_with_BabyID(self, BabyID: str or List[str]):
        """
        Baby ID has 1:1 correspondence with MotherID
        :return:
        """
        if type(BabyID) is str:
            BabyID = [BabyID]
        list_filtered_dict = self.filter_with_BabyID(BabyID)
        list_motherID = []
        for case in list_filtered_dict:
            list_motherID.append(case["motherid"])
        return list_motherID

    def get_records_baby(self, BabyID: str or List[str]):
        """
        Do a full fields retrieve of the cases based on their INDEX which is the babyID
        :param cases:
        :return:
        """
        if type(BabyID) is str:
            BabyID = [BabyID]
        cases_data = self.project.export_records(records=BabyID)
        return cases_data


if __name__ == "__main__":
    # def test_get_all_CNBPIDs():

    baby = baby_project()
    cnbpid = "6689"
    test = baby.filter_with_BabyID(cnbpid)
    print(test)
    test = baby.get_PatientUI_with_BabyID(cnbpid)
    print(test)
    test = baby.get_MotherID_with_BabyID(cnbpid)
    print(test)

    cnbpid = ["6834", "6890"]
    test = baby.filter_with_BabyID(cnbpid)
    print(test)
    test = baby.get_PatientUI_with_BabyID(cnbpid)
    print(test)
    test = baby.get_MotherID_with_BabyID(cnbpid)
    print(test)
