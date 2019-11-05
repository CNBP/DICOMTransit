import os, sys
import luigi
import logging

sys.path.append("/toshiba4/DICOMTransit")

from DICOMTransit.settings import config_get
from PythonUtils.PUFile import unique_name
from DICOMTransit.LocalDB.API import check_status
from DICOMTransit.LORIS.API import check_online_status


logger = logging.getLogger()
"""
# Sentry Log Monitoring Service SDK:
import sentry_sdk


##################
# Logging sections
##################
# sentry_sdk.init("https://d788d9bf391a4768a22ea6ebabfb4256@sentry.io/1385114")

# Set all debugging level:
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

# Create logger.
# Root Logger (for debug transition)


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


class UpdateNetworkStatus(luigi.Task):
    """
    Luigi task to check if network is working. 
    """

    # Ping CNBP frontend server.
    # Ping LORIS server.
    # Ping Google.
    STATUS_NETWORK = None

    def run(self):
        self.STATUS_NETWORK = check_online_status()

    def complete(self):
        if self.STATUS_NETWORK:
            logger.debug("General Network system status OKAY!")
            return True
        elif self.STATUS_NETWORK is False:
            logger.critical("!!!General Network system is DOWN!!!")

        return False


class UpdateLocalDBStatus(luigi.Task):
    """
    Luigi task to check LocalDB integrity.
    """

    STATUS_LOCALDB = None

    def run(self):
        # Read local db. See if it exist based on the setting.

        self.STATUS_LOCALDB = check_status()

    def complete(self):
        if self.STATUS_LOCALDB:
            logger.debug("LocalDB system status OKAY!")
            return True
        elif self.STATUS_LOCALDB is False:
            logger.critical("!!!LocalDB system is DOWN!!!")
            return False

        # Default path.
        return False


class UpdateOrthancStatus(luigi.Task):
    """
    Luigi task to check if orthanc is online.
    """

    STATUS_ORTHANC = None
    check_dev = luigi.BoolParameter()

    def run(self):

        # Check ENV for the predefined Orthanc URL to ensure that it exists.
        from DICOMTransit.orthanc.API import (
            check_prod_orthanc_status,
            check_dev_orthanc_status,
        )

        if self.check_dev:
            self.STATUS_ORTHANC = check_dev_orthanc_status()
        else:
            self.STATUS_ORTHANC = check_prod_orthanc_status()

    def complete(self):
        if self.STATUS_ORTHANC:
            logger.debug("Orthanc system status OKAY!")
            return True
        elif self.STATUS_ORTHANC is False:
            logger.critical("!!!Orthanc system is DOWN!!!")

        # Default path.
        return False


class UpdateLORISStatus(luigi.Task):
    STATUS_LORIS = None

    def requires(self):
        return [UpdateNetworkStatus(), UpdateLocalDBStatus()]

    def run(self):
        # Ping LORIS production server to check if it is online.
        from DICOMTransit.LORIS.API import check_status

        self.STATUS_LORIS = check_status()

    def complete(self):

        if self.STATUS_LORIS:  # online path.
            logger.debug("LORIS production system status OKAY!")
            return True
        elif self.STATUS_LORIS is False:  # off line path.
            logger.critical(
                "LORIS system not accessible using the provided credential. Either LORIS system is DOWN OR your credential is no longer valid."
            )

        # Default path.
        return False


if __name__ == "__main__":
    luigi.build([UpdateLORISStatus()])
