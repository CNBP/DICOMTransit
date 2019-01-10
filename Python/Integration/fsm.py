from transitions import Machine
import datetime
import logging
logging.basicConfig(level=logging.DEBUG)
logging.getLogger('transition').setLevel(logging.INFO)

class DICOMTransitImport(object):

    # These are the plausible major steps within a DICOMTransitImport process.
    states = [
        "waiting",

        "no_new_data_detected",
        "detected_new_data",

        "no_new_data_obtained",
        "obtained_new_data",

        "cannot_obtain_MRN",
        "no_MRN_obtained",
        "obtained_MRN",

        "cannot_connect_LocalDB",
        "connected_LocalDB",

        "no_matching_MRN",
        "found_matching_MRN",

        "cannot_connect_LORIS",
        "connected_LORIS",

        "files_anonymized"
        
        "files_zipped"

        "zip_prepared",


        "zip_uploaded",

        "zip_inserted",

        "error_orthanc",

        "error_LORIS",

        "error_file_corruption",

        "error_sqlite",

        "error_network",

        "human_intervention_required",
    ]


    # trigger, source, destination
    actions = [
        ['CheckMRIScanner', 'waiting', 'detected_new_data'],
        [],
        [],
        [],
        [],
        [],
        [],
        [],



    ]

    def __init__(self, name):

        # Timestamp
        self.time = datetime.datetime.now()

        # We shall name this with
        self.name = self.time.isoformat()

        # Initialize the state machine
        self.machine = Machine(model=self,
                               states=DICOMTransitImport.states,
                               transitions=DICOMTransitImport.actions,
                               auto_transitions=False,
                               initial="waiting")

        #Transitions:
        self.machine.add_transition(trigger="CheckOrthanc", source="waiting", dest="detected_new_data", condition="Has_NewData")
        self.machine.add_transition("DownloadNewData", "detected_new_data", "obtained_new_data")
        self.machine.add_transition("CheckMRN", "obtained_new_data", "obtained_MRN", conditions="Has_ZIP")
        self.machine.add_transition("ConnectLocalDB", "obtained_MRN", "connected_LocalDB", conditions="Has_MRN")
        self.machine.add_transition("CheckLocalDBMRN", "connected_LocalDB", "ProcessingOldPatient", conditions="Found_MRN")
        self.machine.add_transition("CheckLocalDBMRN", "connected_LocalDB", "ProcessingNewPatient", conditions="NoPreviousMRN")


        # New Subject Path.
        self.machine.add_transition("RetrieveGender", "ProcessingNewPatient", "obtained_new_subject_gender", conditions="DICOMHasGender")
        self.machine.add_transition("RetrieveDOB", "obtained_new_subject_gender", "obtained")
        self.machine.add_transition("", "", "")
        self.machine.add_transition("", "", "")
        self.machine.add_transition("", "", "")
        self.machine.add_transition("", "", "")
        self.machine.add_transition("", "", "")
        self.machine.add_transition("", "", "")
        self.machine.add_transition("", "", "")
        self.machine.add_transition("", "", "")
        self.machine.add_transition("", "", "")





