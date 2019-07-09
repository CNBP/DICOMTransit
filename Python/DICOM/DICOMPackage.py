from DICOM.validate import DICOM_validate
from DICOM.elements_batch import DICOM_elements_batch
from PythonUtils.file import zip_with_name
from LORIS.validate import LORIS_validation
from LORIS.timepoint import LORIS_timepoint
from settings import config_get
from typing import List
import logging
import os


logger = logging.getLogger()


class DICOMPackage:
    """
    DICOM package class that represents a collection of DICOM
    files with shared ID, CNBP, timepoint, MRN etc information usually obtained from the same session
    """

    def __init__(self, dicom_folder=None, consistency_check=True):
        logger.info("Creating subject specific DICOM package class")
        # Set the DICOM_folder attribute
        self.__dicom_folder__ = (
            dicom_folder
        )  # reference kept to prevent auto garbage collection
        self.dicom_folder: str = dicom_folder.name

        # Set default value.
        self.validity: bool = None
        self.dicom_files: list = None  # should already be validated and vetted by the DICOM_validate.path routine

        # series UID: used to tell if a scan has been uploaded before.
        self.list_series_UID = None

        # Update validity and dicom_files. This flag is used successful
        self.validity, self.dicom_files, self.list_series_UID = DICOM_elements_batch.traversal(
            self.dicom_folder, consistency_check
        )  # actual path stored in name.

        self.CNBPID: str = None  # also known as PSCI id
        self.DCCID: int = None
        self.timepoint: str = None

        self.studies: str = None  # study description from raw DICOM
        self.project: str = None  # the actual project ID used on LORIS.

        self.MRN: int = None  # Medical Record Number
        self.birthday = None
        self.sex = None
        self.gender = None
        self.scan_date = None

        self.is_anonymized: bool = False
        self.is_zipped: bool = False
        self.zipname: str = None  # this zip name has NO EXTENSION! Many code assume its extension is ZIP.
        self.zip_location: str = None

        logger.info("Commencing subject specific checks. ")

        # todo study inference is not robust. Need debug and refactoring.
        # success = self.update_study()
        # assert success

        # todo project inference is not robust. Need debug and refactoring.
        # success = self.update_project()
        # assert success

        success = self.update_scan_date()
        if success:
            logger.debug("Subject specific scan date retrieved and past check.")
        else:
            logger.error(
                "Subject scan data did not include scan date, high likelyhood of corrupt data or non-patient data. Assuming a default scan date of 1900-01-01"
            )
            raise ValueError("DICOM")  # FIXME: enable these after full debug test.

        success = self.update_birthdate()
        if success:
            logger.debug("Subject specific birthdate retrieved and past check.")
        else:
            logger.error(
                "Subjects have NO BIRTHDATE! LORIS interaction will not function."
            )
            raise ValueError("DICOM")

        success = self.update_sex()
        if success:
            logger.debug("Subject specific sex field from DICOM past check.")
        else:
            logger.error(
                "Subjects have NO BIRTHDATE! LORIS interaction will not function."
            )
            ValueError("DICOM")

        success = self.update_gender()
        if success:
            logger.debug("Subject specific LORIS gender field past check.")
        else:
            logger.error("Subject gender failed check.")
            ValueError("DICOM")

        logger.debug(
            f"DICOMPackage successfully initialized based on {self.dicom_folder}"
        )

    def check_validity(self):
        """
        #todo: this KEY WRAPPER FUNCTION function to check the validity of the object before conducting anything else. Currently not working because I am not using decorator functions properly.
        :param package_function: the package_function to be performed
        :return:
        """

        # Update validity and dicom_files if they have not been done before.
        if self.validity is None:
            # Force an individual file level naming/user ID consistency check.
            self.validity, self.dicom_files = DICOM_validate.path(
                self.dicom_folder, consistency_check=True
            )

        # Check validity before moving forward with the update process:
        if self.validity is True:
            # package_function()
            return True
        else:
            return False

    def update_study(self):
        """
        Update the studies field based on the protocol
        :return:
        """
        if self.check_validity():
            import DICOM.API

            # retrieve all the possible studies.
            self.studies = DICOM.API.retrieve_study_protocol(self.dicom_files)
            return True
        else:
            return False

    def update_project(self):
        """
        Update the actual PROJECT ID that is used on LORIS system.
        :return:
        """
        if self.check_validity():
            import DICOM.API

            self.project = DICOM.API.study_validation(self.studies)

    def update_birthdate(self):
        """
        After passing the consistency check, update MRN record from one of the DICOM files.
        :return:
        """
        if self.check_validity():
            from DICOM.elements import DICOM_elements

            # dicom_files are already vetted, and all of them are consistent in terms of MRN, just load the birthday from first file.
            success, self.birthday = DICOM_elements.retrieve_birthday(
                self.dicom_files[0]
            )
            if not success:
                raise ValueError(
                    f"Could not retrieve birthday from DICOM file {self.dicom_files[0]}"
                )
            return success
        else:
            return False

    def update_sex(self):
        """
        After passing the consistency check, update MRN record from one of the DICOM files.
        :return:
        """
        if self.check_validity():
            from DICOM.elements import DICOM_elements

            # dicom_files are already vetted, and all of them are consistent in terms of MRN, just load the sex from first file.
            success, self.sex = DICOM_elements.retrieve_sex(self.dicom_files[0])
            if not success:
                raise ValueError(
                    f"Could not retrieve sex from DICOM file {self.dicom_files[0]}"
                )
            return success
        else:
            return False

    def update_gender(self):
        """
        After passing the consistency check, update MRN record from one of the DICOM files.
        :return:
        """
        if self.check_validity():
            if self.sex == "M":
                self.gender = "Male"
            elif self.sex == "F":
                self.gender = "Female"
            return True
        else:
            return False

    def update_scan_date(self):
        """
        Retrieve the scan date from the DIOCM files and then update the DICOM archive.
        :return:
        """
        if self.check_validity():
            from DICOM.elements import DICOM_elements

            success, self.scan_date = DICOM_elements.retrieve_scan_date(
                self.dicom_files[0]
            )
            if success:
                return success
            else:
                from datetime import datetime

                self.scan_date = datetime.strptime("19000101", "%Y%m%d")
                return False
        else:
            return False

    def update_MRN(self):
        """
        After passing the consistency check, update MRN record from one of the DICOM files.
        :return:
        """
        if self.check_validity():
            from DICOM.elements import DICOM_elements

            # dicom_files are already vetted, and all of them are consistent in terms of MRN, just load the MRN from first file.
            success, self.MRN = DICOM_elements.retrieve_MRN(self.dicom_files[0])
            return success
        else:
            return False

    def get_dicom_files(self, consistency_check=True):
        """
        A more secure way of getting DICOM files instead of directly reading the attribute (as it can be None)
        :return:
        """

        # Validate all files and load them if they have not been loaded before.
        if self.dicom_files is None:
            self.validity, self.dicom_files = DICOM_validate.path(
                self.dicom_folder, consistency_check
            )
        return self.dicom_files

    def update_sUID(self) -> List[str]:
        """
        Check all dicom files to get a unique list of all possible series UIDs.
        :return:
        """
        from DICOM.elements_batch import DICOM_elements_batch

        self.list_series_UID = DICOM_elements_batch.retrieve_sUID(self.dicom_files)
        return self.list_series_UID

    def anonymize(self):
        """
        Thie function will check all the appropriate information are correct before attempting to anonymize the whole bunch of files.
        :return:
        """
        if self.CNBPID is None or self.DCCID is None or self.timepoint is None:
            logger.error("CNBPID, DCCID, Timepoint value is NONE!")
            raise ValueError

        if (
            not LORIS_validation.validate_CNBPID(self.CNBPID)
            or not LORIS_validation.validate_DCCID(self.DCCID)
            or not LORIS_timepoint.check_timepoint_compliance(self.timepoint)
        ):
            logger.error("CNBPID, DCCID, Timepoint value failed!")
            raise ValueError

        # Set proper variable name and also the ZIP file name for subsequent processing.

        self.zipname = f"{self.CNBPID}_{str(self.DCCID)}_{self.timepoint}"

        from DICOM.anonymize import DICOM_anonymize

        DICOM_anonymize.folder(self.dicom_folder, self.zipname)
        self.is_anonymized = True

    def validate_anonymization(self):
        """
        Check if all the dicom files are actually properly encoded with the proper name.
        :return:
        """
        # assuming have all the files.
        if self.dicom_files is None:
            raise ValueError("DICOM_files not initialized!")
        if not len(self.dicom_files) > 0:
            raise ValueError("Empty list of DICOM files. ")
        if self.zipname is None:
            raise ValueError(
                "You have not generated the PSCID_DCCID_Visit name properly!"
            )

        # Loop through all files and check.
        from DICOM.API import check_anonymization

        success = check_anonymization(self.dicom_files, self.zipname)
        self.is_anonymized = success
        return success

    def zip(self):
        """

        :return:
        """

        # load system default ZIP storage path.
        zip_storage_path = config_get("ZipPath")

        # Change to the storage folder before carrying out the zip operation.
        os.chdir(zip_storage_path)
        zip_with_name(self.dicom_folder, self.zipname)

        # update zip location, this is the ABSOLUTE path.
        self.zip_location = os.path.join(zip_storage_path, self.zipname + ".zip")
        self.is_zipped = True
