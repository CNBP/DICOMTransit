import luigi
import logging
from DICOMTransit.IntegrationModules.LIM_Status import UpdateOrthancStatus, UpdateLocalDBStatus
from DICOMTransit.IntegrationModules.LIM_Credential import GetDevOrthancCredential
from DICOMTransit.IntegrationModules.LIM_ENV import path_output_pickle

import pickle

logger = logging.getLogger()
from DICOMTransit.orthanc.API import get_all_subject_StudyUIDs




class GetOrthancList(luigi.Task):
    def requires(self):
        return [UpdateOrthancStatus(), GetDevOrthancCredential()]

    def run(self):
        logger.info("Checking Orthanc for new data!")

        with open(
            self.input()[1].path, "rb"
        ) as in_file:  # 1 = GetDevOrthancCredential()
            self.credential = pickle.load(in_file)
            print(self.credential)

        # Get updated orthanc StudyUID.
        orthanc_list_all_StudiesUIDs = get_all_subject_StudyUIDs(self.credential)
        logger.info("Obtained list of all StudiesUID SHA from Orthanc")

        # write each StudyUID
        with open(self.output().path, "wb") as out_file:
            pickle.dump(orthanc_list_all_StudiesUIDs, out_file)

    def output(self):
        return luigi.LocalTarget(path_output_pickle.join("OrthancList.pickle"))


class ProcessOrthancList(luigi.Task):
    def requires(self):
        return [GetOrthancList()]

    def run(self):
        with open(self.input()[0].path, "rb") as in_file:
            orthanc_list_all_StudiesUIDs = pickle.load(in_file)
        for StudyUID in orthanc_list_all_StudiesUIDs:
            yield ProcessOrthancUID(StudyUID)

            # write each StudyUID
            with open(self.output().path, "wa") as out_file:
                pickle.dump(orthanc_list_all_StudiesUIDs, out_file)

    def output(self):
        return luigi.LocalTarget(path_output_pickle.join("ProcessedOrthancList.pickle"))



class ProcessOrthancUID(luigi.Task):
    UID = luigi.Parameter()
    def requires(self):
    def run(self):
        = yield CheckOrthancUID
    def output(self):



if __name__ == "__main__":
    luigi.build([ProcessOrthancList()])
