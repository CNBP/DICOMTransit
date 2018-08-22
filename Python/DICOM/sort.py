import sys
import logging
import os
import shutil
from DICOM.elements import DICOM_elements

logging.basicConfig(stream=sys.stdout, level=logging.INFO)

class DICOM_sort:

    @staticmethod
    def into_folder(input_folder, output_folder):
        """
        This function sort a input folder with or without sub layers and automaticlly flatten everything into a folder before then MOVING them into protocol based folder sorted by acquisition series.
        :param input_folder: Input_folder can be a root folder or flat.
        :return:
        """
        logger = logging.getLogger("DICOM sorting operation")

        #Element to check: Series number.

        from oshelper.file_operation import oshelper_files

        # Get files
        file_list = oshelper_files.recursive_list(input_folder)

        if not os.path.isdir(output_folder):
            os.mkdir(output_folder)


        # copy them to a flat structure to the output folder.
        oshelper_files.copy_files_to_flat_folder(file_list, output_folder)

        # decompress them if necessary.
        # oshelper_files.decompress_folder(output_folder)

        # Get files list again.
        file_list = oshelper_files.recursive_list(output_folder)

        exception_encountered = 0

        # File here should be the FULL path.
        for file in file_list:

            success1, SeriesNumber = DICOM_elements.retrieve(file, "SeriesNumber")

            success2, SeriesDescription = DICOM_elements.retrieve(file, "SeriesDescription")

            if not success1 or not success2:
                logger.info("Skipped file with no acquisition series information: " + file)
                exception_encountered = exception_encountered + 1
                continue

            # Check MRI Series folder exists
            DestinationFolder = str(SeriesNumber) + '-' + SeriesDescription
            DestinationFolder = DestinationFolder.replace(' ', '_')
            DestinationFolder = DestinationFolder.replace(':', '_')
            DestinationFolder = DestinationFolder.replace(r'/', '_')
            DestinationFolder = DestinationFolder.replace(r'\\', '_')

            # Make destination folder if not exist.
            os.chdir(output_folder)
            if not os.path.exists(DestinationFolder):
                os.mkdir(DestinationFolder)

            # Get file name.
            _, filename = os.path.split(file)

            shutil.move(file, os.path.join(DestinationFolder, filename))
        logger.info("Total error encoutnered: " + str(exception_encountered))


if __name__ == "__main__":
    DICOM_sort.into_folder("C:\FullyAnonymizedSubjects\StreamLineTest", "C:\FullyAnonymizedSubjects\StreamLineTest\Test")
