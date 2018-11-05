from DICOM.validate import DICOM_validate

from PythonUtils.folder import recursive_list
import logging
import sys

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logger = logging.getLogger('DICOMPackage Class')

class DICOMPackage:
    """
    DICOM package class that represents a collection of DICOM
    files with shared ID, CNBP, visit, MRN etc information usually obtained from the same session
    """
    def __init__(self, dicom_folder=None):
        # Set the DICOM_folder attribute
        self.dicom_folder = dicom_folder

        # Set default value.
        self.validity = None
        self.dicom_files = None # should already be validated and vetted by the DICOM_validate.path routine

        # Update validity and dicom_files
        self.validity, self.dicom_files = DICOM_validate.path(dicom_folder)

        self.cnbpid = None
        self.lorisid = None
        self.visit = None
        self.MRN = None # Medical Record Number
        self.is_anonymized = False
        logger.info("DICOMPackage initialized based on "+dicom_folder)

    def update_MRN(self):
        """
        After passing the consistency check, update MRN record from one of the DICOM files.
        :return:
        """
        from DICOM.elements import DICOM_elements

        # Update validity and dicom_files if they have not been done before.
        if self.validity is None:
            self.validity, self.dicom_files = DICOM_validate.path(self.dicom_folder)

        # If they are found tot be valid, time to get the MRN number.
        if self.validity is True:
            # dicom_files are already vetted, and all of them are consistent in terms of MRN
            self.MRN = DICOM_elements.retrieveMRN(self.dicom_files)

    def get_dicom_files(self):
        return recursive_list(self.dicom_folder.name)
