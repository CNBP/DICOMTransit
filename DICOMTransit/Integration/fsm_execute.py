import os, sys, inspect
from transitions import MachineError
from PythonUtils.PUDateTime import sleep_until
import pickle
from datetime import time as timeobject
from DICOMTransit.Integration.fsm import DICOMTransitImport
import logging
from DICOMTransit.settings import config_get

# Import the states and transition definitions
from DICOMTransit.Integration.fsm_states import *
from DICOMTransit.Integration.fsm_transitions import *

from PythonUtils.PUFile import unique_name

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

#############################################
# Main execution component to DRIVE the FSM.
##############################################


if __name__ == "__main__":

    # Periodically trigger this:
    cmd_folder = os.path.realpath(
        os.path.dirname(
            os.path.abspath(os.path.split(inspect.getfile(inspect.currentframe()))[0])
        )
    )

    if cmd_folder not in sys.path:
        sys.path.insert(0, cmd_folder)

    current_import_process = DICOMTransitImport()
    current_import_process.setup_machine()

    """
    The main entry point of the application
    """

    delete_LocalDB = False

    if delete_LocalDB:
        ####DELETE THIS PART, fixme
        # Debug deletion of the temporary database
        from DICOMTransit.settings import config_get

        localDB_path = config_get("LocalDatabasePath")
        os.remove(localDB_path)
        from DICOMTransit.LocalDB.create_CNBP import LocalDB_createCNBP

        LocalDB_createCNBP.database(localDB_path)
        ####DELETE THIS PART

    # System initialization check.
    current_import_process.UpdateOrthancStatus()
    current_import_process.UpdateNetworkStatus()
    current_import_process.UpdateLocalDBStatus()
    current_import_process.UpdateLORISStatus()

    # From this point onward, going to assume, they remain the same for the duration of the transaction.
    # Current system is NOT robust enough to deal with mid interruption. It will just trigger failed insertion to try again.

    # Import1.show_graph()

    # current_import.waiting is the default state.

    # Execute the following every 10 minutes:
    # fixme: disable transition error. Let silent fail.

    monitoring = True

    # This variable controls whether in this loop, we are processing new data or just processing existing data.
    # This controls whether "orthanc_list_all_subjectUUIDs" list get updated from Orthanc or not.
    check_new_data = True

    while monitoring:
        try:
            # Initial state MUST be waiting:
            current_import_process.reinitialize()

            if check_new_data:
                current_import_process.trigger_wrap(TR_UpdateOrthancNewDataStatus)

            current_import_process.trigger_wrap(
                TR_HandlePotentialOrthancData
            )  # has its own branching termination state.
            # Need to loop back here.
            if current_import_process.has_new_data():

                current_import_process.trigger_wrap(TR_CheckLocalDBStudyUID)

                if current_import_process.has_matched_orthanc_StudyUID():
                    current_import_process.trigger_wrap(
                        TR_ProcessNextSubject
                    )  # either way, gonna trigger this transition.
                    # Need to loop back based on the beginning BUT not get new data.
                    check_new_data = False
                    continue

                current_import_process.trigger_wrap(TR_DownloadNewData)
                current_import_process.trigger_wrap(TR_UnpackNewData)
                current_import_process.trigger_wrap(TR_ObtainDICOMMRN)
                current_import_process.trigger_wrap(TR_UpdateNewMRNStatus)
            else:
                # that previous statement will transition to waiting state.
                logger.info(
                    f"Orthanc did not detect any new data. Sleeping until 19:00. Current time:{unique_name()}"
                )
                check_new_data = True

                sleep_until(timeobject(hour=19))

                continue

            current_import_process.trigger_wrap(
                TR_ProcessPatient
            )  # has its own branching termination state.

            if current_import_process.found_MRN():
                ###################
                # old patients path
                ###################
                current_import_process.trigger_wrap(TR_FindInsertionStatus)

                # First date match loop back.
                if current_import_process.has_matched_localUID():
                    current_import_process.trigger_wrap(
                        TR_ProcessNextSubject
                    )  # either way, gonna trigger this transition.
                    # Need to loop back based on the beginning BUT not get new data.
                    check_new_data = False
                    continue
                else:
                    current_import_process.trigger_wrap(TR_QueryLocalDBForDCCID)
                    current_import_process.trigger_wrap(TR_QueryRemoteUID)

                    # Second UID match loop back.
                    if current_import_process.has_matched_remoteUID():
                        current_import_process.trigger_wrap(
                            TR_ProcessNextSubject
                        )  # either way, gonna trigger this transition.
                        # Need to loop back based on the beginning BUT not get new data.
                        check_new_data = False
                        continue
                    current_import_process.trigger_wrap(TR_IncrementRemoteTimepoint)
                    current_import_process.trigger_wrap(TR_UpdateLocalRecords)
            else:
                ###################
                # new patient path
                ###################
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

            if current_import_process.has_more_data():
                current_import_process.trigger_wrap(TR_ProcessNextSubject)
                check_new_data = False

                logger.info("One insertion cycle complete. Check next subject.")
                continue

            current_import_process.trigger_wrap(TR_ResumeMonitoring)

            logger.info(
                f"One pass through insertion of ALL orthanc data is now complete. Sleeping until 19:00 before checking next cycle. Current time: {unique_name()}"
            )
            check_new_data = True
            sleep_until(timeobject(hour=19))

        except (NotImplementedError, ValueError):
            # except (ValueError, AssertionError, IOError, OSError, AssertionError, MachineError, ConnectionError):

            current_study_UID = current_import_process.orthanc_list_all_StudiesUIDs[
                current_import_process.orthanc_index_current_study
            ]
            logger.critical(
                f"A critical error has been encountered which aborted the subject scan for {current_study_UID}"
            )

            from DICOMTransit.settings import config_get

            zip_path = config_get("ZipPath")
            name_log = os.path.join(
                zip_path, "StateMachineDump_" + unique_name() + ".pickle"
            )
            with open(name_log, "wb") as f:
                # Pickle the 'data' dictionary using the highest protocol available.
                pickle.dump(current_import_process.machine, f, pickle.HIGHEST_PROTOCOL)
            logger.warning(
                f"A finite state machine pickle dump has been made at {name_log}"
            )
            logger.warning("Check that path for more detail. ")
            current_import_process.critical_error = True
            current_import_process.trigger_wrap(
                TR_ProcessNextSubject
            )  # When ONE subject impede flow, go to the next one (without checking new data)!
            check_new_data = False
