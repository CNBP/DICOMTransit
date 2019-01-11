import os, sys, inspect, io
from transitions import *
from transitions.extensions import GraphMachine as Machine
import datetime
import logging
logging.basicConfig(level=logging.DEBUG)
logging.getLogger('transition').setLevel(logging.INFO)

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

    class Process(object):

        def __init__(self, name: str = "untitled"):
            self.name = name

        def is_valid(self):
            return True

        def is_not_valid(self):
            return False

        def is_also_valid(self):
            return True

        # graph object is created by the machine
        def show_graph(self, **kwargs):
            stream = io.BytesIO()
            self.get_graph(**kwargs).draw(stream, prog='dot', format='png')
            object = stream.getvalue()
            with open(self.name+".png", "wb") as png:
                png.write(object)

    # Instantiate the process
    ImportProcess = Process(datetime.datetime.now().isoformat())

    def __init__(self, name):

        # Timestamp
        self.time = datetime.datetime.now()

        # We shall name this with
        self.name = self.time.isoformat()

        # Initialize the state machine
        self.machine = Machine(model=self.ImportProcess,
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
                                    before="CheckOrthanc", after="CheckFileCorruption")

        self.machine.add_transition("UnpackNewData", "obtained_new_data", "unpacked_new_data",
                                    before="CheckFileCorruption") # need to check zip file.

        self.machine.add_transition("CheckMRN", "unpacked_new_data", "obtained_MRN",
                                    before="CheckFileCorruption") # # need to check the content of the zip file success

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
                                    before="CheckFileCorruption")
        self.machine.add_transition("RetrieveBirthday", "obtained_new_subject_gender", "obtained_new_subject_birthday",
                                    before="CheckFileCorruption")
        #self.machine.add_transition("RetrieveStudy", "obtained_new_subject_birthday", "RetrieveStudy",
        #                            before="CheckFileCorruption")
        self.machine.add_transition("CreateLORISSubject", "obtained_new_subject_birthday", "created_remote_subject",
                                    before=["CheckNetwork", "CheckLORIS"])
        self.machine.add_transition("CreateLocalSubject", "created_remote_subject", "created_local_subject",
                                    before="CheckLocalDB")
        self.machine.add_transition("HarmonizeLatestTimepoint", "created_local_subject", "harmonized_timepoints",
                                    before=["CheckNetwork", "CheckLORIS"])

        # From this point onward, all path are merged:
        self.machine.add_transition("AnonymizeFiles", "harmonized_timepoints", "files_anonymized",
                                    before="CheckFileCorruption", after="DoubleCheckAnonymization")

        self.machine.add_transition("ZipFiles", "files_anonymized", "files_zipped",
                                    conditions="AreAnonymized", before="CheckFiles", after="CheckFiles")
        self.machine.add_transition("UploadZip", "files_zipped", "zip_uploaded",
                                    before=["CheckNetwork", "CheckLORIS"], after="CheckUploadSuccess")
        self.machine.add_transition("InsertSubjectData", "zip_uploaded", "zip_inserted",
                                    before=["CheckNetwork", "CheckLORIS"], after="CheckInsertion")
        self.machine.add_transition("RecordInsertion", "zip_inserted", "waiting",
                                    conditions="AreInserted", before=["CheckNetwork", "CheckLORIS"])

        """            
        # Any time, in ANY state, if these check fails, we should go to error state. There might be additional flags in terms situation specific reactions.
        self.machine.add_transition("CheckOrthanc",         "*", "error_orthanc",           conditions="OrthancUnavailable")
        self.machine.add_transition("CheckLORIS",           "*", "error_LORIS",             conditions="LORISUnavailable")
        self.machine.add_transition("CheckFileCorruption",  "*", "error_file_corruption",   conditions="FileUnavailable")
        self.machine.add_transition("CheckLocalDB",         "*", "error_localDB",           conditions="LocalDBUnavailable")
        self.machine.add_transition("CheckNetwork",         "*", "error_network",           conditions="NetworkUnavailable")


        # At the end, if all else fails, log, ask for help. Ready for next run.
        self.machine.add_transition("AskMeatBagsForHelp", "*", "human_intervention_required")
        """

    def draw_fsm(self):
        # draw the whole graph ...
        self.ImportProcess.show_graph()

if __name__ == "__main__":
    cmd_folder = os.path.realpath(
        os.path.dirname(
            os.path.abspath(os.path.split(inspect.getfile(inspect.currentframe()))[0])))

    if cmd_folder not in sys.path:
        sys.path.insert(0, cmd_folder)

    Import1 = DICOMTransitImport("2019")
    Import1.draw_fsm()
    pass