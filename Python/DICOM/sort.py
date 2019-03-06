import logging
import os
import shutil
from DICOM.elements import DICOM_elements
from DICOM.validate import DICOM_validate
from tqdm import tqdm

logger = logging.getLogger()

class DICOM_sort:

    @staticmethod
    def into_folder(input_folder, output_folder):
        """
        This function sort a input folder with or without sub layers and automaticlly flatten everything into a folder before then MOVING them into protocol based folder sorted by acquisition series.
        :param input_folder: Input_folder can be a root folder or flat.
        :return:
        """


        #Element to check: Series number.

        from PythonUtils.file import flatcopy
        from PythonUtils.folder import recursive_list

        # Get files
        file_list = recursive_list(input_folder)

        if not os.path.isdir(output_folder):
            os.mkdir(output_folder)


        # copy them to a flat structure to the output folder.
        flatcopy(file_list, output_folder, DICOM_validate.file)

        # decompress them if necessary.
        # oshelper_files.decompress_folder(output_folder)

        # Get files list again.
        file_list = recursive_list(output_folder)

        exception_encountered = 0

        logger.info("Sorting files into folders:")

        # File here should be the FULL path.
        for file in tqdm(file_list, position=0):

            success1, SeriesNumber = DICOM_elements.retrieve(file, "SeriesNumber")

            success2, SeriesDescription = DICOM_elements.retrieve(file, "SeriesDescription")

            if not success1 or not success2:
                logger.info(f"Skipped file with no acquisition series information: {file}")
                exception_encountered = exception_encountered + 1
                continue

            # Check MRI Series folder exists
            DestinationFolder = str(SeriesNumber) + '_' + SeriesDescription
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
        logger.info(f"Total error encountered: {str(exception_encountered)}")


if __name__ == "__main__":
    DICOM_sort.into_folder("C:\FullyAnonymizedSubjects\StreamLineTest", "C:\FullyAnonymizedSubjects\StreamLineTest\Test")
