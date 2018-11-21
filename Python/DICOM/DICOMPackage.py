from DICOM.validate import DICOM_validate
from PythonUtils.file import zip_with_name
from PythonUtils.env import load_validate_dotenv
from LORIS.validate import LORIS_validation
from LORIS.timepoint import LORIS_timepoint
from LocalDB.schema import CNBP_blueprint
import logging
import sys
import os

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logger = logging.getLogger('DICOMPackage Class')

class DICOMPackage:
    """
    DICOM package class that represents a collection of DICOM
    files with shared ID, CNBP, timepoint, MRN etc information usually obtained from the same session
    """
    def __init__(self, dicom_folder=None):
        # Set the DICOM_folder attribute
        self.__dicom_folder__ = dicom_folder # reference kept to prevent auto garbage collection
        self.dicom_folder: str = dicom_folder.name

        # Set default value.
        self.validity: bool = None
        self.dicom_files: list = None # should already be validated and vetted by the DICOM_validate.path routine

        # Update validity and dicom_files
        self.validity, self.dicom_files = DICOM_validate.path(self.dicom_folder) #actual path stored in name.

        self.CNBPID: str = None # also known as PSCI id
        self.DCCID: int = None
        self.timepoint: str = None

        self.studies = None

        self.MRN: int = None # Medical Record Number

        self.is_anonymized: bool = False
        self.zipname: str = None
        self.zip_location: str = None
        logger.info("DICOMPackage initialized based on "+self.dicom_folder)

    def update_study(self):
        """
        Update the studies field based on the protocol
        :return:
        """
        from DICOM.elements import DICOM_elements
        import DICOM.API


        # Update validity and dicom_files if they have not been done before.
        if self.validity is None:
            self.validity, self.dicom_files = DICOM_validate.path(self.dicom_folder)

        # If they are found tot be valid, time to get the MRN number.
        if self.validity is True:

            # retrieve all the possible studies.
            self.studies = DICOM.API.retrieve_study_descriptions(self.dicom_files)


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
            # dicom_files are already vetted, and all of them are consistent in terms of MRN, just load the MRN from first file.
            success, self.MRN = DICOM_elements.retrieveMRN(self.dicom_files[0])
            assert success


    def get_dicom_files(self):
        """
        A more secure way of getting DICOM files instead of directly reading the attribute (as it can be None)
        :return:
        """
        if self.dicom_files is None:
            self.validity, self.dicom_files = DICOM_validate.path(self.dicom_folder)
        return self.dicom_files


    def anonymize(self):
        """
        Thie function will check all the appropriate information are correct before attempting to anonymize the whole bunch of files.
        :return:
        """
        assert(self.CNBPID  is not None)
        assert(self.DCCID is not None)
        assert(self.timepoint is not None)
        LORIS_validation.validate_CNBPID(self.CNBPID)
        LORIS_validation.validate_DCCID(self.DCCID)
        LORIS_timepoint.check_timepoint_compliance(self.timepoint)

        # Set proper variable name and also the ZIP file name for subsequent processing.
        self.is_anonymized = True
        self.zipname = self.CNBPID + "_" + self.DCCID + "_" + self.timepoint

        # todo not finished code.
        raise NotImplementedError


    def zip(self):

        zip_storage_path = load_validate_dotenv("zip_storage_location", CNBP_blueprint.dotenv_variables)

        # Change to the storage folder before carrying out the zip operation.
        os.chdir(zip_storage_path)
        zip_with_name(self.dicom_folder, self.zipname)

        # update zip location.
        self.zip_location = os.path.join(zip_storage_path, self.zipname+".zip")
