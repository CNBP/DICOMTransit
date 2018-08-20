import sys
import logging

logging.basicConfig(stream=sys.stdout, level=logging.INFO)


class oshelper_scheduler:

    @staticmethod
    def DICOMMonitor():
        """
        Monitor the DICOM folders of Orthanc output.
        :return: 
        """                
        logger = logging.getLogger('DICOMMonitor')

        default_locations = "example path"
        default_monitoring_duration = 60 #seconds
        default_DCMTK = "DCMTK path"
        default_os = "ubuntu"

        #Check for all the new batch if they contain any of the known existing DICOM string.


# if __name__ == '__main__':
