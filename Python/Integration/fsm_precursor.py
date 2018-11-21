import DICOM.API
import orthanc.API
import LORIS.API
import LocalDB.API
from DICOM.DICOMPackage import DICOMPackage
import os

if __name__ == "__main__":
    """Quick and dirty script that calls various high level APIs to insert a subject from ORTHANC to LORIS"""
    # Eventually, a finite state machine will be built out of this

    # Get list of subjects.
    list_subjects = orthanc.API.get_list_of_subjects()

    # Get first subject.
    dicom_folder = orthanc.API.get_subject_zip(list_subjects[0]) # if index is 0, no subject in LORIS.

    # Convert it to a DICOMPackage.
    DICOM_package = DICOMPackage(dicom_folder)


    # Check Protocol.
    DICOM_package.update_MRN()
    DICOM_package.update_study()
    MRN = DICOM_package.MRN

    MRN_exist = LocalDB.API.check_MRN(MRN)

    if MRN_exist:

        # Use MRN to retrieve CNBPID, update the dicom-package
        DICOM_package.CNBPID = LocalDB.API.get_CNBP(MRN)

        # Use MRN to retrieve DCCID, update the dicom-package
        DICOM_package.DCCID = LocalDB.API.get_DCCID(MRN)

        # Use MRN to retrieve VISIT , update the dicom-package
        DICOM_package.visit = LocalDB.API.get_visit(MRN)

        # Auto increment the VISIT count.

        # Write to database and also online.

    else:

        # Dynamicly generate the new CNBPID based ont he protocol.

        # todo: attempt to generate the CNBPID/PSCID based on study protocol.
        DICOM_package.CNBPID = LocalDB.API.propose_CNBPID(DICOM_package.studies[0])

        # create new PSCID and get DCCID
        success, DCCID = LORIS.API.create_new(DICOM_package.CNBPID)

        # Local Variable for anonymization.
        DICOM_package.DCCID = DCCID
        DICOM_package.visit = "V1" # auto generated.

        # Update local database storage.
        LocalDB.API.set_CNBP(DICOM_package.MRN, DICOM_package.CNBPID)
        LocalDB.API.set_DCCID(DICOM_package.MRN, DCCID)
        LocalDB.API.set_timepoint(DICOM_package.MRN, "V1")

    # Generate new string with everything.
    DICOM_package.zipname = DICOM_package.CNBPID + "_" + str(DICOM_package.DCCID) + "_" + DICOM_package.visit

    # Anonymize to Zip
    DICOM.API.anonymize_to_zip(DICOM_package.dicom_folder, DICOM_package.zipname)

    # Upload
    LORIS.API.upload(os.path.join(r"C:\GitHub\DICOMTransit\Python\data_archives", DICOM_package.zipname + ".zip"))

    # Trigger insertion.
    LORIS.API.trigger_insertion(DICOM_package.zipname)