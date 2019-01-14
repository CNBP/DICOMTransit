import os, sys, inspect, io
import datetime
import logging
from transitions import *
from transitions.extensions import GraphMachine as Machine
import DICOM.API
import orthanc.API
import LORIS.API
import LocalDB.API
from DICOM.DICOMPackage import DICOMPackage

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('transition').setLevel(logging.INFO)

"""
HasNewData = Method
has_new_data = Variable. 
STATUS_NETWORK = status binary variable. 

"""

class DICOMTransitImport(object):

    # These are the plausible major steps within a DICOMTransitImport process.
    states = [
        "waiting",

        "obtained_MRN",

        # Orthanc related:
        "detected_new_data",
        "obtained_new_data",

        # File related:
        "unpacked_new_data",
        "obtained_MRN",

        # Main analyses path:
        "processing_old_patient",
        "processing_new_patient",

        # Existing patient path.
        "obtained_LocalDB_timepoint",
        "updated_LocalDB_timepoint",
        #"updated_remote_timepoint",

        # New patient path.
        "obtained_new_subject_gender",
        "obtained_new_subject_birthday",
        #"obtained_new_subject_study",
        "created_remote_subject",
        "created_local_subject",
        "updated_LORIS_timepoint",

        "retry0",
        "retry1",
        "retry2",
        "retry3",
        "retry4",
        "retry5",
        "retry6",
        "retry7",
        "retry8",
        "retry9",

        "files_anonymized",
        "files_zipped",
        "zip_uploaded",
        "zip_inserted",


    ]


    """
    # Errors:
    "error_orthanc",
    "error_LORIS",
    "error_file_corruption",
    "error_sqlite",
    "error_network",
    "human_intervention_required",
    """

    # trigger, source, destination
    actions = [
        ['CheckMRIScanner', 'waiting', 'detected_new_data'],
    ]

    # Status indicator whether they are reachable/online
    STATUS_ORTHANC = False
    STATUS_LORIS = False
    STATUS_NETWORK = False
    STATUS_FILE = False
    STATUS_LOCALDB = False

    orthanc_has_new_data = False
    localDB_found_mrn = None
    no_localDB_mrn = None
    scan_already_processed = True
    are_anonymized = False
    are_inserted = False

    orthanc_index_current_subject = 0
    orthanc_list_all_subjects = []

    DICOM_zip = None
    DICOM_package = None

    def __init__(self, name):



        # Timestamp
        self.time = datetime.datetime.now()

        # New Data Status:


        # We shall name this with
        self.name = self.time.isoformat()

        self.url, self.user, self.password = orthanc.API.get_prod_orthanc_credentials()


        # Initialize the state machine
        self.machine = Machine(model=self,
                               states=DICOMTransitImport.states,
                               transitions=DICOMTransitImport.actions,
                               #transitions=None,
                               auto_transitions=False,
                               show_auto_transitions=True,
                               title="Import Process is Messy",
                               show_conditions=True,
                               initial="waiting")

        #Transitions:

        # Check orthanc for new data, if has new data, proceed to the next stage. Else, no stage transition happen.
        self.machine.add_transition(trigger="CheckOrthancNewData", source="waiting", dest="detected_new_data",
                                    conditions="HasNewData", before="CheckOrthanc")

        #
        self.machine.add_transition("DownloadNewData", "detected_new_data", "obtained_new_data",
                                    before="CheckOrthanc", after="CheckFile")

        self.machine.add_transition("UnpackNewData", "obtained_new_data", "unpacked_new_data",
                                    before="CheckFile")  # need to check zip file.

        self.machine.add_transition("CheckMRN", "unpacked_new_data", "obtained_MRN",
                                    before=["CheckFile", "CheckLocalDB"], after="CheckLocalDBMRN") # # need to check the content of the zip file success

        # Depending on the result of the MRN check, whether it exist previously or not, this is where the decision tree bifurcate
        self.machine.add_transition("ProcessPatient", "obtained_MRN", "processing_old_patient",
                                    conditions="Found_MRN", after="CheckAlreadyInsert")
        self.machine.add_transition("ProcessPatient", "obtained_MRN", "processing_new_patient",
                                    conditions="NoPreviousMRN")

        # Old Subject Path.

        # Cycle used to delet all non-essential subjects already processed.
        self.machine.add_transition("DeleteSubject", "processing_old_patient", "=",
                                    before="CheckOrthanc", conditions="CheckExistingScan", after="CheckAlreadyInsert")


        self.machine.add_transition("RetrieveCNBPIDDCCID", "processing_old_patient", "obtained_DCCID_CNBPID",
                                    before=["CheckNetwork", "CheckLORIS"])

        self.machine.add_transition("IncrementRemoteTimepoint", "obtained_DCCID_CNBPID", "updated_LORIS_timepoint",
                                    before=["CheckNetwork", "CheckLORIS"])

        self.machine.add_transition("IncrementLocalTimepoint", "updated_LORIS_timepoint", "harmonized_timepoints",
                                    before="CheckLocalDB")



        # New Subject Path

        self.machine.add_transition("RetrieveGender", "processing_new_patient", "obtained_new_subject_gender",
                                    before="CheckFile")
        self.machine.add_transition("RetrieveBirthday", "obtained_new_subject_gender", "obtained_new_subject_birthday",
                                    before="CheckFile")
        #self.machine.add_transition("RetrieveStudy", "obtained_new_subject_birthday", "RetrieveStudy",
        #                            before="CheckFile")
        self.machine.add_transition("CreateLORISSubject", "obtained_new_subject_birthday", "created_remote_subject",
                                    before=["CheckNetwork", "CheckLORIS"])
        self.machine.add_transition("CreateLocalSubject", "created_remote_subject", "harmonized_timepoints",
                                    before="CheckLocalDB")

        # From this point onward, all path are merged:

        self.machine.add_transition("AnonymizeFiles", "harmonized_timepoints", "files_anonymized",
                                    before="CheckFile", after="DoubleCheckAnonymization")
        self.machine.add_transition("ZipFiles", "files_anonymized", "files_zipped",
                                    conditions="AreAnonymized", before="CheckFiles", after="CheckFiles")
        self.machine.add_transition("UploadZip", "files_zipped", "zip_uploaded",
                                    before=["CheckNetwork", "CheckLORIS"], after="CheckUploadSuccess")
        self.machine.add_transition("InsertSubjectData", "zip_uploaded", "zip_inserted",
                                    before=["CheckNetwork", "CheckLORIS"], after="CheckInsertion")
        self.machine.add_transition("RecordInsertion", "zip_inserted", "waiting",
                                    conditions="AreInserted", before=["CheckNetwork", "CheckLORIS"])

        # Retrying block.
        self.machine.add_transition("reattempt", ["error_orthanc", "error_LORIS", "error_file_corruption", "error_localDB", "error_network"], "=")

        # Any time, in ANY state, if these check fails, we should go to error state. There might be additional flags in terms situation specific reactions.
        self.machine.add_transition("CheckOrthanc",         "*", "error_orthanc",           conditions="is_Orthanc_Unavailable")
        self.machine.add_transition("CheckLORIS",           "*", "error_LORIS",             conditions="is_LORIS_Unavailable")
        self.machine.add_transition("CheckFile",  "*", "error_file_corruption",   conditions="is_File_Unavailable")
        self.machine.add_transition("CheckLocalDB",         "*", "error_localDB",           conditions="is_LocalDB_Unavailable")
        self.machine.add_transition("CheckNetwork",         "*", "error_network",           conditions="is_Network_Unavailable")


        # At the end, if all else fails, log, ask for help. Ready for next run.
        self.machine.add_transition("AskMeatBagsForHelp", "*", "human_intervention_required")


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

        # fixme: authentication issue.
        self.orthanc_list_all_subjects = orthanc.API.get_list_of_subjects_noauth(self.url)
        if self.orthanc_list_all_subjects is None or len(self.orthanc_list_all_subjects) == 0:
            self.orthanc_has_new_data = False
        else:
            self.orthanc_has_new_data = True
            # fixme: for now, only analyze ONE single subject from the Orthanc query.
            self.orthanc_index_current_subject = self.orthanc_index_current_subject + 1

    def DownloadNewData(self):
        """
        Download the new data. Since this state is reached once we confirm there are new data.
        :return:
        """
        subject = self.orthanc_list_all_subjects[self.orthanc_index_current_subject]
        subject_url = self.url + "patients/" + subject + '/archive'  # it must contain patients/ and archive in the path name

        # fixme: Authentication issue
        self.DICOM_zip = orthanc.API.get_subject_zip(subject_url, self.user, self.password)

    def UnpackNewData(self):
        """
        Properly create the DICOM package.
        :return:
        """
        # Properly set the DICOM_package.
        self.DICOM_package = DICOMPackage(self.DICOM_zip)

    def CheckMRN(self):
        """
        Check the MRN from the file.
        :return:
        """
        # Update some of the key process related to the DICOM_packages that have just been created.
        success = self.DICOM_package.update_MRN()
        assert success
        logger.info("Subject specific MRN pass check.")


    def ProcessPatient(self):
        logger.info("We are now entering the processing stage. ")
        pass

    def CheckLocalDBMRN(self):
        """
        Check the MRN from the local database.
        :return:
        """
        self.localDB_found_mrn = LocalDB.API.check_MRN(self.DICOM_package.MRN)
        self.no_localDB_mrn = not LocalDB.API.check_MRN(self.DICOM_package.MRN)

    def CheckAlreadyInsert(self):

        # Intervention block: Check scan dates to see if they have already been inserted.
        DICOM_date = self.DICOM_package.scan_date

        API_date_string = LocalDB.API.get_scan_date(self.DICOM_package.MRN)

        LocalDB_date = datetime.datetime.strptime(API_date_string, "%Y-%m-%d %H:%M:%S")

        if (DICOM_date == LocalDB_date):
            print("Scan date already exist in the database. Data likely already exist. Consider manual intervention. ")
            self.scan_already_processed = True
            # Already processed.
            self.orthanc_index_current_subject = self.orthanc_index_current_subject + 1
        else:
            # Default path is already it has not been processed.
            self.scan_already_processed = False

    def DeleteSubject(self):
        # fixme: need to actually delete the subject
        # orthanc.API.remove

        logger.warning("MOCK deleting the subject currently!")


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


    def IncrementLocalTimepoint(self):
        # Update the record to use the latest timepoint and the scandate!
        LocalDB.API.set_timepoint(self.DICOM_package.MRN, self.DICOM_package.timepoint)
        LocalDB.API.set_scan_date(self.DICOM_package.MRN, self.DICOM_package.scan_date)

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
        #raise NotImplementedError
        # todo: For now, all project are under LORIS. The projectID etc systems are not being actively used.
        self.DICOM_package.project = "loris"

    def CreateLORISSubject(self):
        # create new PSCID and get DCCID
        success, DCCID, PSCID = LORIS.API.create_new(self.DICOM_package.project,
                                                     self.DICOM_package.birthday,
                                                     self.DICOM_package.gender)
        # Local Variable for anonymization.
        self.DICOM_package.DCCID = DCCID
        self.DICOM_package.CNBPID = PSCID
        self.DICOM_package.timepoint = "V1"  # auto generated.

    def CreateLocalSubject(self):
        LocalDB.API.set_CNBP(self.DICOM_package.MRN, self.DICOM_package.CNBPID)
        LocalDB.API.set_DCCID(self.DICOM_package.MRN, self.DICOM_package.DCCID)
        LocalDB.API.set_timepoint(self.DICOM_package.MRN, self.DICOM_package.timepoint)
        LocalDB.API.set_scan_date(self.DICOM_package.MRN, self.DICOM_package.scan_date)

    def AnonymizeFiles(self):
        pass
    def ZipFiles(self):
        pass
    def UploadZip(self):
        pass
    def InsertSubjectData(self):
        pass
    def RecordInsertion(self):
        pass

    def CheckExistingScan(self):
        return self.scan_already_processed

    # Conditions Method
    def HasNewData(self):
        return self.orthanc_has_new_data

    def Found_MRN(self):
        return self.localDB_found_mrn

    def NoPreviousMRN(self):
        return self.no_localDB_mrn

    def AreAnonymized(self):
        return self.are_anonymized

    def AreInserted(self):
        return self.are_inserted


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
    def CheckLORIS(self):

        self.STATUS_NETWORK = self.CheckNetwork()

        # Return false if network is down.
        if not self.STATUS_NETWORK:
            self.STATUS_LORIS = self.STATUS_NETWORK

        # Ping LORIS production server to check if it is online.
        from LORIS.API import check_status
        self.STATUS_LORIS = check_status()

    def CheckNetwork(self):
        # Ping CNBP frontend server.
        # Ping LORIS server.
        # Ping Google.
        from LORIS.API import check_online_status
        self.STATUS_NETWORK = check_online_status()

    def CheckLocalDB(self):
        # Read local db. See if it exist based on the setting.
        from LocalDB.API import check_status
        self.STATUS_LOCALDB = check_status()

    def CheckFile(self, file_path):
        # Ensure the file provided exist.
        # NOTE: this does not check if the valid is the right is CORRECT!
        if os.path.exists(file_path) and os.path.isfile(file_path):
            return True
        else:
            return False

    def CheckOrthanc(self):
        # Check ENV for the predefined Orthanc URL to ensure that it exists.
        from orthanc.API import check_status
        self.STATUS_ORTHANC = check_status()


    # Meta methods todo
    def SaveStatusToDisk(self):

        raise NotImplementedError


if __name__ == "__main__":

    # Periodically trigger this:
    cmd_folder = os.path.realpath(
        os.path.dirname(
            os.path.abspath(os.path.split(inspect.getfile(inspect.currentframe()))[0])))

    if cmd_folder not in sys.path:
        sys.path.insert(0, cmd_folder)

    Import1 = DICOMTransitImport("2019")
    Import1.CheckOrthanc()
    Import1.DownloadNewData()
    Import1.UnpackNewData()
    Import1.CheckMRN()
    Import1.CheckLocalDBMRN()

    Import1.RetrieveCNBPIDDCCID()
    Import1.obtained_DCCID_CNBPID()
    Import1.IncrementRemoteTimepoint()

    Import1.RetrieveGender()
    Import1.RetrieveBirthday()
    Import1.CreateLORISSubject()
    Import1.CreateLocalSubject()
    Import1.IncrementRemoteTimepoint()

    Import1.AnonymizeFiles()
    Import1.ZipFiles()
    Import1.UploadZip()
    Import1.InsertSubjectData()
    Import1.RecordInsertion()






    pass