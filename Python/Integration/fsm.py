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
logging.getLogger('transition').setLevel(logging.INFO)

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
        "harmonized_timepoints",

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

    has_new_data = False
    found_mrn = None
    no_previous_mrn = None
    are_anonymized = False
    are_inserted = False

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
                                    before="CheckFile") # need to check zip file.

        self.machine.add_transition("CheckMRN", "unpacked_new_data", "obtained_MRN",
                                    before="CheckFile") # # need to check the content of the zip file success

        # Depending on the result of the MRN check, whether it exist previously or not, this is where the decision tree bifurcate
        self.machine.add_transition("CheckLocalDBMRN", "obtained_MRN", "processing_old_patient",
                                    conditions="Found_MRN", before="CheckLocalDB")
        self.machine.add_transition("CheckLocalDBMRN", "obtained_MRN", "processing_new_patient",
                                    conditions="NoPreviousMRN", before="CheckLocalDB")

        # Old Subject Path.
        self.machine.add_transition("RetrieveLatestLocalDBTimepoint", "processing_old_patient", "obtained_LocalDB_timepoint",
                                    before="CheckLocalDB")
        self.machine.add_transition("IncrementLocalDBTimepoint", "obtained_LocalDB_timepoint", "updated_LocalDB_timepoint",
                                    before="CheckLocalDB")
        self.machine.add_transition("HarmonizeLatestTimepoint", "updated_LocalDB_timepoint", "harmonized_timepoints",
                                    before=["CheckNetwork", "CheckLORIS"])

        # New Subject Path
        self.machine.add_transition("RetrieveGender", "processing_new_patient", "obtained_new_subject_gender",
                                    before="CheckFile")
        self.machine.add_transition("RetrieveBirthday", "obtained_new_subject_gender", "obtained_new_subject_birthday",
                                    before="CheckFile")
        #self.machine.add_transition("RetrieveStudy", "obtained_new_subject_birthday", "RetrieveStudy",
        #                            before="CheckFile")
        self.machine.add_transition("CreateLORISSubject", "obtained_new_subject_birthday", "created_remote_subject",
                                    before=["CheckNetwork", "CheckLORIS"])
        self.machine.add_transition("CreateLocalSubject", "created_remote_subject", "created_local_subject",
                                    before="CheckLocalDB")
        self.machine.add_transition("HarmonizeLatestTimepoint", "created_local_subject", "harmonized_timepoints",
                                    before=["CheckNetwork", "CheckLORIS"])

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
        stream = io.BytesIO()
        self.get_graph(**kwargs).draw(stream, prog='dot', format='png')
        object = stream.getvalue()
        with open(self.name + ".png", "wb") as png:
            png.write(object)

    def CheckOrthancNewData(self):
        list_subjects = orthanc.API.get_list_of_subjects_noauth(self.url)
        if (len(list_subjects) > 0):
            self.has_new_data = True

    def DownloadNewData(self):
        pass

    def UnpackNewData(self):
        pass
    def CheckMRN(self):
        pass
    def CheckLocalDBMRN(self):
        pass
    def RetrieveLatestLocalDBTimepoint(self):
        pass
    def IncrementLocalDBTimepoint(self):
        pass
    def HarmonizeLatestTimepoint(self):
        pass
    def RetrieveGender(self):
        pass
    def RetrieveBirthday(self):
        pass
    def CreateLORISSubject(self):
        pass
    def CreateLocalSubject(self):
        pass
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

    # Conditions Method
    def HasNewData(self):
        return self.has_new_data

    def Found_MRN(self):
        return self.found_mrn

    def NoPreviousMRN(self):
        return self.no_previous_mrn

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
    cmd_folder = os.path.realpath(
        os.path.dirname(
            os.path.abspath(os.path.split(inspect.getfile(inspect.currentframe()))[0])))

    if cmd_folder not in sys.path:
        sys.path.insert(0, cmd_folder)

    Import1 = DICOMTransitImport("2019")
    Import1.show_graph()
    pass