import sys, traceback

import os
import logging
import orthanc.API
import DICOM.API
from PythonUtils.folder import recursive_list
from pydispatch import dispatcher
SIGNAL = 'my-first-signal'
SIG_Error = 'Generic Error'
SIG_INCOMING_DICOM = 'incoming-dicom'
SIG_GET_DICOM_FILE = 'get-dicom-file'
SIG_GET_MRN_FROM_DICOM = 'get-mrn-from-dicom'
SIG_CHECK_MRN_EXISTS = 'check-mrn-exists'
SIG_GET_CNBPID_USING_MRN = 'get-cnbpid-using-mrn'
SIG_GET_AND_ASSIGN_CNBPID_USING_MRN = 'get-and-assign-cnbpid-using-mrn'
SIG_ASSIGN_CNBPID = 'assign-cnbpid'
SIG_MRN_DOES_NOT_EXIST = 'mrn-does-not-exist'
SIG_GET_LORISID_AND_VISIT = 'get-lorsid-and-visit'
SIG_ANONYMIZE_DATA = 'anonymize-data'
SIG_UPLOAD_ANONYMIZED_DATA = 'upload-anonymized-data'
SIG_HANDLE_DICOM_FILE = 'handle-dicom-file'
SIG_TASK_COMPLETE = 'task-complete'

""" Function to handle events """
def handle_event( signal, sender ):
    """Simple event handler"""
    print (signal, ' to handle_event was sent by', sender)

def pacs():
    """Simple event trigger"""
    pacs_sender = "pacs_sender"
    dispatcher.send( signal=SIG_INCOMING_DICOM, sender=pacs_sender )

def scanner ( signal, sender ):
    """Simple event handler"""
    print (signal, ' to scanner was sent by', sender)

def check_orthanc_srvr (signal, sender):
    """
    Check orthanc server using the orthanc module and download the files.
    :param signal:
    :param sender:
    :return:
    """
    print (signal, ' to check_orthanc_srvr was sent by', sender)
    dispatcher.send(signal=SIG_GET_DICOM_FILE, sender=check_orthanc_srvr)

def check_mrn_exists ( signal, sender ):
    """Simple event handler"""
    """Currently not used. i.e nothing fires its event"""
    print ('Signal is', signal)
    print ('Signal to check_mrn_exists was sent by', sender)
    # Pretend that MRN found so assign CNBPID
    cnbpidv = 999
    sa = 'hello'
    dispatcher.send( SIG_ASSIGN_CNBPID, sender=sa, cnbpid=cnbpidv )

def get_mrn_from_dicom ( signal=None, sender=None, dicom_file=None ):
    """Simple event handler"""
    print ('Signal is', signal)
    print ('Signal to get_mrn_from_dicom was sent by', sender)
    dicom_file.mrn = 'This is a medical record number'
    dispatcher.send( signal=SIG_TASK_COMPLETE, sender=get_mrn_from_dicom,
                    dicomFile=dicom_file,from_signal=signal)

def get_and_assign_cnbpid_using_mrn ( signal=None, sender=None, mrn=None, dicom_file=None ):
    """Simple event handler"""
    print ('Signal is', signal)
    print ('Signal to get_and_assign_cnbpid_using_mrn was sent by', sender)
    # Get CNBPID based on MRN
    # THE CNBPDID
    # Assign retrieved MRN
    dicom_file.cnbpid = 999
    dispatcher.send( signal=SIG_TASK_COMPLETE,
                    sender=get_and_assign_cnbpid_using_mrn,
                    from_signal=signal,dicomFile=dicom_file)

def get_lorisid_and_visit ( signal=None, sender=None, dicom_file=None, cnbpid=None ):
    """Simple event handler"""
    print ('Signal is', signal)
    print ('Signal to get_lorisid_and_visit was sent by', sender)
    # Get Loris ID and Visit based on CNBPID
    # Send signal that result is ready
    dicom_file.lorisid = 0
    dicom_file.visit = 0
    dispatcher.send( signal=SIG_TASK_COMPLETE, sender=get_lorisid_and_visit,
                    from_signal=signal, dicomFile=dicom_file)

def get_dicom_file( signal=None, sender=None ):
    """Simple event handler"""
    print ('Signal is', signal)
    print ('Signal to get_dicom_file was sent by', sender)

    # Get the list of subjects
    subjects_list = orthanc.API.get_list_of_subjects()

    for subject in subjects_list:

        try:
            dicom_folder = orthanc.API.get_subject_zip(subject)

            dicom_package = DICOMPackage(dicom_folder)
            dispatcher.send( signal=SIG_HANDLE_DICOM_FILE, sender=get_dicom_file,
                        dicomFile=dicom_package)
        except Exception as ex:
            #traceback.print_exc(file=sys.stdout)
            dispatcher.send(signal=SIG_Error, sender=get_dicom_file, arglist={"Exception": ex})



def assign_cnbpid ( signal=None, sender=None, mrn=None, cnbpid=None, dicom_file=None ):
    """Simple event handler"""
    print ('Signal is', signal)
    print ('Signal to assign_cnbpid was sent by', sender)
    print ('cnbpid := ', cnbpid)
    # Assign cnbpid. This function is no longer necessary because of
    # get_cnbpid_from_mrn it seems. The latter functions assigns the value 
    dicom_file.cnbpid
    # Send signal that result is ready
    dispatcher.send( signal=SIG_TASK_COMPLETE, sender=assign_cnbpid,
                    from_signal=signal,dicomFile=dicom_file)

def anonymize_data ( signal=None, sender=None, dicom_file=None):
    """Simple event handler"""
    print ('Signal is', signal)
    print ('Signal to anonymize_data was sent by', sender)
    # dicom_folder.dicom_folder = 'an anonymized dicom file'

    DICOM.API.anonymize_files(dicom_file.get_dicom_files())
    dicom_file.is_anonymized = 1
    dispatcher.send( signal=SIG_TASK_COMPLETE, sender=anonymize_data,
                    from_signal=signal, dicomFile=dicom_file)

def upload_anonymized_data ( signal=None, sender=None, anon_dicom_file=None ):
    """Simple event handler"""
    print ('Signal is', signal)
    print ('Signal to upload_anonymized_data was sent by', sender)
    # Upload anonymized file
    dispatcher.send( signal=SIG_TASK_COMPLETE,
                    sender=upload_anonymized_data,from_signal=signal,
                    dicomFile=anon_dicom_file)

"""
Postman directs the appropriate action to take depending on what state
processing is in
Postman is then sent a signal by tasks that have finished with the results
@arglist ; A dictionary
@dicomFile ; A DICOM file
@signal ; Signal, relayed by PyDispatch
@sender ;  Sender of the signal, relayed by PyDispatch
@from_signal ; The signal that precipitated the value in 'signal'
"""
def postman ( signal=None, sender=None, from_signal=None, dicomFile=None, arglist=None ):
    print ('Signal is', signal)
    print ('Signal to postman was sent by', sender)
    # Check that dicomFile is an instance of DICOMPackage
    # Based on the signal, pass control to replyto
    # if(not isinstance(dicomFile, DICOMPackage)):
    #     print ('dicomFile not a DICOMPackage object. Exiting ...')
    #     return 0

    # 1a. Get dicom file
    if( signal==SIG_HANDLE_DICOM_FILE ):
        if( dicomFile is not None):
            # 1b. Get mrn from DICOM file
            if(dicomFile.dicom_folder != None ):
                print(dicomFile.dicom_folder)
                dispatcher.send( signal=SIG_GET_MRN_FROM_DICOM,
                                sender=postman,dicom_file=dicomFile)
                #get_mrn_from_dicom(dicom_folder=dicom_filev)

    # 2., 3. Get CNBPID using MRN
    if(from_signal==SIG_GET_MRN_FROM_DICOM):
        if(dicomFile is not None):
            if(dicomFile.mrn is not None):
                dispatcher.send( signal=SIG_GET_AND_ASSIGN_CNBPID_USING_MRN,
                                sender=postman, dicom_file=dicomFile)
                #get_and_assign_cnbpid_using_mrn(mrn=mrnv,dicom_folder=dicom_filev)

    # 4. Assign cnbpid (to dicom file?)
    if(from_signal==SIG_GET_CNBPID_USING_MRN):
        if(dicomFile is not None):
            if(dicomFile.cnbpid is not None):
                dispatcher.send( signal=SIG_ASSIGN_CNBPID, sender=postman,
                                dicom_file=dicomFile)
                #assign_cnbpid(cnbpid=cnbpidv,dicom_folder=dicom_filev)

    # 5. Get lorisid and visit
    if(from_signal==SIG_GET_AND_ASSIGN_CNBPID_USING_MRN):
        if(dicomFile is not None):
            if(dicomFile.cnbpid is not None):
                dispatcher.send( signal=SIG_GET_LORISID_AND_VISIT,
                                sender=postman, dicom_file=dicomFile)
                #get_lorisid_and_visit( cnbpid=cnbpidv )

    # 6. Anonymize dicom file
    if(from_signal==SIG_GET_LORISID_AND_VISIT ):
        if(dicomFile is not None):
            if(dicomFile.lorisid is not None and dicomFile.visit is not None):
                # 6. Anonymize the dicom file
                dispatcher.send( signal=SIG_ANONYMIZE_DATA,
                                sender=postman, dicom_file=dicomFile)
                #anonymize_data(dicom_folder=dicom_filev,
                #              lorisid_and_visit=lorisid_and_visitv)

    # 7. Upload the anonymized dicom file
    if(from_signal==SIG_ANONYMIZE_DATA ):
        if(dicomFile is not None):
            if(dicomFile.is_anonymized is not None):
                dispatcher.send( signal=SIG_UPLOAD_ANONYMIZED_DATA,
                                sender=postman,
                                anon_dicom_file=dicomFile)
                #r = upload_anonymized_data(anon_dicom_file=anon_dicom_filev)
    if(SIG_Error):
        # When errored, do something,
        if arglist is not None:
            print(arglist["Exception"])
        traceback.print_exc(file=sys.stdout)

"""Dicom file class """
class DICOMPackage:
    def __init__(self, dicom_folder=None):
        self.dicom_folder = dicom_folder
        self.cnbpid = None
        self.lorisid = None
        self.visit = None
        self.mrn = None
        self.is_anonymized = 0

    def get_dicom_files(self):
        return recursive_list(self.dicom_folder.name)



# Connect events to handlers
dispatcher.connect( handle_event, signal=SIGNAL,sender=dispatcher.Any )
dispatcher.connect(check_orthanc_srvr, signal=SIG_INCOMING_DICOM, sender=dispatcher.Any)
dispatcher.connect( get_mrn_from_dicom, signal=SIG_GET_MRN_FROM_DICOM,sender=dispatcher.Any )
dispatcher.connect( check_mrn_exists, signal=SIG_CHECK_MRN_EXISTS,sender=dispatcher.Any )
#dispatcher.connect( get_cnbpid_using_mrn, signal=SIG_GET_CNBPID_USING_MRN,sender=dispatcher.Any )
dispatcher.connect( get_and_assign_cnbpid_using_mrn,
                   signal=SIG_GET_AND_ASSIGN_CNBPID_USING_MRN,sender=dispatcher.Any )
dispatcher.connect( get_lorisid_and_visit, signal=SIG_GET_LORISID_AND_VISIT,sender=dispatcher.Any )
dispatcher.connect( anonymize_data, signal=SIG_ANONYMIZE_DATA,sender=dispatcher.Any )
dispatcher.connect( upload_anonymized_data, signal=SIG_UPLOAD_ANONYMIZED_DATA,sender=dispatcher.Any )
dispatcher.connect( assign_cnbpid, signal=SIG_ASSIGN_CNBPID,sender=dispatcher.Any )
dispatcher.connect( get_dicom_file, signal=SIG_GET_DICOM_FILE,sender=dispatcher.Any )
dispatcher.connect( postman, signal=SIG_HANDLE_DICOM_FILE,sender=dispatcher.Any )
dispatcher.connect( postman, signal=SIG_TASK_COMPLETE,sender=dispatcher.Any )
dispatcher.connect(postman, signal=SIG_Error, sender=dispatcher.Any)

# Fire events
def main( ):
    # Simulate a signal from Pacs
    pacs()

if __name__ == "__main__":
    main()
