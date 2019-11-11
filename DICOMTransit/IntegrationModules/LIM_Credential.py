import luigi
import logging
import pickle

from DICOMTransit.IntegrationModules.LIM_Status import UpdateLocalDBStatus
from DICOMTransit.IntegrationModules.LIM_ENV import path_output_pickle
from DICOMTransit.orthanc.API import (
    get_prod_orthanc_credentials,
    get_dev_orthanc_credentials,
)

logger = logging.getLogger()


class GetDevOrthancCredential(luigi.Task):
    def requires(self):
        return [UpdateLocalDBStatus()]

    def run(self):
        credential = (
            get_dev_orthanc_credentials()
        )  # to be overwritten by LIM_Credential
        with open(self.output().path, "wb") as out_file:
            pickle.dump(credential, out_file)

    def output(self):
        return luigi.LocalTarget(path_output_pickle.join("OrthancCredential.pickle"))
