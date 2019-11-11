import luigi

from DICOMTransit.LocalDB.API import get_list_StudyUID
from DICOMTransit.IntegrationModules.LIM_Status import UpdateLocalDBStatus


class CheckOrthancUID(luigi.Task):
    UID = luigi.ListParameter()

    def requires(self):
        return [UpdateLocalDBStatus]

    def run(self):
        """
        Check LocalDB for the particular StudyUID. Recall StudyUID is appended PER MRN
        :return:
        """
        import json

        # Determine current StudyUID..
        current_study_UID = self.orthanc_list_all_StudiesUIDs[
            self.orthanc_index_current_study
        ]

        # Check the database, get list of all possible study UID.
        list_knownStudyUID = get_list_StudyUID()

        if list_knownStudyUID is None:
            self.matched_orthanc_StudyUID = False
            return

        # Loop through all possible SubjectUID
        for known_StudyUID in list_knownStudyUID:
            list_known_StudyUID = json.loads(
                known_StudyUID
            )  # remember, subjectUUID can have more tha ONE!
            if current_study_UID in list_known_StudyUID:
                self.matched_orthanc_StudyUID = True
                return

        self.matched_orthanc_StudyUID = False
        return

    def output(self):
        return luigi.LocalTarget(path_output_pickle.join(f" {self.UID}.pickle"))
