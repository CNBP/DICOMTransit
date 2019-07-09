import DICOM.API
import orthanc.API
import LORIS.API
import LocalDB.API
from DICOM.DICOMPackage import DICOMPackage
from settings import config_get
import os

if __name__ == "__main__":
    """Quick and dirty script that calls various high level APIs to insert a subject from ORTHANC to LORIS"""
    # Eventually, a finite state machine will be built out of this

    credential = orthanc.API.get_prod_orthanc_credentials()
    # credential = orthanc.API.get_local_orthanc_credentials()

    # Get list of subjects.
    # list_subjects = orthanc.API.get_list_of_subjects(url, user, password)
    list_subjects = orthanc.API.get_list_of_subjects_noauth(credential.url)

    assert len(list_subjects) > 0

    # Get ALL subjects, loop through them
    for subject in list_subjects[2:5]:
        try:
            subject_url = (
                f"{credential.url}patients/{subject }/archive"
            )  # it must contain patients/ and archive in the path name

            zip_file = orthanc.API.get_StudyUID_zip(subject_url, credential)

            # Location to write small buffer.
            path_temp = config_get("ZipPath")

            dicom_folder = orthanc.API.unpack_subject_zip(zip_file, path_temp)

            # Convert it to a DICOMPackage, it checks for a bunch of validity, update a bunch of its meta information regarding the entire archive
            DICOM_package = DICOMPackage(dicom_folder)

            # Check Protocol.
            MRN_exist = LocalDB.API.check_MRN(DICOM_package.MRN)

            if MRN_exist is False:  # most common scenario first
                # Dynamicly generate the new CNBPID based ont he protocol.

                # Attempt to generate the CNBPID/PSCID based on study protocol.
                # DICOM_package.CNBPID = LocalDB.API.propose_CNBPID(DICOM_package.studies[0])

                # todo: For now, all project are under LORIS. The projectID etc systems are not being actively used.
                DICOM_package.project = "loris"

                # create new PSCID and get DCCID
                success, DCCID, PSCID = LORIS.API.create_candidate(
                    DICOM_package.project, DICOM_package.birthday, DICOM_package.gender
                )

                # Local Variable for anonymization.
                DICOM_package.DCCID = DCCID
                DICOM_package.CNBPID = PSCID
                DICOM_package.timepoint = "V1"  # auto generated.

                # Update local database storage with regard to CNBPID, DCCID, timepoint, and scandate.
                LocalDB.API.set_CNBP(DICOM_package.MRN, DICOM_package.CNBPID)
                LocalDB.API.set_DCCID(DICOM_package.MRN, DICOM_package.DCCID)
                LocalDB.API.set_timepoint(DICOM_package.MRN, DICOM_package.timepoint)
                LocalDB.API.set_scan_date(DICOM_package.MRN, DICOM_package.scan_date)

            elif MRN_exist is True:
                import datetime

                # Intervention block: Check scan dates to see if they have already been inserted.
                DICOM_date = DICOM_package.scan_date
                API_date_string = LocalDB.API.get_scan_date(DICOM_package.MRN)
                LocalDB_date = datetime.datetime.strptime(
                    API_date_string, "%Y-%m-%d %H:%M:%S"
                )

                if DICOM_date == LocalDB_date:
                    print(
                        "Scan date already exist in the database. Data likely already exist. Consider manual intervention. "
                    )
                    continue

                # Use MRN to retrieve CNBPID, update the dicom-package
                DICOM_package.CNBPID = LocalDB.API.get_CNBP(DICOM_package.MRN)

                # Use MRN to retrieve DCCID, update the dicom-package
                DICOM_package.DCCID = LocalDB.API.get_DCCID(DICOM_package.MRN)

                # Get the latest local known timepoint:
                # last_database_timepoint = LocalDB.API.get_timepoint(DICOM_package.MRN)
                # print("Last known timepoint: "+last_database_timepoint)

                # Using LORIS API to create the new timepoint:
                latest_timepoint = LORIS.API.increment_timepoint(DCCID)
                DICOM_package.timepoint = latest_timepoint

                # Update the record to use the latest timepoint and the scandate!
                LocalDB.API.set_timepoint(DICOM_package.MRN, DICOM_package.timepoint)
                LocalDB.API.set_scan_date(DICOM_package.MRN, DICOM_package.scan_date)

                # Write to database and also online.
            else:
                raise ValueError(
                    "Ambigious MRN existence status. Check code for error."
                )  # Any unanticipated errors.

            # Generate new string with everything.
            DICOM_package.zipname = f"{DICOM_package.CNBPID}_{str(DICOM_package.DCCID)}_{DICOM_package.timepoint}"

            # Anonymize to Zip
            DICOM.API.anonymize_to_zip(
                DICOM_package.dicom_folder, DICOM_package.zipname
            )

            # Upload
            LORIS.API.old_upload(
                os.path.join(
                    r"C:\GitHub\DICOMTransit\Python\data_archives",
                    DICOM_package.zipname + ".zip",
                )
            )

            # Trigger insertion.
            LORIS.API.new_trigger_insertion(DICOM_package.zipname)
        except:
            # Any exceptions, continue!
            continue
