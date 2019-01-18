import os, sys, inspect, io
import datetime
import logging
from transitions import Machine
from transitions import MachineError
#from transitions.extensions import GraphMachine as Machine
import DICOM.API
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

class DICOMTransitImport(object):
    # These are the plausible major steps within a DICOMTransitImport process.
    states = [
        "waiting",
            
        # Orthanc related:
        "determined_orthanc_new_data_status",
        "detected_new_data",
        "obtained_new_data",

        # File related:
        "unpacked_new_data",
        "obtained_MRN",
        "determined_MRN_status",

        # Main analyses path:
        "processing_old_patient",
        "processing_new_patient",

        # Existing patient path.
        "ensured_only_new_subjects_remain",
        "obtained_DCCID_CNBPID",
        "updated_LORIS_timepoint",

        #"updated_remote_timepoint",

        # New patient path.
        "obtained_new_subject_gender",
        "obtained_new_subject_birthday",
        #"obtained_new_subject_study",
        "created_remote_subject",

        "harmonized_timepoints",
        "files_anonymized",
        "files_zipped",
        "zip_uploaded",
        "zip_inserted",

        "retry",
        "error_orthanc",
        "error_LORIS",
        "error_file_corruption",
        "error_sqlite",
        "error_network",
        "human_intervention_required",
    ]

    # Status indicator whether they are reachable/online
    STATUS_ORTHANC = False
    STATUS_LORIS = False
    STATUS_NETWORK = False
    STATUS_FILE = False
    STATUS_LOCALDB = False

    orthanc_has_new_data = False
    localDB_found_mrn = None
    scan_already_processed = True
    scan_anonymized = False
    scan_inserted = False

    orthanc_index_current_subject = 0
    orthanc_list_all_subjects = []

    # The full path to the zip file downloaded
    DICOM_zip = None
    DICOM_package = None

    # This is the list of the files that are constantly being monitored and checked if reachable. It is dynamicly updated through out the analyses process. It can be a list of zip files, or a single zip file. It respresents the local file resources that CONSTANTLY needs to be monitored to ensure no fault occurs.
    files = []

    machine = None
    retry = 0
    max_retry = 5

    def __init__(self):

        self.states_last = []

        # Timestamp
        self.time = datetime.datetime.now()

        self.retry = 0
        self.scan_anonymized = False

        # We shall name this with
        self.name = self.time.isoformat().replace(":","")

        self.url, self.user, self.password = orthanc.API.get_prod_orthanc_credentials()

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

        machine.add_transition("TR_UpdateOrthancNewDataStatus", "waiting", "determined_orthanc_new_data_status",
                               prepare="UpdateOrthancStatus",
                               unless="is_Orthanc_Unavailable",
                               after="CheckOrthancNewData")  # this will set the


        # Paired branching transitions
        machine.add_transition("TR_HandlePotentialOrthancData", "determined_orthanc_new_data_status", "waiting",
                               unless="has_new_data")
        machine.add_transition("TR_HandlePotentialOrthancData", "determined_orthanc_new_data_status", "detected_new_data",
                               prepare="UpdateOrthancStatus",
                               unless="is_Orthanc_Unavailable",
                               conditions="has_new_data")



        machine.add_transition("TR_DownloadNewData", "detected_new_data", "obtained_new_data",
                               prepare="UpdateOrthancStatus",
                               unless="is_Orthanc_Unavailable",
                               # note that we typically ENTER the state first BEFORE applying the action. Therefore, the AFTER action MUST SUCCEED.
                               after="DownloadNewData",  # "UpdateFileStatus"
                               )

        machine.add_transition("TR_UnpackNewData", "obtained_new_data", "unpacked_new_data",
                               prepare="UpdateFileStatus",
                               unless="is_File_Unavailable",
                               after="UnpackNewData"
                               )  # need to check zip file.

        machine.add_transition("TR_ObtainDICOMMRN", "unpacked_new_data", "obtained_MRN",
                               prepare="UpdateFileStatus",
                               unless="is_File_Unavailable",
                               after="CheckMRN"
                               )  # need to check the content of the zip file success

        machine.add_transition("TR_UpdateNewMRNStatus", "obtained_MRN", "determined_MRN_status",
                               prepare="UpdateLocalDBStatus",
                               unless="is_LocalDB_Unavailable",
                               after="CheckLocalDBMRN"
                               )

        # Paired branching transitions
        # Depending on the result of the MRN check, whether it exist previously or not, this is where the decision tree bifurcate
        machine.add_transition("TR_ProcessPatient", "determined_MRN_status", "processing_old_patient",
                               conditions="found_MRN")
        machine.add_transition("TR_ProcessPatient", "determined_MRN_status", "processing_new_patient",
                               unless="found_MRN")

        # Old Subject Path.

        # Cycle back to the detected new data with INCREMENTED COUNTER.
        machine.add_transition("TR_DeleteSubject", "processing_old_patient", "detected_new_data",
                               prepare="UpdateProcessStatus",  # Check if the current subject is already inserted.
                               conditions="are_scans_processed",
                               # and only if it is inserted, fixme: check what this is about!
                               after="DeleteSubject")  # then do we carry out the deletion process.

        # Once all subjects are completed, move on to process the new subjects.
        machine.add_transition("TR_DeleteSubject", "processing_old_patient", "ensured_only_new_subjects_remain",
                               prepare="UpdateProcessStatus",  # Check if the current subject is already inserted.
                               unless="are_scans_processed",
                               # and only if it is inserted, fixme: check what this is about!
                               )  # then do we carry out the deletion process.

        machine.add_transition("TR_RetrieveCNBPIDDCCID", "ensured_only_new_subjects_remain", "obtained_DCCID_CNBPID",
                               prepare=["UpdateLORISStatus"],
                               unless=["is_LORIS_Unavailable"],
                               after="RetrieveCNBPIDDCCID")

        machine.add_transition("TR_IncrementRemoteTimepoint", "obtained_DCCID_CNBPID", "updated_LORIS_timepoint",
                               prepare=["UpdateLORISStatus"],
                               unless=["is_LORIS_Unavailable"],
                               after="IncrementRemoteTimepoint")

        machine.add_transition("TR_IncrementLocalTimepoint", "updated_LORIS_timepoint", "harmonized_timepoints",
                               prepare=["UpdateLocalDBStatus"],
                               unless=["is_LocalDB_Unavailable"],
                               after="IncrementRemoteTimepoint")

        # New Subject Path

        machine.add_transition("TR_RetrieveGender", "processing_new_patient", "obtained_new_subject_gender",
                               prepare=["UpdateFileStatus"],
                               unless=["is_File_Unavailable"],
                               after="RetrieveGender")

        machine.add_transition("TR_RetrieveBirthday", "obtained_new_subject_gender", "obtained_new_subject_birthday",
                               prepare=["UpdateFileStatus"],
                               unless=["is_File_Unavailable"],
                               after="RetrieveBirthday")

        # self.machine.add_transition("TR_RetrieveStudy", "obtained_new_subject_birthday", "RetrieveStudy",
        #                            before="UpdateFileStatus")
        # fixme: this part dynamicly update the project of the DICOM_package.

        machine.add_transition("TR_LORISCreateSubject", "obtained_new_subject_birthday", "created_remote_subject",
                               prepare=["UpdateLORISStatus"],
                               unless=["is_LORIS_Unavailable"],
                               after="LORISCreateSubject")

        machine.add_transition("TR_LocalDBCreateSubject", "created_remote_subject", "harmonized_timepoints",
                               prepare=["UpdateLocalDBStatus"],
                               unless=["is_LocalDB_Unavailable"],
                               after="LocalDBCreateSubject")

        # From this point onward, all path are merged:

        machine.add_transition("TR_AnonymizeFiles", "harmonized_timepoints", "files_anonymized",
                               prepare=["UpdateFileStatus"],
                               unless=["is_File_Unavailable"],
                               after=["AnonymizeFiles"])

        machine.add_transition("TR_ZipFiles", "files_anonymized", "files_zipped",
                               prepare=["DoubleCheckAnonymization", "UpdateFileStatus"],
                               conditions="are_anonymized",
                               unless=["is_File_Unavailable"],
                               after="ZipFiles")

        machine.add_transition("TR_UploadZip", "files_zipped", "zip_uploaded",
                               prepare=["UpdateLORISStatus"],
                               unless=["is_LORIS_Unavailable"],
                               after=["UploadZip", "CheckUploadSuccess"])

        machine.add_transition("TR_InsertSubjectData", "zip_uploaded", "zip_inserted",
                               prepare=["UpdateLORISStatus"],
                               unless=["is_LORIS_Unavailable"],
                               after=["InsertSubjectData", "CheckInsertionSuccess"])

        machine.add_transition("TR_RecordInsertion", "zip_inserted", "waiting",
                               prepare=["UpdateLocalDBStatus"],
                               unless=["is_LocalDB_Unavailable"],
                               after="RecordInsertion")

        # Retrying block.
        machine.add_transition("TR_reattempt",
                               ["error_orthanc", "error_LORIS", "error_file_corruption", "error_localDB",
                                "error_network"], "=")

        # Any time, in ANY state, if these check fails, we should go to error state. There might be additional flags in terms situation specific reactions.
        machine.add_transition("TR_DetectedOrthancError", "*", "error_orthanc",
                               unless="ExceedMaxRetry")

        machine.add_transition("TR_DetectedLORISError", "*", "error_LORIS",
                               unless="ExceedMaxRetry")

        machine.add_transition("TR_DetectedFileError", "*", "error_file_corruption",
                               unless="ExceedMaxRetry")

        machine.add_transition("TR_DetectedLocalDBError", "*", "error_localDB",
                               unless="ExceedMaxRetry")

        machine.add_transition("TR_DetectedNetworkError", "*", "error_network",
                               unless="ExceedMaxRetry")

        # At the end, if all else fails, log, ask for help. Ready for next run.
        # Meatbag state
        machine.add_transition("TR_DetectedOrthancError", "*", "human_intervention_required",
                               conditions="ExceedMaxRetry")

        machine.add_transition("TR_DetectedLORISError", "*", "human_intervention_required",
                               conditions="ExceedMaxRetry")

        machine.add_transition("TR_DetectedFileError", "*", "human_intervention_required",
                               conditions="ExceedMaxRetry")

        machine.add_transition("TR_DetectedLocalDBError", "*", "human_intervention_required",
                               conditions="ExceedMaxRetry")

        machine.add_transition("TR_DetectedNetworkError", "*", "human_intervention_required",
                               conditions="ExceedMaxRetry")
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
        object = stream.getvalue()
        with open(self.name + ".png", "wb") as png:
            png.write(object)

    def CheckOrthancNewData(self):
        """
        Check if there are new data. Set the proper flag.
        :return:
        """
        logger.info("Transition: Checking orthanc for new data!")

        # fixme: authentication issue.
        self.orthanc_list_all_subjects = orthanc.API.get_list_of_subjects(self.url, self.user, self.password)
        if self.orthanc_list_all_subjects is None or len(self.orthanc_list_all_subjects) == 0:
            self.orthanc_has_new_data = False
            logger.info("Orthanc has no new data for us.")
        else:
            self.orthanc_has_new_data = True
            # fixme: for now, only analyze ONE single subject from the Orthanc query.
            self.orthanc_index_current_subject = self.orthanc_index_current_subject + 1
            logger.info("Detected new data on the orthanc. Commence processing. ")

    def DownloadNewData(self):
        """
        Download the new data for a SINGLE subject. We will return to this state when more subjects exist. Since this state is reached once we confirm there are new data.
        :return:
        """
        logger.info("Transition: Downloading new data now!")
        subject = self.orthanc_list_all_subjects[self.orthanc_index_current_subject]
        subject_url = self.url + "patients/" + subject + '/archive'  # it must contain patients/ and archive in the path name

        self.DICOM_zip = orthanc.API.get_subject_zip(subject_url, self.user, self.password)

        # Update the self.files to be scrutinized
        self.files.clear()
        self.files.append(self.DICOM_zip)
        logger.info("Successfully downloaded the data.")

    def DeleteSubject(self):
        self.orthanc_index_current_subject=self.orthanc_index_current_subject+1
        logger.info("Mock deleting the subject currently") #fixme: use real api calls here to delete.


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
        else:
            logger.info("Subject specific MRN pass check.")


    def CheckLocalDBMRN(self):
        """
        Check the MRN from the local database.
        :return:
        """
        self.localDB_found_mrn = LocalDB.API.check_MRN(self.DICOM_package.MRN)
        logger.info("Successful checking local database about the MRN")

    def UpdateProcessStatus(self):

        # Intervention block: Check scan dates to see if they have already been inserted.
        DICOM_date = self.DICOM_package.scan_date

        API_date_string = LocalDB.API.get_scan_date(self.DICOM_package.MRN)

        LocalDB_date = datetime.datetime.strptime(API_date_string, "%Y-%m-%d %H:%M:%S")

        if (DICOM_date == LocalDB_date):
            logger.info("Scan date already exist in the database. Data likely already exist. Consider manual intervention. ")
            self.scan_already_processed = True
            # Already processed.
            self.orthanc_index_current_subject = self.orthanc_index_current_subject + 1
            # Goto download new data
            self.TR_DownloadNewData()
        else:
            # Default path is already it has not been processed.
            self.scan_already_processed = False
            logger.info("Dealing with new subject.")

    # Old Subject Path:
    def RetrieveCNBPIDDCCID(self):

        self.DICOM_package.CNBPID = LocalDB.API.get_CNBP(self.DICOM_package.MRN)

        # Use MRN to retrieve DCCID, update the dicom-package
        self.DICOM_package.DCCID = LocalDB.API.get_DCCID(self.DICOM_package.MRN)

        # Get the latest local known timepoint:
        #self.last_database_timepoint = LocalDB.API.get_timepoint(self.DICOM_package.MRN)
        #logger.info("Last known timepoint: " + self.last_database_timepoint)

    def obtained_DCCID_CNBPID(self):
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
        #LocalDB.API.set_CNBP(self.DICOM_package.MRN, self.DICOM_package.CNBPID)
        #LocalDB.API.set_DCCID(self.DICOM_package.MRN, self.DICOM_package.DCCID)
        #LocalDB.API.set_timepoint(self.DICOM_package.MRN, self.DICOM_package.timepoint)
        #LocalDB.API.set_scan_date(self.DICOM_package.MRN, self.DICOM_package.scan_date)
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

    def are_scans_processed(self):
        return self.scan_already_processed

    # Conditions Method
    def has_new_data(self):
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

    try:
        current_import_process.TR_UpdateOrthancNewDataStatus()

        if current_import_process.has_new_data():
            current_import_process.TR_HandlePotentialOrthancData()
            current_import_process.TR_DownloadNewData()
            current_import_process.TR_UnpackNewData()
            current_import_process.TR_ObtainDICOMMRN()
            current_import_process.TR_UpdateNewMRNStatus()
        else:
            current_import_process.TR_HandlePotentialOrthancData()

        current_import_process.TR_ProcessPatient()

        if current_import_process.found_MRN():
            # old patients path

            while current_import_process.are_scans_processed():
                current_import_process.TR_DeleteSubject()

            current_import_process.TR_RetrieveCNBPIDDCCID()
            current_import_process.TR_IncrementRemoteTimepoint()
            current_import_process.TR_IncrementLocalTimepoint()

        else:
            # new patient path
            current_import_process.TR_RetrieveGender()
            current_import_process.TR_RetrieveBirthday()
            current_import_process.TR_LORISCreateSubject()
            current_import_process.TR_LocalDBCreateSubject()

        current_import_process.TR_AnonymizeFiles()
        current_import_process.TR_ZipFiles()
        current_import_process.TR_UploadZip()
        current_import_process.TR_InsertSubjectData()
        current_import_process.TR_RecordInsertion()
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