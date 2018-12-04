import logging
import sys
import traceback

from pydispatch import dispatcher

import DICOM.API
import LORIS.API
import LocalDB.API
import orthanc.API
from DICOM.DICOMPackage import DICOMPackage
from PythonUtils.file import current_funct_name

SIGNAL          = 'my-first-signal'
SIG_Error       = 'Generic Error'

# Generic Error Signals
ERROR_Orthanc   = 'Generic Orthanc error'
ERROR_DICOM     = 'Generic DICOM error'
ERROR_LORIS     = 'Generic LORIS error'
ERROR_SQLite    = 'Generic SQLite error'

SIG_INCOMING_DICOM = 'incoming-dicom'
SIG_GET_DICOM_FILE = 'get-dicom-file'
SIG_GET_MRN_FROM_DICOM = 'get-MRN-from-dicom'
SIG_CHECK_MRN_EXISTS = 'check-MRN-exists'


SIG_GET_CNBPID_USING_MRN = 'get-CNBPID-using-MRN'
SIG_GET_DCCID_USING_MRN = 'get-DCCID-using-MRN'
SIG_GET_VISIT_USING_MRN = 'get-VISIT-using-MRN'

SIG_GET_AND_ASSIGN_CNBPID_USING_MRN = 'get-and-assign-CNBPID-using-MRN'

SIG_GENERATE_CNBPID = 'assign-CNBPID'
SIG_MRN_DOES_NOT_EXIST = 'MRN-does-not-exist'
SIG_GET_LORISID_AND_VISIT = 'get-lorsid-and-timepoint'
SIG_ANONYMIZE_DATA = 'anonymize-data'
SIG_UPLOAD_ANONYMIZED_DATA = 'upload-anonymized-data'
SIG_HANDLE_DICOM_FILE = 'handle-dicom-file'
SIG_TASK_COMPLETE = 'task-complete'

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logger = logging.getLogger('Finite state machine')

""" Function to handle events """
def handle_event(signal, sender ):
    """Simple event handler"""
    print(signal, ' to handle_event was sent by', sender)


def pacs():
    """Simple event trigger"""
    pacs_sender = "pacs_sender"
    dispatcher.send(signal=SIG_INCOMING_DICOM,
                    sender=current_funct_name())


def scanner(signal, sender ):
    """Simple event handler"""
    print(signal, ' to scanner was sent by', sender)


def check_orthanc_srvr(signal, sender):
    """Check orthanc server using the orthanc module and pass on the list to the next event handler to process individual subject
    :param signal: The signal that this function is listening to.
    :param sender: The sender that sent this signal.
    :returns: None.
    """
    print(signal, ' to check_orthanc_srvr was sent by', sender)

    # Save the function arguments in case of recovery
    mylocals = locals()

    try:
        list_subjects = orthanc.API.get_list_of_subjects() #todo: this API call must support authentication. ERROR IMMENENT
        # Pass the signal to get DICOM fils based on the list of subjects given.
        dispatcher.send(signal=SIG_GET_DICOM_FILE,
                        sender=current_funct_name(),
                        list_subjects=list_subjects)

    except Exception as ex:
        # traceback.print_exc(file=sys.stdout)
        args = {"Exception": ex, 'locals': mylocals}
        dispatcher.send(signal=ERROR_Orthanc,
                        sender=current_funct_name(),
                        arglist=args)


def get_DICOM_file(signal=None, sender=None, list_subjects=None):
    """
    Event handler to attempt to get DICOM-files using ORTHANC API based on the configuration specified in the .env file
    :param signal:
    :param sender:
    :return:
    """
    print('Signal is',                  signal)
    print('Signal to get_DICOM_file was sent by', sender)

    # Save the function arguments in case of recovery
    mylocals = locals()

    # Loop through each Orthanc subject UUID
    for subject in list_subjects:

        try:
            # Get the temporary folder object reference
            dicom_folder = orthanc.API.get_subject_zip(subject)

            # Package it using the DICOMPackage class
            DICOM_package = DICOMPackage(dicom_folder)

            # Send for down stream processing
            dispatcher.send(signal=SIG_HANDLE_DICOM_FILE,
                            sender=current_funct_name(),
                            DICOM_package=DICOM_package)
        except Exception as ex:
            #traceback.print_exc(file=sys.stdout)
            args={"Exception": ex,'locals':mylocals}
            dispatcher.send(signal=ERROR_Orthanc,
                            sender=current_funct_name(),
                            arglist=args)


def get_MRN_from_DICOM(signal=None, sender=None, DICOM_package: DICOMPackage=None):
    """
    Calls the lower level function to get and update MRN information within the DICOM package.
    :param signal:
    :param sender:
    :param DICOM_package:
    :return:
    """
    print('Signal is',                  signal)
    print('Signal to get_MRN_from_DICOM was sent by', sender)

    # Save the function arguments in case of recovery
    mylocals = locals()

    # Use the DICOMPackage class function to validate.
    try:
        DICOM_package.update_MRN()
        dispatcher.send(signal=SIG_CHECK_MRN_EXISTS,
                        sender=current_funct_name(),
                        DICOM_package=DICOM_package,
                        from_signal=signal)
    except Exception as ex:
        #traceback.print_exc(file=sys.stdout)
        args={"Exception": ex, 'locals':mylocals}
        dispatcher.send(signal=ERROR_DICOM,
                        sender=current_funct_name(),
                        arglist=args)


def check_mrn_exists(signal=None, sender=None, DICOM_package: DICOMPackage=None):
    """
    Check if the CNBPID corresponding to the MRN exist locally then either get it or generate the CNBPID
    :param signal:
    :param sender:
    :param DICOM_package:
    :return:
    """
    print('Signal is', signal)
    print('Signal to check_mrn_exists was sent by', sender)

    # Save the function arguments in case of recovery
    mylocals = locals()

    try:
        MRN = DICOM_package.MRN
        MRN_exist = LocalDB.API.check_MRN(MRN)

        if MRN_exist: #in the local SQLiteDB
            dispatcher.send(signal=SIG_GET_CNBPID_USING_MRN,
                            sender=current_funct_name(),
                            DICOM_package=DICOM_package)
            dispatcher.send(signal=SIG_GET_DCCID_USING_MRN,
                            sender=current_funct_name(),
                            DICOM_package=DICOM_package)
            dispatcher.send(signal=SIG_GET_VISIT_USING_MRN,
                            sender=current_funct_name(),
                            DICOM_package=DICOM_package)
        else: #not exist scenerio
            dispatcher.send(signal=SIG_GENERATE_CNBPID,
                            sender=current_funct_name(),
                            DICOM_package=DICOM_package)
    except Exception as ex:
        # In case SQLite connection has issues.
        args = {"Exception": ex, 'locals':mylocals}
        dispatcher.send(signal=ERROR_SQLite,
                        sender=current_funct_name(),
                        arglist=args)


def get_CNBPID_using_MRN(signal=None, sender=None, DICOM_package: DICOMPackage=None):
    """
    Check if the MRN exist locally then either get the information locally OR assign it remotely.
    :param signal:
    :param sender:
    :param DICOM_package:
    :return:
    """
    print('Signal is', signal)
    print('Signal to check_mrn_exists was sent by', sender)

    # Save the function arguments in case of recovery
    mylocals = locals()

    try:
        # Use MRN
        MRN = DICOM_package.MRN

        # Use MRN to retrieve CNBPID, update the dicom-package
        DICOM_package.cnbpid = LocalDB.API.get_CNBP(MRN)

        dispatcher.send(signal=SIG_TASK_COMPLETE,
                        sender=current_funct_name(),
                        DICOM_package=DICOM_package)
    except Exception as ex:
        # traceback.print_exc(file=sys.stdout)
        args = {"Exception": ex, 'locals': mylocals}
        dispatcher.send(signal=ERROR_DICOM,
                        sender=current_funct_name(),
                        arglist=args)


def assign_cnbpid_using_mrn(signal=None, sender=None, dicom_file=None):
    """Simple event handler"""
    print('Signal is',                  signal)
    print('Signal to assign_cnbpid_using_mrn was sent by', sender)
    # Get CNBPID based on MRN
    # THE CNBPDID
    # Assign retrieved MRN
    dicom_file.cnbpid = 999
    dispatcher.send(signal=SIG_TASK_COMPLETE,
                    sender=current_funct_name(),
                    from_signal=signal,
                    DICOM_package=dicom_file)


def get_DCCID_using_MRN(signal=None, sender=None, DICOM_package: DICOMPackage=None):
    """
    Check if the DCCID exist locally in the SQLite database
    :param signal:
    :param sender:
    :param DICOM_package:
    :return:
    """
    print('Signal is', signal)
    print('Signal to check_mrn_exists was sent by', sender)

    # Save the function arguments in case of recovery
    mylocals = locals()

    try:
        # Use MRN
        MRN = DICOM_package.MRN

        # Use MRN to retrieve CNBPID, update the dicom-package
        DICOM_package.DCCID = LocalDB.API.get_DCCID(MRN)

        dispatcher.send(signal=SIG_TASK_COMPLETE,
                        sender=current_funct_name(),
                        DICOM_package=DICOM_package)
    except Exception as ex:
        # traceback.print_exc(file=sys.stdout)
        args = {"Exception": ex, 'locals': mylocals}
        dispatcher.send(signal=ERROR_DICOM,
                        sender=current_funct_name(),
                        arglist=args)


def get_VISIT_using_MRN(signal=None, sender=None, DICOM_package: DICOMPackage=None):
    """
    Check if the DCCID exist locally in the SQLite database
    :param signal:
    :param sender:
    :param DICOM_package:
    :return:
    """
    print('Signal is', signal)
    print('Signal to check_mrn_exists was sent by', sender)

    # Save the function arguments in case of recovery
    mylocals = locals()

    try:
        # Use MRN
        MRN = DICOM_package.MRN
        
        # Use MRN to retrieve CNBPID, update the dicom-package
        DICOM_package.visit = LocalDB.API.get_visit(MRN)

        dispatcher.send(signal=SIG_TASK_COMPLETE,
                        sender=current_funct_name(),
                        DICOM_package=DICOM_package)
    except Exception as ex:
        # traceback.print_exc(file=sys.stdout)
        args = {"Exception": ex, 'locals': mylocals}
        dispatcher.send(signal=ERROR_DICOM,
                        sender=current_funct_name(),
                        arglist=args)


def assign_cnbpid(signal=None, sender=None, cnbpid=None, dicom_file=None ):
    """Simple event handler"""
    print('Signal is',                  signal)
    print('Signal to assign_cnbpid was sent by', sender)
    print('CNBPID := ', cnbpid)
    # Assign CNBPID. This function is no longer necessary because of
    # get_cnbpid_from_mrn it seems. The latter functions assigns the value 
    dicom_file.cnbpid
    # Send signal that result is ready
    dispatcher.send(signal=SIG_TASK_COMPLETE,
                    sender=current_funct_name(),
                    from_signal=signal,
                    dicomFile=dicom_file)


def anonymize_data(signal=None, sender=None, dicom_file=None):
    """Simple event handler"""
    print('Signal is',                  signal)
    print('Signal to anonymize_data was sent by', sender)
    # dicom_folder.dicom_folder = 'an anonymized dicom file'

    DICOM.API.anonymize_files(dicom_file.get_dicom_files())
    dicom_file.is_anonymized = True
    dispatcher.send(signal=SIG_TASK_COMPLETE,
                    sender=current_funct_name(),
                    from_signal=signal,
                    DICOM_package=dicom_file)


def upload_anonymized_data(signal=None, sender=None, anon_dicom_file: DICOMPackage=None):
    """Simple event handler"""
    print('Signal is',                  signal)
    print('Signal to upload_anonymized_data was sent by', sender)

    # Upload anonymized file

    # Generate the appropriate zip first.
    anon_dicom_file.zip()

    # Upload the zip file to the server for further processing.
    LORIS.API.upload(anon_dicom_file.zip_location)

    dispatcher.send(signal=SIG_TASK_COMPLETE,
                    sender=current_funct_name(),
                    from_signal=signal,
                    DICOM_package=anon_dicom_file)


"""
Postman directs the appropriate action to take depending on what state
processing is in
Postman is then sent a signal by tasks that have finished with the results
@arglist ; A dictionary
@DICOM_package ; DICOMPackage, a collection of DICOM files. 
@signal ; Signal, relayed by PyDispatch
@sender ;  Sender of the signal, relayed by PyDispatch
@from_signal ; The signal that precipitated the value in 'signal'
"""
def postman (signal=None, sender=None, from_signal=None, DICOM_package: DICOMPackage=None, arglist=None):
    print('Signal is',                  signal)
    print('Signal to postman was sent by', sender)

    # 1a. Get DICOM package from
    if(signal==SIG_HANDLE_DICOM_FILE ):
        if( DICOM_package is not None):
            # 1b. Get MRN from DICOM file
            if(DICOM_package.dicom_folder != None):
                print(DICOM_package.dicom_folder)
                dispatcher.send(signal=SIG_GET_MRN_FROM_DICOM,
                                sender=postman,
                                DICOM_package=DICOM_package)
                #get_MRN_from_DICOM(dicom_folder=dicom_filev)

    # 2., 3. Get CNBPID using MRN
    if(from_signal==SIG_GET_MRN_FROM_DICOM):
        if(DICOM_package is not None):
            if(DICOM_package.mrn is not None):
                dispatcher.send(signal=SIG_GET_AND_ASSIGN_CNBPID_USING_MRN,
                                sender=postman,
                                DICOM_package=DICOM_package)
                #assign_cnbpid_using_mrn(MRN=mrnv,dicom_folder=dicom_filev)

    # 4. Assign CNBPID (to dicom file?)
    if(from_signal==SIG_GET_CNBPID_USING_MRN):
        if(DICOM_package is not None):
            if(DICOM_package.cnbpid is not None):
                dispatcher.send(signal=SIG_GENERATE_CNBPID,
                                sender=postman,
                                DICOM_package=DICOM_package)
                #assign_cnbpid(CNBPID=cnbpidv,dicom_folder=dicom_filev)

    # 5. Get DCCID and timepoint
    if(from_signal==SIG_GET_AND_ASSIGN_CNBPID_USING_MRN):
        if(DICOM_package is not None):
            if(DICOM_package.cnbpid is not None):
                dispatcher.send(signal=SIG_GET_LORISID_AND_VISIT,
                                sender=postman,
                                DICOM_package=DICOM_package)
                #get_DCCID_using_MRN( CNBPID=cnbpidv )

    # 6. Anonymize dicom file
    if(from_signal==SIG_GET_LORISID_AND_VISIT ):
        if(DICOM_package is not None):
            if(DICOM_package.lorisid is not None and DICOM_package.visit is not None):
                # 6. Anonymize the dicom file
                dispatcher.send(signal=SIG_ANONYMIZE_DATA,
                                sender=postman,
                                DICOM_package=DICOM_package)
                #anonymize_data(dicom_folder=dicom_filev,
                #              lorisid_and_visit=lorisid_and_visitv)

    # 7. Upload the anonymized dicom file
    if(from_signal==SIG_ANONYMIZE_DATA ):
        if(DICOM_package is not None):
            if(DICOM_package.is_anonymized is not None):
                dispatcher.send(signal=SIG_UPLOAD_ANONYMIZED_DATA,
                                sender=postman,
                                anon_dicom_file=DICOM_package)
                #r = upload_anonymized_data(anon_dicom_file=anon_dicom_filev)

    # Error handling
    if(SIG_Error):
        # When errored, do something,
        if arglist is not None:
            print(arglist["Exception"])
            print("Printing function local arguments")
            print(arglist["locals"])
        traceback.print_exc(file=sys.stdout)
        # Save State/Transition related info to data store for recovery


# Connect events to handlers
dispatcher.connect(handle_event,            signal=SIGNAL,                      sender=dispatcher.Any)

dispatcher.connect(check_orthanc_srvr,      signal=SIG_INCOMING_DICOM,          sender=dispatcher.Any)
dispatcher.connect(get_MRN_from_DICOM,      signal=SIG_GET_MRN_FROM_DICOM,      sender=dispatcher.Any)
dispatcher.connect(check_mrn_exists,        signal=SIG_CHECK_MRN_EXISTS,        sender=dispatcher.Any)
dispatcher.connect(get_CNBPID_using_MRN,    signal=SIG_GET_CNBPID_USING_MRN,    sender=dispatcher.Any)
dispatcher.connect(get_DCCID_using_MRN,     signal=SIG_GET_DCCID_USING_MRN,   sender=dispatcher.Any)
dispatcher.connect(get_VISIT_using_MRN,     signal=SIG_GET_VISIT_USING_MRN,   sender=dispatcher.Any)

dispatcher.connect(assign_cnbpid_using_mrn, signal=SIG_GET_AND_ASSIGN_CNBPID_USING_MRN, sender=dispatcher.Any)

dispatcher.connect(anonymize_data,          signal=SIG_ANONYMIZE_DATA,          sender=dispatcher.Any)
dispatcher.connect(upload_anonymized_data,  signal=SIG_UPLOAD_ANONYMIZED_DATA,  sender=dispatcher.Any)
dispatcher.connect(assign_cnbpid,           signal=SIG_GENERATE_CNBPID,         sender=dispatcher.Any)
dispatcher.connect(get_DICOM_file,          signal=SIG_GET_DICOM_FILE,          sender=dispatcher.Any)
dispatcher.connect(postman,                 signal=SIG_HANDLE_DICOM_FILE,       sender=dispatcher.Any)
dispatcher.connect(postman,                 signal=SIG_TASK_COMPLETE,           sender=dispatcher.Any)
dispatcher.connect(postman,                 signal=SIG_Error,                   sender=dispatcher.Any)

# Fire events
def main( ):
    # Simulate a signal from Pacs
    pacs()

if __name__ == "__main__":
    main()
