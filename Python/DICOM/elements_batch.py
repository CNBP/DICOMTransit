from DICOM.elements import DICOM_elements
from typing import List

class DICOM_elements_batch:

    @staticmethod
    def retrieve_sUID(dicom_files: list) -> List[str]:
        """
        Check all dicom files to get a unique list of all possible UUIDs.
        :param dicom_files:
        :return:
        """
        from DICOM.elements import DICOM_elements
        list_sUID = []
        for file in dicom_files:
            success, UID = DICOM_elements.retrieve_seriesUID(file)
            if UID not in list_sUID:
                list_sUID.append(UID)

        return list_sUID