import luigi
import logging
from DICOMTransit.IntegrationModules.LIM_Status import UpdateOrthancStatus
from DICOMTransit.orthanc.API import get_dev_orthanc_credentials


logger = logging.getLogger()
from DICOMTransit.orthanc.API import get_all_subject_StudyUIDs


class GetOrthancList(luigi.Task):
    credential = luigi.Parameter(
        default=get_dev_orthanc_credentials()
    )  # to be overwritten by LIM_Credential

    def requires(self):
        return [UpdateOrthancStatus()]

    def run(self):
        logger.info("Checking Orthanc for new data!")

        # Get updated orthanc StudyUID.
        orthanc_list_all_StudiesUIDs = get_all_subject_StudyUIDs(self.credential)
        logger.info("Obtained list of all StudiesUID SHA from Orthanc")

        # write each StudyUID
        with self.output().open("w") as outfile:
            for StudyUID in orthanc_list_all_StudiesUIDs:
                outfile.write("{StudyUID}\n")

    def output(self):
        return luigi.LocalTarget("OrthancList.txt")

class ProcessOrthancList(luigi.Task):
    def requires(self):
        return []

    def run(self):

    def output(self):
        return luigi.LocalTarget()

