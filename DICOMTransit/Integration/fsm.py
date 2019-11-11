import os, sys, io
import datetime
import logging
from transitions import Machine


# from transitions.extensions import GraphMachine as Machine
import DICOMTransit.orthanc.API
import DICOMTransit.LORIS.API
import DICOMTransit.LocalDB.API

from DICOMTransit.DICOM.DICOMPackage import DICOMPackage
from PythonUtils.PUFile import unique_name
from PythonUtils.PUDateTime import sleep

from DICOMTransit.settings import config_get

# Import the states and transition definitions
from DICOMTransit.Integration.fsm_states import *
from DICOMTransit.Integration.fsm_transitions import *

# Sentry Log Monitoring Service SDK:
import sentry_sdk

# in order for prod and dev esting, both bool needs to change here.
run_production: bool = True
run_dev: bool = False

##################
# Logging sections
##################
sentry_sdk.init("https://d788d9bf391a4768a22ea6ebabfb4256@sentry.io/1385114")

# Set all debugging level:
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

# Create logger.
# Root Logger (for debug transition)
logger = logging.getLogger()

# Set logger path.
log_file_path = os.path.join(
    config_get("LogPath"), f"DICOMTransit_FSM_Log_{unique_name()}.txt"
)

# Set logging level for the sub modules:
logging.getLogger("transitions.core").setLevel(logging.ERROR)
logging.getLogger("urllib3").setLevel(logging.INFO)

# create the logging file handler
filehandler = logging.FileHandler(log_file_path)
formatter = logging.Formatter(
    "[%(asctime)s]\t\t%(name)s\t\t[%(levelname)8s]\t\t[%(funcName)32s():\tLine %(lineno)i]:\t\t%(message)s"
)

filehandler.setFormatter(formatter)

# add handler to logger object
logger.addHandler(filehandler)


"""
has_new_data = Method
has_new_data = Variable. 
STATUS_NETWORK = status binary variable. 
"""


class DICOMTransitImport(object):

    # Class Variables: shared across instances!!!!!
    # These are the plausible major steps within a DICOMTransitImport process.
    states = [
        # New patient path.
        ST_waiting,
        # Orthanc related:
        ST_determined_orthanc_new_data_status,
        ST_determined_orthanc_StudyUID_status,
        # File related:
        ST_detected_new_data,
        ST_obtained_new_data,
        ST_unpacked_new_data,
        ST_obtained_MRN,
        ST_determined_MRN_status,
        # Main analyses path:
        ST_processing_old_patient,
        ST_processing_new_patient,
        ST_found_insertion_status,
        ST_ensured_only_new_subjects_remain,
        ST_obtained_DCCID_CNBPID,
        ST_updated_remote_timepoint,
        ST_obtained_new_subject_gender,
        ST_obtained_new_subject_birthday,
        ST_crosschecked_seriesUID,
        ST_created_remote_subject,
        ST_harmonized_timepoints,
        ST_files_anonymized,
        ST_files_zipped,
        ST_zip_uploaded,
        ST_zip_inserted,
        ST_insertion_recorded,
        ST_retry,
        ST_error_orthanc,
        ST_error_LORIS,
        ST_error_localDB,
        ST_error_file_corruption,
        ST_error_sqlite,
        ST_error_network,
        ST_human_intervention_required,
    ]

    # Status indicator whether they are reachable/online. They are shared across all instances of import process.
    STATUS_ORTHANC = False
    STATUS_LORIS = False
    STATUS_NETWORK = False
    STATUS_FILE = False
    STATUS_LOCALDB = False

    def reinitialize(self):
        """
        This sets the attribute for one processing a SINGLE subject.
        :return:
        """
        self.critical_error = False
        ##################
        # Status Indicator Flag:
        ##################
        self.localDB_found_mrn = None

        self.matched_localUID = None
        self.matched_remoteUID = None
        self.matched_orthanc_StudyUID = None

        self.scan_anonymized = False
        self.mri_uploadID = None
        self.process_ID = None

        self.last_localDB_scan_date = None
        self.last_loris_scan_dadte = None

        ##################
        # Files:
        ##################
        # The full path to the zip file downloaded
        self.DICOM_zip = None
        # The DICOMPackage object which is being created at per subject level.
        self.DICOM_package: DICOMPackage = None
        # This is the list of the files that are constantly being monitored and checked if reachable. It is dynamicly updated through out the analyses process. It can be a list of zip files, or a single zip file. It respresents the local file resources that CONSTANTLY needs to be monitored to ensure no fault occurs.
        self.files = []

        ##################
        # Error Handling:
        ##################
        # Current retry number.
        self.retry = 0

        # The maximum number of retry before machine hangs or ask for human intervention
        self.max_retry = 12  # first retry in minutes, then in hours, lastly in days.

    def __init__(self):

        # These variables are SUBJECT specific and needs to be reset ever time a new subject is being processed.
        self.reinitialize()

        # Only store variables that persist ACROSS subject.
        # Timestamp
        self.time = datetime.datetime.now()
        # We shall name this with
        self.name = self.time.isoformat().replace(" : ", "")

        ##################
        # Machine Meta:
        ##################
        self.transitions_last: list = []
        self.states_last: list = []
        # This is the state machine which will be updated as the analyses process.
        self.machine: Machine = None

        ##################
        # Orthanc
        ##################
        if run_production is True and run_dev is False:
            self.credential = DICOMTransit.orthanc.API.get_prod_orthanc_credentials()
        else:
            self.credential = DICOMTransit.orthanc.API.get_dev_orthanc_credentials()

        self.orthanc_has_new_data = False
        # the list of all StudyUIDs returned by Orthanc.
        self.orthanc_list_all_StudiesUIDs: list = []
        # this variable keeps track of the INDEX among the list returned by Orthanc which the current processing is being done. In theory, it should never be more than 1 as WHEN we detected already inserted subjects against local database, we removed that entry from the list and go to the next one.
        self.orthanc_index_current_study = 0
        self.orthanc_studies_buffer_limit: int = 50  # the maximum number of studies that will be kept in Orthanc.

    def setup_machine(self):
        """
        This sections etup the finite state machine, while also define the traversal pathways among the states within them.
        :return:
        """

        # Initialize the state machine
        machine = Machine(
            model=self,
            auto_transitions=True,  # this is enabled such taht we can FORCE reset the state of the machine for error recovery
            states=self.states,
            # send_event=True,
            # title="Import Process is Messy",
            # show_auto_transitions=True,
            # show_conditions=True,
            before_state_change=self.record_last_state.__name__,  # record the last state and transition before changing.
            initial=ST_waiting,
        )

        # Universal Transitions:

        # Check orthanc for new data, if has new data, proceed to the next stage. Else, no stage transition happen.

        machine.add_transition(
            TR_UpdateOrthancNewDataStatus,
            ST_waiting,
            ST_determined_orthanc_new_data_status,
            prepare=self.UpdateOrthancStatus.__name__,
            unless=self.is_Orthanc_Unavailable.__name__,  # Check orthanc status.
            after=[self.GetOrthancList.__name__, self.ProcessOrthancList.__name__],
        )  # this will set the flag related to whether there is new orthanc data

        # Paired branching transitions to see if to proceed with new data analyses or go back waiting.
        machine.add_transition(
            TR_HandlePotentialOrthancData,
            ST_determined_orthanc_new_data_status,
            ST_waiting,
            unless=self.has_new_data.__name__,
        )
        machine.add_transition(
            TR_HandlePotentialOrthancData,
            ST_determined_orthanc_new_data_status,
            ST_detected_new_data,
            conditions=self.has_new_data.__name__,
        )

        # After checking orthanc status, check with localDB for existing StudyUID
        machine.add_transition(
            TR_CheckLocalDBStudyUID,
            ST_detected_new_data,
            ST_determined_orthanc_StudyUID_status,
            prepare=self.UpdateLocalDBStatus.__name__,
            unless=self.is_LocalDB_Unavailable.__name__,
            after=self.CheckLocalDBStudyUID.__name__,
        )

        # Paired branching transitions to see if to proceed with new data analyses or go back waiting.
        machine.add_transition(
            TR_ProcessNextSubject,
            ST_determined_orthanc_StudyUID_status,
            ST_determined_orthanc_new_data_status,
            prepare=self.UpdateOrthancStatus.__name__,
            conditions=self.has_matched_orthanc_StudyUID.__name__,
            unless=self.is_Orthanc_Unavailable.__name__,
            after=[self.DeleteSubject.__name__, self.ProcessOrthancList.__name__],
        )

        machine.add_transition(
            TR_DownloadNewData,
            ST_determined_orthanc_StudyUID_status,
            ST_obtained_new_data,
            prepare=self.UpdateOrthancStatus.__name__,
            unless=[
                self.is_Orthanc_Unavailable.__name__,
                self.has_matched_orthanc_StudyUID.__name__,
            ],
            after=self.DownloadNewData.__name__,
        )

        # After checking the zip file status, unpack the new data
        machine.add_transition(
            TR_UnpackNewData,
            ST_obtained_new_data,
            ST_unpacked_new_data,
            prepare=self.UpdateFileStatus.__name__,
            unless=self.is_File_Unavailable.__name__,
            after=self.UnpackNewData.__name__,
        )  # need to check zip file.

        # After checking the unpacked file file status, check the file for MRN
        machine.add_transition(
            TR_ObtainDICOMMRN,
            ST_unpacked_new_data,
            ST_obtained_MRN,
            prepare=self.UpdateFileStatus.__name__,
            unless=self.is_File_Unavailable.__name__,
            after=self.CheckMRN.__name__,
        )  # need to check the content of the zip file success

        # After checking the local DB status, query it for MRN EXISTENCE.
        machine.add_transition(
            TR_UpdateNewMRNStatus,
            ST_obtained_MRN,
            ST_determined_MRN_status,
            prepare=self.UpdateLocalDBStatus.__name__,
            unless=self.is_LocalDB_Unavailable.__name__,
            after=self.CheckLocalDBMRN.__name__,
        )

        # Paired branching transitions
        # Depending on the result of the MRN check, whether it exist previously or not, this is where the decision tree bifurcate
        machine.add_transition(
            TR_ProcessPatient,
            ST_determined_MRN_status,
            ST_processing_old_patient,
            conditions=self.found_MRN.__name__,
        )
        machine.add_transition(
            TR_ProcessPatient,
            ST_determined_MRN_status,
            ST_processing_new_patient,
            unless=self.found_MRN.__name__,
        )

        # Old Subject Path.

        # Check if the old subject has already been inserted.
        machine.add_transition(
            TR_FindInsertionStatus,
            ST_processing_old_patient,
            ST_found_insertion_status,
            prepare=self.UpdateLocalDBStatus.__name__,
            unless=self.is_LocalDB_Unavailable.__name__,
            after=self.CheckLocalUID.__name__,
        )  # Check if the current subject is already inserted.

        # Paired branching transitions
        # Cycle back to the detected new data with adjusted subjects list.

        machine.add_transition(
            TR_ProcessNextSubject,
            ST_found_insertion_status,
            ST_determined_orthanc_new_data_status,
            prepare=self.UpdateOrthancStatus.__name__,
            conditions=[self.has_matched_localUID.__name__],
            unless=self.is_Orthanc_Unavailable.__name__,
            after=[self.DeleteSubject.__name__, self.ProcessOrthancList.__name__],
        )  # then do we carry out the deletion process only when 1) scan processd. 2) orthanc reachable.
        # Once all subjects are completed, move on to process the new subjects.
        machine.add_transition(
            TR_QueryLocalDBForDCCID,
            ST_found_insertion_status,
            ST_obtained_DCCID_CNBPID,
            prepare=[self.UpdateLocalDBStatus.__name__],
            unless=[
                self.is_LocalDB_Unavailable.__name__,
                self.has_matched_localUID.__name__,
            ],
            after=self.QueryLocalDBForCNBPIDDCCID.__name__,
        )

        # Now we know that this subject was previously seen, and we need to check if this timepoint has already processed before.
        machine.add_transition(
            TR_QueryRemoteUID,
            ST_obtained_DCCID_CNBPID,
            ST_crosschecked_seriesUID,
            prepare=[self.UpdateLORISStatus.__name__],
            unless=[self.is_LORIS_Unavailable.__name__],
            after=self.CheckRemoteUID.__name__,
        )

        # Paired branching conditions
        machine.add_transition(
            TR_ProcessNextSubject,
            ST_crosschecked_seriesUID,
            ST_determined_orthanc_new_data_status,
            prepare=self.UpdateOrthancStatus.__name__,
            conditions=[self.has_matched_remoteUID.__name__],
            unless=self.is_Orthanc_Unavailable.__name__,
            after=[self.DeleteSubject.__name__, self.ProcessOrthancList.__name__],
        )  # then do we carry out the deletion process only when 1) scan processd. 2) orthanc reachable.

        machine.add_transition(
            TR_IncrementRemoteTimepoint,
            ST_crosschecked_seriesUID,
            ST_updated_remote_timepoint,
            prepare=[self.UpdateLORISStatus.__name__],
            unless=[
                self.is_LORIS_Unavailable.__name__,
                self.has_matched_remoteUID.__name__,
            ],
            after=self.IncrementRemoteTimepoint.__name__,
        )

        # We then need to record this timepoint in the local database. Once this is done, we reached HARMONIZED TIMEPOINT state
        machine.add_transition(
            TR_UpdateLocalRecords,
            ST_updated_remote_timepoint,
            ST_harmonized_timepoints,
            prepare=[self.UpdateLocalDBStatus.__name__],
            unless=[self.is_LocalDB_Unavailable.__name__],
            after=self.UpdateLocalRecord.__name__,
        )

        # New Subject Path

        # After ensuring the DICOM files are available, Get gender information from DICOM files.
        machine.add_transition(
            TR_RetrieveGender,
            ST_processing_new_patient,
            ST_obtained_new_subject_gender,
            prepare=[self.UpdateFileStatus.__name__],
            unless=[self.is_File_Unavailable.__name__],
            after=self.RetrieveGender.__name__,
        )

        # After ensuring the DICOM files are available, Get birthday information from DICOM files.
        machine.add_transition(
            TR_RetrieveBirthday,
            ST_obtained_new_subject_gender,
            ST_obtained_new_subject_birthday,
            prepare=[self.UpdateFileStatus.__name__],
            unless=[self.is_File_Unavailable.__name__],
            after=self.RetrieveBirthday.__name__,
        )

        # self.machine.add_transition(TR_RetrieveStudy.__name__, "obtained_new_subject_birthday.__name__, "RetrieveStudy.__name__,
        #                            before="UpdateFileStatus.__name__)
        # fixme: this part dynamicly update the project of the DICOM_package.

        # After ensuring LORIS is available, we call the LORIS to create this subject (with default V1 timepoint)
        machine.add_transition(
            TR_RemoteCreateSubject,
            ST_obtained_new_subject_birthday,
            ST_created_remote_subject,
            prepare=[self.UpdateLORISStatus.__name__],
            unless=[self.is_LORIS_Unavailable.__name__],
            after=self.LORISCreateSubject.__name__,
        )

        # After ensuring LocalDB is available, we call the LocalDB to create this subject (with default V1 timepoint)
        machine.add_transition(
            TR_LocalDBCreateSubject,
            ST_created_remote_subject,
            ST_harmonized_timepoints,
            prepare=[self.UpdateLocalDBStatus.__name__],
            unless=[self.is_LocalDB_Unavailable.__name__],
            after=self.LocalDBCreateSubject.__name__,
        )

        # From this point onward, all path are merged:
        # Now loris and LocalDB are up to date, we can start anonymizing the file.
        # Check files are still there before anonymizing it.
        machine.add_transition(
            TR_AnonymizeFiles,
            ST_harmonized_timepoints,
            ST_files_anonymized,
            prepare=[self.UpdateFileStatus.__name__],
            unless=[self.is_File_Unavailable.__name__],
            after=[self.AnonymizeFiles.__name__],
        )

        # BRANCHING CONDITION
        # Check files are still there before zipping it.
        # Also double check for anonymization.
        machine.add_transition(
            TR_ZipFiles,
            ST_files_anonymized,
            ST_files_zipped,
            prepare=[
                self.DoubleCheckAnonymization.__name__,
                self.UpdateFileStatus.__name__,
            ],
            conditions=self.are_anonymized.__name__,
            unless=[self.is_File_Unavailable.__name__],
            after=self.ZipFiles.__name__,
        )
        # If failed anonymization check (e.g. file got swapped somwhow? REDO anonymization!
        machine.add_transition(
            TR_ZipFiles,
            ST_files_anonymized,
            ST_harmonized_timepoints,
            prepare=[
                self.DoubleCheckAnonymization.__name__,
                self.UpdateFileStatus.__name__,
            ],
            unless=[self.is_File_Unavailable.__name__, self.are_anonymized.__name__],
        )

        machine.add_transition(
            TR_UploadZip,
            ST_files_zipped,
            ST_zip_uploaded,
            prepare=[self.UpdateLORISStatus.__name__],
            unless=[self.is_LORIS_Unavailable.__name__],
            after=[self.UploadZip.__name__, self.CheckUploadSuccess.__name__],
        )

        machine.add_transition(
            TR_InsertSubjectData,
            ST_zip_uploaded,
            ST_zip_inserted,
            prepare=[self.UpdateLORISStatus.__name__],
            conditions=[self.CheckUploadSuccess.__name__],
            unless=[self.is_LORIS_Unavailable.__name__],
            after=[
                self.InsertSubjectData.__name__,
                self.CheckInsertionSuccess.__name__,
            ],
        )

        machine.add_transition(
            TR_RecordInsertion,
            ST_zip_inserted,
            ST_insertion_recorded,
            prepare=[self.UpdateLocalDBStatus.__name__],
            unless=[self.is_LocalDB_Unavailable.__name__],
            after=self.RecordInsertion.__name__,
        )

        machine.add_transition(
            TR_ProcessNextSubject,
            ST_insertion_recorded,
            ST_determined_orthanc_new_data_status,
            prepare=self.UpdateOrthancStatus.__name__,
            conditions=[self.has_more_data.__name__],
            unless=self.is_Orthanc_Unavailable.__name__,
            after=[self.DeleteSubject.__name__, self.ProcessOrthancList.__name__],
        )

        machine.add_transition(
            TR_ResumeMonitoring,
            ST_insertion_recorded,
            ST_waiting,
            unless=[self.has_more_data.__name__],
            after=self.DeleteSubject.__name__,
        )

        ##################################################################################
        # Error transition, any time there is a critical error, skip to the next subject.
        ##################################################################################
        machine.add_transition(
            TR_ProcessNextSubject,
            "*",
            ST_determined_orthanc_new_data_status,
            prepare=self.UpdateOrthancStatus.__name__,
            conditions=[self.has_critical_error.__name__],
            unless=self.is_Orthanc_Unavailable.__name__,
            after=[self.DeleteSubject.__name__, self.ProcessOrthancList.__name__],
        )

        # Retrying block.
        machine.add_transition(
            TR_reattempt,
            [
                ST_error_orthanc,
                ST_error_LORIS,
                ST_error_file_corruption,
                ST_error_localDB,
                ST_error_network,
            ],
            "=",
        )

        # Any time, in ANY state, if these check fails, we should go to error state. There might be additional flags in terms situation specific reactions.
        machine.add_transition(
            TR_DetectedOrthancError,
            "*",
            ST_error_orthanc,
            unless=self.ExceedMaxRetry.__name__,
            after=self.RetryPreviousActions.__name__,
        )

        machine.add_transition(
            TR_DetectedLORISError,
            "*",
            ST_error_LORIS,
            unless=self.ExceedMaxRetry.__name__,
            after=self.RetryPreviousActions.__name__,
        )

        machine.add_transition(
            TR_DetectedFileError,
            "*",
            ST_error_file_corruption,
            unless=self.ExceedMaxRetry.__name__,
            after=self.RetryPreviousActions.__name__,
        )

        machine.add_transition(
            TR_DetectedLocalDBError,
            "*",
            ST_error_localDB,
            unless=self.ExceedMaxRetry.__name__,
            after=self.RetryPreviousActions.__name__,
        )

        machine.add_transition(
            TR_DetectedNetworkError,
            "*",
            ST_error_network,
            unless=self.ExceedMaxRetry.__name__,
            after=self.RetryPreviousActions.__name__,
        )

        # At the end, if all else fails, logs, ask for help. Ready for next run.
        # Meatbag state
        machine.add_transition(
            TR_DetectedOrthancError,
            "*",
            ST_human_intervention_required,
            conditions=self.ExceedMaxRetry.__name__,
        )

        machine.add_transition(
            TR_DetectedLORISError,
            "*",
            ST_human_intervention_required,
            conditions=self.ExceedMaxRetry.__name__,
        )

        machine.add_transition(
            TR_DetectedFileError,
            "*",
            ST_human_intervention_required,
            conditions=self.ExceedMaxRetry.__name__,
        )

        machine.add_transition(
            TR_DetectedLocalDBError,
            "*",
            ST_human_intervention_required,
            conditions=self.ExceedMaxRetry.__name__,
        )

        machine.add_transition(
            TR_DetectedNetworkError,
            "*",
            ST_human_intervention_required,
            conditions=self.ExceedMaxRetry.__name__,
        )

        # assign to INSTANCE, not class!
        self.machine = machine

    # graph object is created by the machine
    def show_graph(self, **kwargs):
        """
        Used on LINUX (due to dependency hell on windows) to generate the workflow image of the finite state machine.
        :param kwargs:
        :return:
        """
        stream = io.BytesIO()
        self.get_graph(**kwargs).draw(stream, prog="dot", format="png")
        output_object = stream.getvalue()
        with open(f"{self.name}.png", "wb") as png:
            png.write(output_object)

    def GetOrthancList(self):
        logger.info("Checking Orthanc for new data!")

        # Get updated orthanc StudyUID.
        self.orthanc_list_all_StudiesUIDs = DICOMTransit.orthanc.API.get_all_subject_StudyUIDs(
            self.credential
        )
        logger.info("Obtained list of all StudiesUID SHA from Orthanc")

    def ProcessOrthancList(self):
        """
        Check if there are new data. Set the proper flag.
        :return:
        """
        # Note this part actually deal with loop back from already inserted situation TOO.
        if (
            self.orthanc_list_all_StudiesUIDs is None
            or len(self.orthanc_list_all_StudiesUIDs) == 0
        ):
            self.orthanc_has_new_data = False
            logger.info("Orthanc has no new data for us.")
        else:
            self.orthanc_has_new_data = True
            # fixme: for now, only analyze ONE single subject from the Orthanc query.
            # self.orthanc_index_current_subject = self.orthanc_index_current_subject + 1
            logger.info("Detected new data on the Orthanc. Commence processing. ")

    def CheckLocalDBStudyUID(self):
        """
        Check LocalDB for the particular StudyUID. Recall StudyUID is appended PER MRN
        :return:
        """
        import json

        # Determine current StudyUID..
        current_study_UID = self.orthanc_list_all_StudiesUIDs[
            self.orthanc_index_current_study
        ]

        # Check the database, get list of all possible study UID.
        list_knownStudyUID = DICOMTransit.LocalDB.API.get_list_StudyUID()

        if list_knownStudyUID is None:
            self.matched_orthanc_StudyUID = False
            return

        # Loop through all possible SubjectUID
        for known_StudyUID in list_knownStudyUID:
            list_known_StudyUID = json.loads(
                known_StudyUID
            )  # remember, subjectUUID can have more tha ONE!
            if current_study_UID in list_known_StudyUID:
                self.matched_orthanc_StudyUID = True
                return

        self.matched_orthanc_StudyUID = False
        return

    def DownloadNewData(self):
        """
        Download the new data for a SINGLE subject. We will return to this state when more subjects exist. Since this state is reached once we confirm there are new data.
        :return:
        """
        logger.info("Downloading new data now!")

        subject = self.orthanc_list_all_StudiesUIDs[self.orthanc_index_current_study]

        subject_url = (
            f"{self.credential.url}/studies/{subject}/archive"
        )  # it must contain patients/ and archive in the path name

        self.DICOM_zip = DICOMTransit.orthanc.API.get_StudyUID_zip(
            subject_url, self.credential
        )

        # Update the self.files to be scrutinized
        self.files.clear()
        self.files.append(self.DICOM_zip)
        logger.info("Successfully downloaded the data.")

    def DeleteSubject(self):

        # If currently, Orthanc has more than subjects we plan to keep, remove the subject we just checked WHICH we know has already been inserted.
        # Note that THIS does not influnece the list in any ways, It influence Orthanc subjects DIRECTLY.
        if len(self.orthanc_list_all_StudiesUIDs) > self.orthanc_studies_buffer_limit:
            studyUID = self.orthanc_list_all_StudiesUIDs[
                self.orthanc_index_current_study
            ]
            DICOMTransit.orthanc.API.delete_study(studyUID)
            logger.info(
                "More subjects exists than the current buffer size. Removing a already downloaded subject before processing next subject. "
            )

        # Instead of actually deleting the subject, let's try to remove the found subject from the list. This will move the analyses forward.
        # As this is EQUIVALENT of moving the index forward
        del self.orthanc_list_all_StudiesUIDs[self.orthanc_index_current_study]
        # Now, the index will refer to the next subject. Also, we can recycle the state/list length check etc.
        # @todo: check how the deletion work in a real scenerio.
        logger.debug("Mock deleting the subject currently")

    def UnpackNewData(self):
        """
        Properly create the DICOM package and update its relevant basic informations like files reference and UIDs
        :return:
        """

        path_temp_zip = config_get("ZipPath")

        # Properly set the DICOM_package.
        temporary_folder = DICOMTransit.orthanc.API.unpack_subject_zip(
            self.DICOM_zip, path_temp_zip
        )

        # Orthanc files are GUARNTEED to have consistency name and ID so no need to check that. A cursory DICOM check is good enough for performance reasons.

        self.DICOM_package = DICOMPackage(
            temporary_folder, consistency_check=False
        )  # Series UID is extracted at this time.
        # Update unique UID information to help discriminate existing scans.
        # self.DICOM_package.update_sUID()

        self.DICOM_package.project = (
            "loris"
        )  # fixme: this is a place holder. This neeeds to be dyanmiclly updated.

        # Update the self.files to be scrutinized
        self.files.clear()
        self.files = self.DICOM_package.get_dicom_files(
            consistency_check=False
        )  # consistency do not need to be checked.

        logger.info("Successfully unpacked the data downloaded.")

    def CheckMRN(self):
        """
        Check the MRN from the file for validity. Assign a default compliant MRN when the data is non-compliant.
        :return:
        """
        # Update some of the key process related to the DICOM_packages that have just been created.
        success = self.DICOM_package.update_MRN()

        if not success:
            self.DICOM_package.MRN = 999999
            logger.warning(
                "Non-compliant MRN detected! Assigning default placeholder MRN of 9999999."
            )
        else:
            logger.info("Subject specific MRN pass check.")

    def CheckLocalDBMRN(self):
        """
        Check the MRN from the local database.
        :return:
        """
        self.localDB_found_mrn = DICOMTransit.LocalDB.API.check_MRN(
            self.DICOM_package.MRN
        )
        logger.info("Successful checking local database about the MRN")

    def CheckLocalDBMatchingScanDate(self):
        """
        Check scan dates to see if it has already been inserted. This will influence the subsequent check.
        :return:
        """
        # Get DICOM date.
        DICOM_date = self.DICOM_package.scan_date

        # Use DICOM's MRN to get the LocalDB last known scan date, as we previously already know the MRN exist in the database
        LocalDB_date_string = DICOMTransit.LocalDB.API.get_scan_date(
            self.DICOM_package.MRN
        )
        self.last_localDB_scan_date = datetime.datetime.strptime(
            LocalDB_date_string, "%Y-%m-%d %H:%M:%S"
        )
        logger.info("Last known scan date for this subject was: " + LocalDB_date_string)

        if DICOM_date == self.last_localDB_scan_date:
            logger.info(
                "Scan date already exist in the database. Data likely already exist. Consider manual intervention. "
            )
            self.matched_localUID = True
            # Already processed.
            # self.orthanc_index_current_subject = self.orthanc_index_current_subject + 1
        else:
            # Default path is already it has not been processed.
            self.matched_localUID = False
            logger.info(
                "Dealing with new potentially subject. Conducting stage 2 test with LORIS visit timepoint check."
            )

    def CheckLocalUID(self):
        """
        Check remote scan dates to see if it has already been inserted before. This check helps prevent insertion of previously inserted (but then deleted subject!)
        :return:
        """

        # LORIS API to get a list of VISIT timepoints.
        list_local_series_UID = DICOMTransit.LocalDB.API.get_SeriesUIDs(
            self.DICOM_package.MRN
        )

        # In very rare cases where UID field is somehow empty, we presume ANYTHING we see, is new.
        if list_local_series_UID is None:
            self.matched_localUID = False
            return

        # Compare the two list and ensure that the UID fromt eh DICOM has not been seen before remotely.
        for uid in self.DICOM_package.list_series_UID:
            if uid in list_local_series_UID:
                self.matched_localUID = True
                logger.info("Current list of DICOM series UID has been seen before!")
                return
        self.matched_localUID = False
        logger.info(
            "Confirmed that current list of DICOM series UID are new with respect to local database!"
        )

    def CheckRemoteUID(self):
        """
        Check remote scan dates to see if it has already been inserted before. This check helps prevent insertion of previously inserted (but then deleted subject!)
        :return:
        """
        # Get DICOM UID
        DICOM_date = self.DICOM_package.scan_date

        # LORIS API to get a list of VISIT timepoints.
        list_remote_series_UID = DICOMTransit.LORIS.API.get_allUID(
            self.DICOM_package.DCCID
        )

        # Compare the two list and ensure that the UID fromt eh DICOM has not been seen before remotely.
        for uid in self.DICOM_package.list_series_UID:
            if uid in list_remote_series_UID:
                self.matched_remoteUID = True
                logger.info("Current list of DICOM series UID has been upload before!")
                return
        self.matched_remoteUID = False
        logger.info(
            "Confirmed that current list of DICOM series UID are new with respect to LORIS database!"
        )

    # Old Subject Path:
    def QueryLocalDBForCNBPIDDCCID(self):

        self.DICOM_package.CNBPID = DICOMTransit.LocalDB.API.get_CNBP(
            self.DICOM_package.MRN
        )

        # Use MRN to retrieve DCCID, update the dicom-package
        self.DICOM_package.DCCID = DICOMTransit.LocalDB.API.get_DCCID(
            self.DICOM_package.MRN
        )

        # Get the latest local known timepoint:
        self.last_localDB_timepoint = DICOMTransit.LocalDB.API.get_timepoint(
            self.DICOM_package.MRN
        )
        self.last_localDB_scan_date = DICOMTransit.LocalDB.API.get_scan_date(
            self.DICOM_package.MRN
        )
        logger.info(
            f"Last known localDB timepoint: {self.last_localDB_timepoint } on {self.last_localDB_scan_date}"
        )

    def IncrementRemoteTimepoint(self):
        # Using LORIS API to create the new timepoint:
        latest_timepoint = DICOMTransit.LORIS.API.increment_timepoint(
            self.DICOM_package.DCCID
        )
        self.DICOM_package.timepoint = latest_timepoint
        logger.info("Obtained the latest timepoint for the subject from LORIS.")

    def UpdateLocalRecord(self):
        # Update the record to use the latest timepoint and the scandate!
        DICOMTransit.LocalDB.API.set_timepoint(
            self.DICOM_package.MRN, self.DICOM_package.timepoint
        )
        DICOMTransit.LocalDB.API.set_scan_date(
            self.DICOM_package.MRN, self.DICOM_package.scan_date
        )
        # take old and combine with new so we have a full history of all ever UID associated with this subject.
        DICOMTransit.LocalDB.API.append_SeriesUID(
            self.DICOM_package.MRN, self.DICOM_package.list_series_UID
        )
        logger.info(
            "Incremented the local VISIT timepoint for the subject successfully."
        )

    # New Subject Path:
    def RetrieveGender(self):
        success = self.DICOM_package.update_sex()
        assert success
        logger.info("Subject specific sex DICOM field pass check.")

        success = self.DICOM_package.update_gender()
        assert success
        logger.info("Subject specific LORIS specific gender information determined.")

    def RetrieveBirthday(self):
        success = self.DICOM_package.update_birthdate()
        assert success
        logger.info("Subject specific birthdate pass check.")

    def RetrieveStudy(self):
        # @todo: For now, all project are under LORIS. The projectID etc systems are not being actively used.
        self.DICOM_package.project = "loris"
        # raise NotImplementedError

    def LORISCreateSubject(self):
        # create new PSCID and get DCCID
        success, DCCID, PSCID = DICOMTransit.LORIS.API.create_candidate(
            self.DICOM_package.project,
            self.DICOM_package.birthday,
            self.DICOM_package.gender,
        )
        # Local Variable for anonymization.
        self.DICOM_package.DCCID = DCCID
        self.DICOM_package.CNBPID = PSCID
        self.DICOM_package.timepoint = "V1"  # auto generated.
        logger.info("Creating subject remotely on LORIS is successful.")

    def LocalDBCreateSubject(self):
        # CNBPID had to be created first.
        DICOMTransit.LocalDB.API.set_CNBP(
            self.DICOM_package.MRN, self.DICOM_package.CNBPID
        )
        DICOMTransit.LocalDB.API.set_DCCID(
            self.DICOM_package.MRN, self.DICOM_package.DCCID
        )
        DICOMTransit.LocalDB.API.set_timepoint(
            self.DICOM_package.MRN, self.DICOM_package.timepoint
        )
        DICOMTransit.LocalDB.API.set_scan_date(
            self.DICOM_package.MRN, self.DICOM_package.scan_date
        )
        DICOMTransit.LocalDB.API.set_SeriesUID(
            self.DICOM_package.MRN, self.DICOM_package.list_series_UID
        )
        logger.info("Creating subject locally is successful.")
        pass

    def AnonymizeFiles(self):
        # This will also update self.zipname and self.is_anonymized
        logger.info(f"Anonymizing all {len(self.DICOM_package.dicom_files)} files:")
        self.DICOM_package.anonymize()
        self.scan_anonymized = self.DICOM_package.is_anonymized
        logger.info("Successfully anonymized files.")

    def DoubleCheckAnonymization(self):
        if not self.are_anonymized():
            return

        if self.DICOM_package.is_anonymized is False:
            self.scan_anonymized = False
            return

        # Conduct a per file check to ensure that the files are porperly anonymized.
        self.scan_anonymized = self.DICOM_package.validate_anonymization()
        logger.info("Double checking anonymization is successful.")

    def ZipFiles(self):
        # This will update DICOM_package.zip location.
        self.DICOM_package.zip()

    def UploadZip(self):

        # Attempt to upload the VISIT DICOM and check the returned upload ID.
        self.mri_uploadID = DICOMTransit.LORIS.API.upload_visit_DICOM(
            self.DICOM_package.zip_location,
            self.DICOM_package.DCCID,
            self.DICOM_package.timepoint,
            False,
        )

    def InsertSubjectData(self):
        # Speical cases when auto-launch is on. The process is already triggered.
        if self.mri_uploadID == 0:
            return

        # Trigger insertion.
        else:
            self.process_ID = DICOMTransit.LORIS.API.new_trigger_insertion(
                self.DICOM_package.DCCID,
                self.DICOM_package.timepoint,
                f"{self.DICOM_package.zipname}.zip",
                self.mri_uploadID,
            )

    def RecordInsertion(self):
        # Set the completion status to ZERO
        StudyUID = self.orthanc_list_all_StudiesUIDs[self.orthanc_index_current_study]
        DICOMTransit.LocalDB.API.append_StudyUID(self.DICOM_package.MRN, StudyUID)

    def CheckUploadSuccess(self):
        if self.mri_uploadID is None:
            return False
        else:
            return True

    def CheckInsertionSuccess(self):
        # fixme a script to check insertion status success is required.
        pass

    # Conditions Method
    def has_new_data(self):
        return self.orthanc_has_new_data

    def has_more_data(self):
        if len(self.orthanc_list_all_StudiesUIDs) > 1:
            return True
        else:
            return False

    def has_critical_error(self):
        return self.critical_error

    def has_matched_localUID(self):
        return self.matched_localUID

    def has_matched_remoteUID(self):
        return self.matched_remoteUID

    def has_matched_orthanc_StudyUID(self):
        return self.matched_orthanc_StudyUID

    def found_MRN(self):
        return self.localDB_found_mrn

    def are_anonymized(self):
        return self.scan_anonymized

    # These methods are used to check system unavailiabilites.
    def is_Orthanc_Unavailable(self):
        return not self.STATUS_ORTHANC

    def is_LORIS_Unavailable(self):
        return not self.STATUS_LORIS

    def is_File_Unavailable(self):
        return not self.STATUS_FILE

    def is_LocalDB_Unavailable(self):
        return not self.STATUS_LOCALDB

    def is_Network_Unavailable(self):
        return not self.STATUS_NETWORK

    # Check methods which report the status of various settings.
    def UpdateLORISStatus(self):

        self.UpdateNetworkStatus()
        # Return false if network is down.
        if not self.STATUS_NETWORK:
            self.STATUS_LORIS = self.STATUS_NETWORK

        # Ping LORIS production server to check if it is online.
        from DICOMTransit.LORIS.API import check_status

        self.STATUS_LORIS = check_status()

        if self.STATUS_LORIS:
            logger.debug("LORIS production system status OKAY!")
        else:
            logger.critical(
                "LORIS system not accessible using the provided credential. Either LORIS system is DOWN OR your credential is no longer valid."
            )
            self.trigger_wrap(TR_DetectedLORISError)

    def UpdateNetworkStatus(self):
        # Ping CNBP frontend server.
        # Ping LORIS server.
        # Ping Google.
        from DICOMTransit.LORIS.API import check_online_status

        self.STATUS_NETWORK = check_online_status()
        if self.STATUS_NETWORK:
            logger.debug("General Network system status OKAY!")
        else:
            logger.critical("!!!General Network system is DOWN!!!")
            self.trigger_wrap(TR_DetectedNetworkError)

    def UpdateLocalDBStatus(self):
        # Read local db. See if it exist based on the setting.
        from DICOMTransit.LocalDB.API import check_status

        self.STATUS_LOCALDB = check_status()
        if self.STATUS_LOCALDB:
            logger.debug("LocalDB system status OKAY!")
        else:
            logger.critical("!!!LocalDB system is DOWN!!!")
            self.trigger_wrap(TR_DetectedLocalDBError)

    def UpdateOrthancStatus(self):
        # Check ENV for the predefined Orthanc URL to ensure that it exists.
        from DICOMTransit.orthanc.API import (
            check_prod_orthanc_status,
            check_dev_orthanc_status,
        )

        if run_production is True and run_dev is False:
            self.STATUS_ORTHANC = check_prod_orthanc_status()
        else:
            self.STATUS_ORTHANC = check_dev_orthanc_status()

        if self.STATUS_ORTHANC:
            logger.debug("Orthanc system status OKAY!")
        else:
            logger.critical("!!!Orthanc system is DOWN!!!")
            self.trigger_wrap(TR_DetectedOrthancError)

    def UpdateFileStatus(self):
        # Ensure the file provided exist.
        # NOTE: this does not check if the valid is the right is CORRECT!
        for file in self.files:
            if os.path.exists(file) and os.path.isfile(file):
                continue
            else:
                self.STATUS_FILE = False
                self.trigger_wrap(TR_DetectedFileError)
        self.STATUS_FILE = True
        logger.debug("File(s) status APPEAR OKAY!")

    def RetryPreviousActions(self):
        """
        This method is called when detected an error of SOME sort.
        :return:
        """
        last_state = self.states_last[-1]
        last_transition = self.transitions_last[-1]

        if self.retry == 0:  # immediately retry
            logger.info(
                f"Transition from {last_state} using {last_transition} failed and is now being retried first time."
            )
            logger.info(f"Immediately retrying. Current time: {unique_name()}")

        elif self.retry <= 5:  # wait for minutes at a time. ,
            logger.warning(
                f"Warning! Transition from {last_state} using {last_transition} failed and is now being retried on Retry#{self.retry}."
            )
            logger.warning(
                f"Sleeping {self.retry} minutes. Current time: {unique_name()}"
            )
            sleep(m=self.retry)
        elif self.retry <= 10:  # wait for hours at a time.
            logger.error(
                f"ERROR!! Transition from {last_state} using {last_transition} failed and is now being retried on Retry#{self.retry}."
            )
            logger.error(f"Sleeping {self.retry} hours. Current time: {unique_name()}")
            sleep(h=self.retry - 5)
        else:  # FINAL issues, wait for a few hours.
            logger.critical(
                f"CRITICAL!!! Transition from {last_state} using {last_transition} failed and is now being retried on Retry#{self.retry}."
            )
            logger.critical(
                f"Sleeping {self.retry} days. Current time: {unique_name()}"
            )
            sleep(h=(self.retry - 10) * 24)

        # Set to previous state.
        self.machine.set_state(last_state)

        # Trigger the previous transition
        self.trigger_wrap(last_transition)

        # Try to increment the retry counter.
        self.retry += 1
        pass

    def trigger_wrap(self, transition_name):
        """
        a wrapped call to trigger the transition.
        :param transition_name:
        :return:
        """
        # A wrapped call to the machine trigger function.
        self.transitions_last.append(transition_name)
        self.trigger(transition_name)

    def return_goto_function(self, function_name):
        """
        Return the fuction of the import_process which is to be executed.
        :param import_process:
        :param function_name:
        :return:
        """

        try:
            function = getattr(self, function_name)
            return function
        except AttributeError:
            logger.error(function_name + " not found")

    def record_last_transition(self, transition_name: str):
        """
        Keeping an archive of the states this instance has been to.
        :return:
        """
        self.transitions_last.append(transition_name)

    def record_last_state(self):
        """
        Keeping an archive of the states this instance has been to.
        :return:
        """
        self.states_last.append(self.state)

    def ExceedMaxRetry(self):
        """
        Signal for human intervention.
        :return:
        """
        if self.retry >= self.max_retry:
            return True
        else:
            return False

    '''
    def set_state(self, state: str):
        """
        Hard reset the machine to a known state: WARNING DOES NOT CHECK STATE belong.
        :param state:
        :return:
        """
        try:
            fun_to_state = getattr(self.machine, f"to_{state}")
            fun_to_state(self.machine)
        except AttributeError:
            logger.critical("State not found during set_to_state")
    '''

    def SaveStatusToDisk(self):

        raise NotImplementedError
