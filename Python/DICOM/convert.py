import sys
import logging
import os
import subprocess
import re
from PythonUtils.file import current_funct_name

class DICOM_convert:

    @staticmethod
    def to_nii(input_folder, output_folder):
        """
        Invoke dcm2niix to carry out the proper conversion.
        :param input_folder: Input_folder can be a root folder or flat.
        :return:
        """

        if not os.path.exists(input_folder) or not os.path.exists(output_folder):
            return False, "Argument input or output folder does not exist"

        try:

            # SUPER IMPORTANT! MAKE SURE dcm2niix by Chris Roden is in the system path!
            subprocess.check_output(['dcm2niix',
                                     '-b', 'y',
                                     '-z', 'y',
                                     '-v', 'y',
                                     '-f', "%s_%p",
                                     '-o', output_folder,
                                    input_folder])

        # When dcmdjpeg has errors
        except subprocess.CalledProcessError as e:
            logger.info(e)
            ErrorMessage = "File type not compatible"
            logger.info(ErrorMessage)
            return False, ErrorMessage
        except Exception as e:
            logger.info(e)
            ErrorMessage = "dcm2niix decompression call failed! Make sure dcm2niix is in your SYSTEM OS PATH and then check your input file:"
            logger.info(ErrorMessage)
            return False, ErrorMessage

        return True, "All conversion successfully finished."

    @staticmethod
    def fix_series(input_folder):
        os.chdir(input_folder)
        for file in os.listdir(input_folder):
            if re.match(r'^[0-9]_', file):
                os.rename(file, '00'+ file)
            elif re.match(r'^[0-9][0-9]_', file):
                os.rename(file, '0'+ file)

    @staticmethod
    def to_minc(input_folder, output_folder):
        raise NotImplementedError

    @staticmethod
    def to_BIDS(input_folder, output_folder):
        raise NotImplementedError


if __name__ == "__main__":
    DICOM_convert.fix_series(r"C:\FullyAnonymizedSubjects\Wed3ConvertResult\raw_sorted")
    #DICOM_convert.to_nii(r"C:\FullyAnonymizedSubjects\2018-08-15_TestSubject2\Wed2-Decompressed", r"C:\FullyAnonymizedSubjects\2018-08-15_TestSubject2\Test")
