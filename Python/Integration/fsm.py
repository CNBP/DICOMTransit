import os, sys, inspect, io, time
import datetime
import logging
from transitions import Machine
from transitions import MachineError
#from transitions.extensions import GraphMachine as Machine
import orthanc.API
import LORIS.API
import LocalDB.API
import pickle
from DICOM.DICOMPackage import DICOMPackage
from PythonUtils.file import unique_name

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('transition')
logger.setLevel(logging.INFO)

"""
has_new_data = Method
has_new_data = Variable. 
STATUS_NETWORK = status binary variable. 

"""

#############################
# Transition Naming Variables:
#############################
# Exists purely to ensure IDE can help mis spellings vs strings, which IDE DO NOT CHECK
TR_ZipFiles = "TR_ZipFiles"

# Orthanc handling transitions
TR_UpdateOrthancNewDataStatus = "TR_UpdateOrthancNewDataStatus"
TR_HandlePotentialOrthancData = "TR_HandlePotentialOrthancData"
TR_DownloadNewData = "TR_DownloadNewData"

# File handling transitions
TR_UnpackNewData = "TR_UnpackNewData"
TR_ObtainDICOMMRN = "TR_ObtainDICOMMRN"
TR_UpdateNewMRNStatus = "TR_UpdateNewMRNStatus"
TR_ProcessPatient = "TR_ProcessPatient"

TR_FindInsertionStatus = "TR_FindInsertionStatus"
TR_ProcessNextSubject = "TR_ProcessNextSubject"

# Process Old Subjects transitions
TR_QueryLocalDBForDCCID = "TR_QueryLocalDBForDCCID"
TR_QueryRemoteUID = "TR_QueryRemoteUID"
TR_IncrementRemoteTimepoint = "TR_IncrementRemoteTimepoint"
TR_IncrementLocalTimepoint = "TR_IncrementLocalTimepoint"

# Process New Subjects transitions
TR_RetrieveGender = "TR_RetrieveGender"
TR_RetrieveBirthday = "TR_RetrieveBirthday"
TR_RemoteCreateSubject = "TR_RemoteCreateSubject"
TR_LocalDBCreateSubject = "TR_LocalDBCreateSubject"

# Files handling transitions.
TR_AnonymizeFiles = "TR_AnonymizeFiles"
TR_UploadZip = "TR_UploadZip"
TR_InsertSubjectData = "TR_InsertSubjectData"
TR_RecordInsertion = "TR_RecordInsertion"
TR_ResumeMonitoring = "TR_ResumeMonitoring"

# Error handling transitions
TR_reattempt = "TR_reattempt"
TR_DetectedOrthancError = "TR_DetectedOrthancError"
TR_DetectedLORISError = "TR_DetectedLORISError"
TR_DetectedFileError = "TR_DetectedFileError"
TR_DetectedLocalDBError = "TR_DetectedLocalDBError"
TR_DetectedNetworkError = "TR_DetectedNetworkError"

#############################
# State Naming Variables:
#############################
# Exists purely to ensure IDE can help mis spellings vs strings, which IDE DO NOT CHECK
ST_waiting = "ST_waiting"
ST_determined_orthanc_new_data_status = "ST_determined_orthanc_new_data_status"
ST_detected_new_data = "ST_detected_new_data"
ST_obtained_new_data = "ST_obtained_new_data"
ST_unpacked_new_data = "ST_unpacked_new_data"

# Old subject states
ST_obtained_MRN = "ST_obtained_MRN"
ST_determined_MRN_status = "ST_determined_MRN_status"
ST_processing_old_patient = "ST_processing_old_patient"
ST_processing_new_patient = "ST_processing_new_patient"
ST_found_insertion_status = "ST_found_insertion_status"
ST_ensured_only_new_subjects_remain = "ST_ensured_only_new_subjects_remain"
ST_obtained_DCCID_CNBPID = "ST_obtained_DCCID_CNBPID"
ST_checked_remoteSeriesUID = "ST_checked_remoteSeriesUID"
ST_updated_remote_timepoint = "ST_updated_remote_timepoint"

# New subject states
ST_obtained_new_subject_gender = "ST_obtained_new_subject_gender"
ST_obtained_new_subject_birthday = "ST_obtained_new_subject_birthday"
ST_created_remote_subject = "ST_created_remote_subject"
ST_harmonized_timepoints = "ST_harmonized_timepoints"

# Files states
ST_files_anonymized = "ST_files_anonymized"
ST_files_zipped = "ST_files_zipped"
ST_zip_uploaded = "ST_zip_uploaded"
ST_zip_inserted = "ST_zip_inserted"
ST_insertion_recorded = "ST_insertion_recorded"

# Error handling states.
ST_retry = "ST_retry"
ST_error_orthanc = "ST_error_orthanc"
ST_error_LORIS = "ST_error_LORIS"
ST_error_localDB = "ST_error_localDB"
ST_error_file_corruption = "ST_error_file_corruption"
ST_error_sqlite = "ST_error_sqlite"
ST_error_network = "ST_error_network"
ST_human_intervention_required = "ST_human_intervention_required"


class DICOMTransitImport(object):

    # Class Variables: shared across instances!!!!!
    # These are the plausible major steps within a DICOMTransitImport process.
    states = [
        # New patient path.
        ST_waiting,
        # Orthanc related:
        ST_determined_orthanc_new_data_status,
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



    def __init__(self):

        # Timestamp
        self.time = datetime.datetime.now()
        # We shall name this with
        self.name = self.time.isoformat().replace(":", "")

        ##################
        # Status Indicator Flag:
        ##################
        self.localDB_found_mrn = None
        self.scan_already_processed = True
        self.scan_anonymized = False
        self.scan_inserted = False
        self.orthanc_has_new_data = False

        self.last_localDB_scan_date = None
        self.last_loris_scan_dadte = None


        ##################
        # Machine Meta:
        ##################
        self.transitions_last: list = []
        self.states_last = []
        # This is the state machine which will be updated as the analyses process.
        self.machine = None


        ##################
        # Files:
        ##################
        # The full path to the zip file downloaded
        self.DICOM_zip = None
        # The DICOMPackage object which is being created at per subject level.
        self.DICOM_package = None
        # This is the list of the files that are constantly being monitored and checked if reachable. It is dynamicly updated through out the analyses process. It can be a list of zip files, or a single zip file. It respresents the local file resources that CONSTANTLY needs to be monitored to ensure no fault occurs.
        self.files = []


        ##################
        # Orthanc
        ##################
        self.orthanc_url, self.orthanc_user, self.orthanc_password = orthanc.API.get_prod_orthanc_credentials()

        # the list of all subjet UUIDs returned by Orthanc.
        self.orthanc_list_all_subjectUUIDs: list = []
        # this variable keeps track of the INDEX among the list returned by Orthanc which the current processing is being done. In theory, it should never be more than 1 as WHEN we detected already inserted subjects against local database, we removed that entry from the list and go to the next one.
        self.orthanc_index_current_subject = 0
        self.orthanc_buffer_limit: int = 50


        ##################
        # Error Handling:
        ##################
        # Current retry number.
        self.retry = 0
        # The maximum number of retry before machine hangs or ask for human intervention
        self.max_retry = 5

    def setup_machine(self):

        # Initialize the state machine
        machine = Machine(model=self,
                          auto_transitions=False,
                          states=self.states,
                          # send_event=True,
                          # title="Import Process is Messy",
                          # show_auto_transitions=True,
                          # show_conditions=True,
                          after_state_change="record_last_state",
                          initial="waiting")

        # Universal Transitions:

        # Check orthanc for new data, if has new data, proceed to the next stage. Else, no stage transition happen.

        machine.add_transition(TR_UpdateOrthancNewDataStatus, ST_waiting, ST_determined_orthanc_new_data_status,
                               prepare=self.UpdateOrthancStatus.__name__,
                               unless=self.is_Orthanc_Unavailable.__name__,  # Check orthanc status.
                               after=[self.GetOrthancList.__name__, CheckOrthancNewData.__name__])  # this will set the flag related to whether there is new orthanc data


        # Paired branching transitions to see if to proceed with new data analyses or go back waiting.
        machine.add_transition(TR_HandlePotentialOrthancData, ST_determined_orthanc_new_data_status, ST_waiting,
                               unless=self.has_new_data.__name__)
        machine.add_transition(TR_HandlePotentialOrthancData, ST_determined_orthanc_new_data_status, ST_detected_new_data,
                               prepare=self.UpdateOrthancStatus.__name__,
                               conditions=self.has_new_data.__name__,
                               unless=self.is_Orthanc_Unavailable.__name__
                               )

        # After checking orthanc status, download the new data.
        machine.add_transition(TR_DownloadNewData, ST_detected_new_data, ST_obtained_new_data,
                               prepare=self.UpdateOrthancStatus.__name__,
                               unless=self.is_Orthanc_Unavailable.__name__,
                               after=self.DownloadNewData.__name__
                               )

        # After checking the zip file status, unpack the new data
        machine.add_transition(TR_UnpackNewData, ST_obtained_new_data, ST_unpacked_new_data,
                               prepare=self.UpdateFileStatus.__name__,
                               unless=self.is_File_Unavailable.__name__,
                               after=self.UnpackNewData.__name__
                               )  # need to check zip file.

        # After checking the unpacked file file status, check the file for MRN
        machine.add_transition(TR_ObtainDICOMMRN, ST_unpacked_new_data, ST_obtained_MRN,
                               prepare=self.UpdateFileStatus.__name__,
                               unless=self.is_File_Unavailable.__name__,
                               after=self.CheckMRN.__name__
                               )  # need to check the content of the zip file success

        # After checking the local DB status, query it for MRN EXISTENCE.
        machine.add_transition(TR_UpdateNewMRNStatus, ST_obtained_MRN, ST_determined_MRN_status,
                               prepare=self.UpdateLocalDBStatus.__name__,
                               unless=self.is_LocalDB_Unavailable.__name__,
                               after=self.CheckLocalDBMRN.__name__
                               )

        # Paired branching transitions
        # Depending on the result of the MRN check, whether it exist previously or not, this is where the decision tree bifurcate
        machine.add_transition(TR_ProcessPatient, ST_determined_MRN_status, ST_processing_old_patient,
                               conditions=self.found_MRN.__name__)
        machine.add_transition(TR_ProcessPatient, ST_determined_MRN_status, ST_processing_new_patient,
                               unless=self.found_MRN.__name__)

        # Old Subject Path.

        # Check if the old subject has already been inserted.
        machine.add_transition(TR_FindInsertionStatus, ST_processing_old_patient, ST_found_insertion_status,
                               prepare=self.UpdateLocalDBStatus.__name__,
                               unless=self.is_LocalDB_Unavailable.__name__,
                               after=self.CheckLocalDBMatchingScanDate.__name__)  # Check if the current subject is already inserted.


        # Paired branching transitions
        # Cycle back to the detected new data with adjusted subjects list. .
        machine.add_transition(TR_ProcessNextSubject, ST_found_insertion_status, ST_determined_orthanc_new_data_status,
                               prepare=self.UpdateOrthancStatus.__name__,
                               conditions=[self.found_matching_scan_date.__name__],
                               unless=self.is_Orthanc_Unavailable.__name__,
                               after=[self.DeleteSubject.__name__, self.CheckOrthancNewData.__name__])  # then do we carry out the deletion process only when 1) scan processd. 2) orthanc reachable.

        # Once all subjects are completed, move on to process the new subjects.
        machine.add_transition(TR_QueryLocalDBForDCCID, ST_found_insertion_status, ST_obtained_DCCID_CNBPID,
                               prepare=[self.UpdateLORISStatus.__name__],
                               unless=[self.is_LORIS_Unavailable.__name__, self.found_matching_scan_date.__name__],
                               after=self.QueryLocalDBForCNBPIDDCCID.__name__)

        # Now we know that this subject was previously seen, and we need to increment the LORIS timepoint to current time point
        machine.add_transition(TR_QueryRemoteUID, ST_obtained_DCCID_CNBPID, ST_checked_remoteSeriesUID,
                               prepare=[self.UpdateLORISStatus.__name__],
                               unless=[self.is_LORIS_Unavailable.__name__],
                               after=self.CheckRemoteTimepoint.__name__)

        machine.add_transition(TR_IncrementRemoteTimepoint, ST_obtained_DCCID_CNBPID, ST_updated_remote_timepoint,
                               prepare=[self.UpdateLORISStatus.__name__],
                               unless=[self.is_LORIS_Unavailable.__name__],
                               after=self.IncrementRemoteTimepoint.__name__)

        # We then need to record this timepoint in the local database. Once this is done, we reached HARMONIZED TIMEPOINT state
        machine.add_transition(TR_IncrementLocalTimepoint, ST_updated_remote_timepoint, ST_harmonized_timepoints,
                               prepare=[self.UpdateLocalDBStatus.__name__],
                               unless=[self.is_LocalDB_Unavailable.__name__],
                               after=self.IncrementLocalTimepoint.__name__)

        # New Subject Path

        # After ensuring the DICOM files are available, Get gender information from DICOM files.
        machine.add_transition(TR_RetrieveGender, ST_processing_new_patient, ST_obtained_new_subject_gender,
                               prepare=[self.UpdateFileStatus.__name__],
                               unless=[self.is_File_Unavailable.__name__],
                               after=self.RetrieveGender.__name__)

        # After ensuring the DICOM files are available, Get birthday information from DICOM files.
        machine.add_transition(TR_RetrieveBirthday, ST_obtained_new_subject_gender, ST_obtained_new_subject_birthday,
                               prepare=[self.UpdateFileStatus.__name__],
                               unless=[self.is_File_Unavailable.__name__],
                               after=self.RetrieveBirthday.__name__)

        # self.machine.add_transition(TR_RetrieveStudy.__name__, "obtained_new_subject_birthday.__name__, "RetrieveStudy.__name__,
        #                            before="UpdateFileStatus.__name__)
        # fixme: this part dynamicly update the project of the DICOM_package.


        # After ensuring LORIS is available, we call the LORIS to create this subject (with default V1 timepoint)
        machine.add_transition(TR_RemoteCreateSubject, ST_obtained_new_subject_birthday, ST_created_remote_subject,
                               prepare=[self.UpdateLORISStatus.__name__],
                               unless=[self.is_LORIS_Unavailable.__name__],
                               after=self.LORISCreateSubject.__name__)

        # After ensuring LocalDB is available, we call the LocalDB to create this subject (with default V1 timepoint)
        machine.add_transition(TR_LocalDBCreateSubject, ST_created_remote_subject, ST_harmonized_timepoints,
                               prepare=[self.UpdateLocalDBStatus.__name__],
                               unless=[self.is_LocalDB_Unavailable.__name__],
                               after=self.LocalDBCreateSubject.__name__)

        # From this point onward, all path are merged:
        # Now loris and LocalDB are up to date, we can start anonymizing the file.
        # Check files are still there before anonymizing it.
        machine.add_transition(TR_AnonymizeFiles, ST_harmonized_timepoints, ST_files_anonymized,
                               prepare=[self.UpdateFileStatus.__name__],
                               unless=[self.is_File_Unavailable.__name__],
                               after=[self.AnonymizeFiles.__name__])

        #BRANCHING CONDITION
        # Check files are still there before zipping it.
        # Also double check for anonymization.
        machine.add_transition(TR_ZipFiles, ST_files_anonymized, ST_files_zipped,
                               prepare=[self.DoubleCheckAnonymization.__name__, self.UpdateFileStatus.__name__],
                               conditions=self.are_anonymized.__name__,
                               unless=[self.is_File_Unavailable.__name__],
                               after=self.ZipFiles.__name__)
        # If failed anonymization check (e.g. file got swapped somwhow? REDO anonymization!
        machine.add_transition(TR_ZipFiles, ST_files_anonymized, ST_harmonized_timepoints,
                               prepare=[self.DoubleCheckAnonymization.__name__, self.UpdateFileStatus.__name__],
                               unless=[self.is_File_Unavailable.__name__, self.are_anonymized.__name__]
                               )

        machine.add_transition(TR_UploadZip, ST_files_zipped, ST_zip_uploaded,
                               prepare=[self.UpdateLORISStatus.__name__],
                               unless=[self.is_LORIS_Unavailable.__name__],
                               after=[self.UploadZip.__name__, self.CheckUploadSuccess.__name__])

        machine.add_transition(TR_InsertSubjectData, ST_zip_uploaded, ST_zip_inserted,
                               prepare=[self.UpdateLORISStatus.__name__],
                               unless=[self.is_LORIS_Unavailable.__name__],
                               after=[self.InsertSubjectData.__name__, self.CheckInsertionSuccess.__name__])

        machine.add_transition(TR_RecordInsertion, ST_zip_inserted, ST_insertion_recorded,
                               prepare=[self.UpdateLocalDBStatus.__name__],
                               unless=[self.is_LocalDB_Unavailable.__name__],
                               after=self.RecordInsertion.__name__)

        machine.add_transition(TR_ResumeMonitoring, ST_insertion_recorded, ST_waiting)

        # Retrying block.
        machine.add_transition(TR_reattempt, [ST_error_orthanc, ST_error_LORIS, ST_error_file_corruption, ST_error_localDB, ST_error_network], "=")

        # Any time, in ANY state, if these check fails, we should go to error state. There might be additional flags in terms situation specific reactions.
        machine.add_transition(TR_DetectedOrthancError, "*", ST_error_orthanc,
                               unless=self.ExceedMaxRetry.__name__,
                               after=self.RetryPreviousActions.__name__)

        machine.add_transition(TR_DetectedLORISError, "*", ST_error_LORIS,
                               unless=self.ExceedMaxRetry.__name__,
                               after=self.RetryPreviousActions.__name__)

        machine.add_transition(TR_DetectedFileError, "*", ST_error_file_corruption,
                               unless=self.ExceedMaxRetry.__name__,
                               after=self.RetryPreviousActions.__name__)


        machine.add_transition(TR_DetectedLocalDBError, "*", ST_error_localDB,
                               unless=self.ExceedMaxRetry.__name__,
                               after=self.RetryPreviousActions.__name__)

        machine.add_transition(TR_DetectedNetworkError, "*", ST_error_network,
                               unless=self.ExceedMaxRetry.__name__,
                               after=self.RetryPreviousActions.__name__)

        # At the end, if all else fails, log, ask for help. Ready for next run.
        # Meatbag state
        machine.add_transition(TR_DetectedOrthancError, "*", ST_human_intervention_required,
                               conditions=self.ExceedMaxRetry.__name__)

        machine.add_transition(TR_DetectedLORISError, "*", ST_human_intervention_required,
                               conditions=self.ExceedMaxRetry.__name__)

        machine.add_transition(TR_DetectedFileError, "*", ST_human_intervention_required,
                               conditions=self.ExceedMaxRetry.__name__)

        machine.add_transition(TR_DetectedLocalDBError, "*", ST_human_intervention_required,
                               conditions=self.ExceedMaxRetry.__name__)

        machine.add_transition(TR_DetectedNetworkError, "*", ST_human_intervention_required,
                               conditions=self.ExceedMaxRetry.__name__)


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
        self.get_graph(**kwargs).draw(stream, prog='dot', format='png')
        output_object = stream.getvalue()
        with open(self.name + ".png", "wb") as png:
            png.write(output_object)



    def GetOrthancList(self):
        logger.info("Transition: Checking Orthanc for new data!")

        # Get updated orthanc UUID.
        self.orthanc_list_all_subjectUUIDs = orthanc.API.get_list_of_subjects(self.orthanc_url, self.orthanc_user, self.orthanc_password)

    def CheckOrthancNewData(self):
        """
        Check if there are new data. Set the proper flag.
        :return:
        """
        # Note this part actually deal with loop back from already inserted situation TOO.
        if self.orthanc_list_all_subjectUUIDs is None or len(self.orthanc_list_all_subjectUUIDs) == 0:
            self.orthanc_has_new_data = False
            logger.info("Orthanc has no new data for us.")
        else:
            self.orthanc_has_new_data = True
            # fixme: for now, only analyze ONE single subject from the Orthanc query.
            self.orthanc_index_current_subject = self.orthanc_index_current_subject + 1
            logger.info("Detected new data on the Orthanc. Commence processing. ")

    def DownloadNewData(self):
        """
        Download the new data for a SINGLE subject. We will return to this state when more subjects exist. Since this state is reached once we confirm there are new data.
        :return:
        """
        logger.info("Transition: Downloading new data now!")

        subject = self.orthanc_list_all_subjectUUIDs[self.orthanc_index_current_subject]

        subject_url = self.orthanc_url + "patients/" + subject + '/archive'  # it must contain patients/ and archive in the path name

        self.DICOM_zip = orthanc.API.get_subject_zip(subject_url, self.orthanc_user, self.orthanc_password)

        # Update the self.files to be scrutinized
        self.files.clear()
        self.files.append(self.DICOM_zip)
        logger.info("Successfully downloaded the data.")


    def DeleteSubject(self):

        # If currently, Orthanc has more than subjects we plan to keep, remove the subject we just checked WHICH we know has already been inserted.
        # Note that THIS does not influnece the list in any ways, It influence Orthanc subjects DIRECTLY.
        if len(self.orthanc_list_all_subjectUUIDs) > self.orthanc_buffer_limit:
            subject_uuid = self.orthanc_list_all_subjectUUIDs[self.orthanc_index_current_subject]
            orthanc.API.delete_subject(subject_uuid)
            logger.info("More subjects exists than the current buffer size. Removing a already downloaded subject before processing next subject. ")

        # Instead of actually deleting the subject, let's try to remove the found subject from the list. This will move the analyses forward.
        # As this is EQUIVALENT of moving the index forward
        del(self.orthanc_list_all_subjectUUIDs[self.orthanc_index_current_subject])
        # Now, the index will refer to the next subject. Also, we can recycle the state/list length check etc.
        #todo: check how the deletion work in a real scenerio.
        logger.info("Mock deleting the subject currently")


    def UnpackNewData(self):
        """
        Properly create the DICOM package.
        :return:
        """
        # Properly set the DICOM_package.
        temporary_folder = orthanc.API.unpack_subject_zip(self.DICOM_zip)
        self.DICOM_package = DICOMPackage(temporary_folder)
        self.DICOM_package.project = "loris" #fixme: this is a place holder. This neeeds to be dyanmiclly updated.

        # Update the self.files to be scrutinized
        self.files.clear()
        self.files = self.DICOM_package.get_dicom_files()
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
            #fixme: add a notifier for this event!
            logger.info("Non-compliant MRN detected! Assigning default placeholder MRN of 9999999")
        else:
            logger.info("Subject specific MRN pass check.")


    def CheckLocalDBMRN(self):
        """
        Check the MRN from the local database.
        :return:
        """
        self.localDB_found_mrn = LocalDB.API.check_MRN(self.DICOM_package.MRN)
        logger.info("Successful checking local database about the MRN")


    def CheckLocalDBMatchingScanDate(self):
        """
        Check scan dates to see if it has already been inserted. This will influence the subsequent check.
        :return:
        """
        # Get DICOM date.
        DICOM_date = self.DICOM_package.scan_date

        # Use DICOM's MRN to get the LocalDB last known scan date, as we previously already know the MRN exist in the database
        LocalDB_date_string = LocalDB.API.get_scan_date(self.DICOM_package.MRN)
        self.last_localDB_scan_date = datetime.datetime.strptime(LocalDB_date_string, "%Y-%m-%d %H:%M:%S")
        logger.info("Last known scan date for this subject was: "+ LocalDB_date_string)

        
        if (DICOM_date == self.last_localDB_scan_date):
            logger.info("Scan date already exist in the database. Data likely already exist. Consider manual intervention. ")
            self.scan_already_processed = True
            # Already processed.
            #self.orthanc_index_current_subject = self.orthanc_index_current_subject + 1
        else:
            # Default path is already it has not been processed.
            self.scan_already_processed = False
            logger.info("Dealing with new potentially subject. Conducting stage 2 test with LORIS visit timepoint check.")


    def CheckRemoteTimepoint(self):
        """
        Check remote scan dates to see if it has already been inserted before. This check helps prevent insertion of previously inserted (but then deleted subject!)
        :return:
        """
        # Get DICOM UID
        DICOM_date = self.DICOM_package.scan_date

        # LORIS API to get a list of VISIT timepoints.

        # For each timepoints, check its list of DICOM tar archives for Series UID.

        # For each timepoints, check its list of DICOM tar archives for Series UID.


        # LORIS API to get a list of DICOM tar archives.

        # Loop
        LORIS_dates = []
        for scan_date in LORIS_dates:
            scan_date = datetime.datetime.strptime(scan_date, "%Y-%m-%d %H:%M:%S")




        # Use DICOM's MRN to get the LocalDB last known scan date, as we previously already know the MRN exist in the database
        LocalDB_date_string = LocalDB.API.get_scan_date(self.DICOM_package.MRN)
        self.last_localDB_scan_date = datetime.datetime.strptime(LocalDB_date_string, "%Y-%m-%d %H:%M:%S")
        logger.info("Last known scan date for this subject was: " + LocalDB_date_string)

        if (DICOM_date == self.last_localDB_scan_date):
            logger.info(
                "Scan date already exist in the database. Data likely already exist. Consider manual intervention. ")
            self.scan_already_processed = True
            # Already processed.
            # self.orthanc_index_current_subject = self.orthanc_index_current_subject + 1
        else:
            # Default path is already it has not been processed.
            self.scan_already_processed = False
            logger.info(
                "Dealing with new potentially subject. Conducting stage 2 test with LORIS visit timepoint check.")

    # Old Subject Path:
    def QueryLocalDBForCNBPIDDCCID(self):

        self.DICOM_package.CNBPID = LocalDB.API.get_CNBP(self.DICOM_package.MRN)

        # Use MRN to retrieve DCCID, update the dicom-package
        self.DICOM_package.DCCID = LocalDB.API.get_DCCID(self.DICOM_package.MRN)

        # Get the latest local known timepoint:
        self.last_localDB_scan_date = LocalDB.API.get_timepoint(self.DICOM_package.MRN)
        logger.info("Last known localDB timepoint: " + self.last_localDB_scan_date)

    def IncrementRemoteTimepoint(self):
        # Using LORIS API to create the new timepoint:
        latest_timepoint = LORIS.API.increment_timepoint(self.DICOM_package.DCCID)
        self.DICOM_package.timepoint = latest_timepoint
        logger.info("Obtained the latest timepoint for the subject from LORIS.")


    def IncrementLocalTimepoint(self):
        # Update the record to use the latest timepoint and the scandate!
        LocalDB.API.set_timepoint(self.DICOM_package.MRN, self.DICOM_package.timepoint)
        LocalDB.API.set_scan_date(self.DICOM_package.MRN, self.DICOM_package.scan_date)
        logger.info("Incremented the local VISIT timepoint for the subject successfully.")


    # New Subject Path:
    def RetrieveGender(self):
        success = self.DICOM_package.update_sex()
        assert success
        logger.info("Subject specific sex pass check.")

        success = self.DICOM_package.update_gender()
        assert success
        logger.info("Subject specific gender pass check.")

    def RetrieveBirthday(self):
        success = self.DICOM_package.update_birthdate()
        assert success
        logger.info("Subject specific birthdate pass check.")

    def RetrieveStudy(self):
        # todo: For now, all project are under LORIS. The projectID etc systems are not being actively used.
        self.DICOM_package.project = "loris"
        # raise NotImplementedError

    def LORISCreateSubject(self):
        # create new PSCID and get DCCID
        success, DCCID, PSCID = LORIS.API.create_new(self.DICOM_package.project,
                                                     self.DICOM_package.birthday,
                                                     self.DICOM_package.gender)
        # Local Variable for anonymization.
        self.DICOM_package.DCCID = DCCID
        self.DICOM_package.CNBPID = PSCID
        self.DICOM_package.timepoint = "V1"  # auto generated.
        logger.info("Creating subject remotely on LORIS is successful.")

    def LocalDBCreateSubject(self):
        # fixme: temporarly disabled this for debugging.
        LocalDB.API.set_CNBP(self.DICOM_package.MRN, self.DICOM_package.CNBPID)
        LocalDB.API.set_DCCID(self.DICOM_package.MRN, self.DICOM_package.DCCID)
        LocalDB.API.set_timepoint(self.DICOM_package.MRN, self.DICOM_package.timepoint)
        LocalDB.API.set_scan_date(self.DICOM_package.MRN, self.DICOM_package.scan_date)
        logger.info("Creating subject locally is successful.")
        pass

    def AnonymizeFiles(self):
        # This will also update self.zipname and self.is_anonymized
        self.DICOM_package.anonymize()
        self.scan_anonymized = self.DICOM_package.is_anonymized

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
        LORIS.API.upload(self.DICOM_package.zip_location)

    def InsertSubjectData(self):
        # Trigger insertion.
        LORIS.API.trigger_insertion(self.DICOM_package.zipname)

    def RecordInsertion(self):
        # Set the completion status to ZERO
        LocalDB.API.set_completion(self.DICOM_package.MRN, 1)

    def CheckUploadSuccess(self):
        # fixme: a script to check upload success is required.
        pass

    def CheckInsertionSuccess(self):
        # fixme a script to check insertion status success is required.
        pass

    def found_matching_scan_date(self):
        return self.scan_already_processed

    # Conditions Method
    def has_new_data (self):
        return self.orthanc_has_new_data

    def found_MRN(self):
        return self.localDB_found_mrn

    def are_anonymized(self):
        return self.scan_anonymized

    def are_inserted(self):
        return self.scan_inserted


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
        from LORIS.API import check_status
        self.STATUS_LORIS = check_status()
        if self.STATUS_LORIS:
            logger.info("LORIS production system status OKAY!")
        else:
            self.TR_DetectedLORISError()

    def UpdateNetworkStatus(self):
        # Ping CNBP frontend server.
        # Ping LORIS server.
        # Ping Google.
        from LORIS.API import check_online_status
        self.STATUS_NETWORK = check_online_status()
        if self.STATUS_NETWORK:
            logger.info("General Network system status OKAY!")
        else:
            self.TR_DetectedNetworkError()

    def UpdateLocalDBStatus(self):
        # Read local db. See if it exist based on the setting.
        from LocalDB.API import check_status
        self.STATUS_LOCALDB = check_status()
        if self.STATUS_LOCALDB:
            logger.info("LocalDB system status OKAY!")
        else:
            self.TR_DetectedLocalDBError()


    def UpdateOrthancStatus(self):
        # Check ENV for the predefined Orthanc URL to ensure that it exists.
        from orthanc.API import check_status
        self.STATUS_ORTHANC = check_status()
        if self.STATUS_ORTHANC:
            logger.info("Orthanc system status OKAY!")
        else:
            self.TR_DetectedOrthancError()


    def UpdateFileStatus(self):
        # Ensure the file provided exist.
        # NOTE: this does not check if the valid is the right is CORRECT!
        for file in self.files:
            if os.path.exists(file) and os.path.isfile(file):
                continue
            else:
                self.STATUS_FILE = False
                self.TR_DetectedFileError()
        self.STATUS_FILE = True
        logger.info("File(s) status APPEAR OKAY!")


    # Meta methods todo
    def RetryPreviousActions(self):
        pass

    def trigger_wrap(self, transition_name):
        # A wrapped call to the machine trigger function.
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
            logger.info(function_name +" not found")


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
        if self.retry >= self.max_retry:
            return True
        else:
            return False

    def SaveStatusToDisk(self):

        raise NotImplementedError


if __name__ == "__main__":

    # Periodically trigger this:
    cmd_folder = os.path.realpath(
        os.path.dirname(
            os.path.abspath(os.path.split(inspect.getfile(inspect.currentframe()))[0])))

    if cmd_folder not in sys.path:
        sys.path.insert(0, cmd_folder)

    current_import_process = DICOMTransitImport()
    current_import_process.setup_machine()



    # System initialization check.
    current_import_process.UpdateOrthancStatus()
    current_import_process.UpdateNetworkStatus()
    current_import_process.UpdateLocalDBStatus()
    current_import_process.UpdateLORISStatus()

    # From this point onward, going to assume, they remain the same for the duration of the transaction.
    # Current system is NOT robust enough to deal with mid interruption. It will just trigger failed insertion to try again.

    #Import1.show_graph()

    # current_import.waiting is the default state.


    # Execute the following every 10 mintes:
    # fixme: disable transition error. Let silent fail.

    monitoring=True

    # This variable controls whether in this loop, we are processing new data or just processing existing data.
    # This controls whether "orthanc_list_all_subjectUUIDs" list get updated from Orthanc or not.
    check_new_data = True

    while monitoring:
        try:
            # Initialial state MUST be waiting:


            if(check_new_data):
                current_import_process.trigger_wrap(TR_UpdateOrthancNewDataStatus)

            # Need to loop back here.
            if current_import_process.has_new_data():
                current_import_process.trigger_wrap(TR_HandlePotentialOrthancData)
                current_import_process.trigger_wrap(TR_DownloadNewData)
                current_import_process.trigger_wrap(TR_UnpackNewData)
                current_import_process.trigger_wrap(TR_ObtainDICOMMRN)
                current_import_process.trigger_wrap(TR_UpdateNewMRNStatus)
            else:
                current_import_process.trigger_wrap(TR_HandlePotentialOrthancData)
                # that previous statement will transition to waiting state.
                continue

            current_import_process.trigger_wrap(TR_ProcessPatient)

            if current_import_process.found_MRN():
                # old patients path
                current_import_process.trigger_wrap(TR_FindInsertionStatus)
                if current_import_process.found_matching_scan_date():
                    current_import_process.trigger_wrap(TR_ProcessNextSubject)
                    # Need to loop back based on the beginning BUT not get new data.
                    check_new_data = False
                    continue
                else:
                    current_import_process.trigger_wrap(TR_QueryLocalDBForDCCID)
                    current_import_process.trigger_wrap(TR_IncrementRemoteTimepoint)
                    current_import_process.trigger_wrap(TR_IncrementLocalTimepoint)
            else:
                # new patient path
                current_import_process.trigger_wrap(TR_RetrieveGender)
                current_import_process.trigger_wrap(TR_RetrieveBirthday)
                current_import_process.trigger_wrap(TR_RemoteCreateSubject)
                current_import_process.trigger_wrap(TR_LocalDBCreateSubject)

            current_import_process.trigger_wrap(TR_AnonymizeFiles)

            current_import_process.trigger_wrap(TR_ZipFiles)
            # If anonymization fails, loop back.

            current_import_process.trigger_wrap(TR_UploadZip)
            current_import_process.trigger_wrap(TR_InsertSubjectData)
            current_import_process.trigger_wrap(TR_RecordInsertion)
            current_import_process.trigger_wrap(TR_ResumeMonitoring)
            logger.info("One insertion cycle complete. Sleeping 30s before checking next cycle.")
            time.sleep(30)

        except MachineError as e:

            logger.warning("A finite state machine state transition has FAILED. Check the log and error message")
            logger.warning("Error Message Encountered:")
            logger.warning(e)
            from settings import get
            zip_path = get("zip_storage_location")
            name_log = os.path.join(zip_path,"StateMachineDump_"+unique_name()+".pickle")
            with open(name_log, 'wb') as f:
                # Pickle the 'data' dictionary using the highest protocol available.
                pickle.dump(current_import_process.machine, f, pickle.HIGHEST_PROTOCOL)
            logger.warning("A finite state machine pickle dump has been made at " + name_log)
            logger.warning("Check that path for more detail. ")
            #current_import_process.to_waiting()