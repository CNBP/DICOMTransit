import DICOM.API
import orthanc.API
import LORIS.API
import LocalDB.API
from DICOM.DICOMPackage import DICOMPackage

import os

if __name__ == "__main__":
    """Quick and dirty script that calls various high level APIs to insert a subject from ORTHANC to LORIS"""
    # Eventually, a finite state machine will be built out of this
    url, user, password = orthanc.API.get_local_orthanc_credentials()

    # Get list of subjects.
    list_subjects = orthanc.API.get_list_of_subjects(url, user, password)

    assert len(list_subjects) > 0

    # Get ALL subjects, loop through them
    for subject in list_subjects:

        subject_url = url + "patients/" + subject + '/archive' # it must contain patients/ and archive in the path name

        dicom_folder = orthanc.API.get_subject_zip(subject_url, user, password)

        # Convert it to a DICOMPackage, it checks for a bunch of validity, update a bunch of its meta information regarding the entire archive
        DICOM_package = DICOMPackage(dicom_folder)

        # Check Protocol.
        MRN_exist = LocalDB.API.check_MRN(DICOM_package.MRN)

        if MRN_exist is False:  # most common scenario first
            # Dynamicly generate the new CNBPID based ont he protocol.

            # todo: attempt to generate the CNBPID/PSCID based on study protocol.
            DICOM_package.CNBPID = LocalDB.API.propose_CNBPID(DICOM_package.studies[0])

            # create new PSCID and get DCCID
            success, DCCID = LORIS.API.create_new(DICOM_package.CNBPID, DICOM_package.birthday, DICOM_package.sex)

            # Local Variable for anonymization.
            DICOM_package.DCCID = DCCID
            DICOM_package.timepoint = "V1" # auto generated.

            # Update local database storage.
            LocalDB.API.set_CNBP(DICOM_package.MRN, DICOM_package.CNBPID)
            LocalDB.API.set_DCCID(DICOM_package.MRN, DCCID)
            LocalDB.API.set_timepoint(DICOM_package.MRN, "V1")

        elif MRN_exist is True:

            # Intervention block: Check scan dates to see if they have already been inserted.
            if (DICOM_package.scan_date == LocalDB.API.get_scan_date(DICOM_package.MRN)):
                raise ValueError("Scan date already exist in the database. Data likely already exist. Consider manual intervention. ")

            # Use MRN to retrieve CNBPID, update the dicom-package
            DICOM_package.CNBPID = LocalDB.API.get_CNBP(DICOM_package.MRN)

            # Use MRN to retrieve DCCID, update the dicom-package
            DICOM_package.DCCID = LocalDB.API.get_DCCID(DICOM_package.MRN)

            # Get the latest local known timepoint:
            last_database_timepoint = LocalDB.API.get_timepoint(DICOM_package.MRN)

            # TODO: refactor the loris timepoint into API.

            """
            from LORIS.timepoint import LORIS_timepoint
            # Get the latest LORIS known timepoint:
            last_LORIS_timepoint = LORIS_timepoint.findLatestTimePoint()
            
            # Ensure they are consistent. 
            
            # Increment timepoint locally.
            # Increment timepoint on LORIS. 
            # Update package with the proper time point. 

            """



            # Auto increment the VISIT count.

            # Use MRN to retrieve VISIT , update the dicom-package
            DICOM_package.timepoint = LocalDB.API.get_timepoint(DICOM_package.MRN)

            # Write to database and also online.
        else:
            raise ValueError("Ambigious MRN existence status. Check code for error.")  # Any unanticipated errors.

        # Generate new string with everything.
        DICOM_package.zipname = DICOM_package.CNBPID + "_" + str(DICOM_package.DCCID) + "_" + DICOM_package.visit

        # Anonymize to Zip
        DICOM.API.anonymize_to_zip(DICOM_package.dicom_folder, DICOM_package.zipname)

        # Upload
        LORIS.API.upload(os.path.join(r"C:\GitHub\DICOMTransit\Python\data_archives", DICOM_package.zipname + ".zip"))

        # Trigger insertion.
        LORIS.API.trigger_insertion(DICOM_package.zipname)