from DICOM.elements import DICOM_elements
from LocalDB.query import LocalDB_query
from LocalDB.schema import CNBP_blueprint
from dotenv import load_dotenv
import logging
from DICOM.validate import DICOM_validate
#from LORIS.candidates import  LORIS_candidates

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logger = logging.getLogger(__name__)

class Integration:

    @staticmethod
    def step2_dicom2LORIS(folder_paths):
        """
        Within each folder, verify they all have the same PatientID.
        :param folder_paths:
        :return:
        """

        database_path = load_dotenv("LocalDatabase")

        for folder in folder_paths:
            success, DICOM_files = DICOM_validate.path(folder)

            if not success or DICOM_files is None:
                return False

            # At this point, we know all DICOM files from the folder has the same name.
            MRN = DICOM_elements.retrieveMRN(DICOM_files[0])

            # Store MRN in database.
            mrn_exist_in_database, _ = LocalDB_query.check_value(database_path, CNBP_blueprint.table_name, CNBP_blueprint.keyfield, MRN)

            # Continue to next subject if MRN already exist in the database.
            if mrn_exist_in_database:
                continue

            # else database the subject.
            elif not mrn_exist_in_database:

                # Create the subject
                LocalDB_query.create_entry(database_path, CNBP_blueprint.table_name, CNBP_blueprint.keyfield, MRN)

                # Retrieve the PSCID based on the scanner protocol
                #DICOM_elements.get_ResearchProtocol()

                #LORIS_candidates.check_PSCID_compliance(PSCID)

                # Contact LORIS to request new MRN number.
