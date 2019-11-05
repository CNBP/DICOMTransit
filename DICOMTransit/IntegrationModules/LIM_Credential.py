import luigi
import logging

from DICOMTransit.IntegrationModules.LIM_Status import UpdateLocalDBStatus
from DICOMTransit.orthanc.API import (
    get_prod_orthanc_credentials,
    get_dev_orthanc_credentials,
)

logger = logging.getLogger()


class getCredential(luigi.Config):
    credential = None

    def requires(self):
        return [UpdateLocalDBStatus()]

    # credential = luigi.Parameter(default=get_dev_orthanc_credentials()
    def run(self):
        self.credential = get_dev_orthanc_credentials()
        # self.credential = get_prod_orthanc_credentials()

    def output(self):
        return luigi.LocalTarget("Credential.txt")

    def complete(self):
        if self.STATUS_NETWORK is not None:
            logger.debug("Orthanc credential retrieved successfully.")
            return True
        else:
            return False
