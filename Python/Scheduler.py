import sys
import os
import argparse
import getpass
import logging

logging.basicConfig(stream=sys.stdout, level=logging.INFO)



def DICOMMonitor():
    '''
    Monitor the DICOM folders of Orthanc output.
    :
    '''
    logger = logging.getLogger('DICOMMonitor')

    default_locations = "example path"
    default_monitoring_duration = 60 #seconds
    default_DCMTK = "DCMTK path"
    default_os = "ubuntu"

    #Check for all the new batch if they contain any of the known existing DICOM string.











if __name__ == '__main__':

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('-u', '--user', dest='email', type=str, help='Username/Email used for login')
    parser.add_argument('-p', '--production', dest='production', action='store_true', help='Example of boolean arg')
    parser.add_argument('-o', '--option', dest='option', type=str, help='Example of str arg')

    parser.add_argument('file', metavar='file', type=str, help='Example of a positional argument')

    args = parser.parse_args()
    logger.info('--------------')

    # Never ask for a password in command-line. Manually ask for it here
    password = getpass.getpass()

    logger.info('Hello World!')
