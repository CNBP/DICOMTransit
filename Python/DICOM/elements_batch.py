from DICOM.elements import DICOM_elements
from typing import List
from tqdm import tqdm
import logging

logger=logging.getLogger()

class DICOM_elements_batch:

    @staticmethod
    def retrieve_sUID(dicom_files: list) -> List[str]:
        """
        Check all dicom files to get a unique list of all possible UUIDs.
        :param dicom_files:
        :return:
        """
        logger.debug("Commencing unique series UID retrieval across all the DICOM files provided. ")
        from DICOM.elements import DICOM_elements
        list_unique_sUID = []
        for file in tqdm(dicom_files):
            success, UID = DICOM_elements.retrieve_seriesUID(file)
            if UID not in list_unique_sUID:
                list_unique_sUID.append(UID)
        logger.debug("Finished compiling all unique series UID across all the DICOM files provided.")

        return list_unique_sUID