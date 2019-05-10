import sys
import logging
import os
import subprocess
import re
import logging
from pathlib import Path

logger = logging.getLogger()


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
            subprocess.check_output(
                [
                    "dcm2niix",
                    "-b",
                    "y",
                    "-z",
                    "y",
                    "-v",
                    "y",
                    "-f",
                    "%s_%p",
                    "-o",
                    output_folder,
                    input_folder,
                ]
            )

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
    def to_nii_mricron(input_folder, output_folder):
        """
        Invoke dcm2niix to carry out the proper conversion.
        :param input_folder: Input_folder can be a root folder or flat.
        :return:
        """

        if not os.path.exists(input_folder) or not os.path.exists(output_folder):
            return False, "Argument input or output folder does not exist"

        try:
            project_root = Path(__file__).parents[2]
            sys.path.append(project_root)
            path_dcm = os.path.join(project_root, "BinDependency", "dcm2nii")
            path_dcm2nii = os.path.join(path_dcm, "dcm2nii")

            # Only append path if it does not exist in there.
            if path_dcm not in os.environ["PATH"]:
                os.environ["PATH"] += os.pathsep + path_dcm

                os.chmod(path_dcm2nii, 0o777)

            logger.info(path_dcm2nii)

            # SUPER IMPORTANT! MAKE SURE dcm2niix by Chris Roden is in the system path!
            subprocess.check_output(
                [
                    "dcm2nii",
                    "-d",
                    "N",
                    "-p",
                    "N",
                    "-r",
                    "N",
                    "-g",
                    "N",
                    "-o",
                    output_folder,
                    input_folder,
                ],
                cwd=output_folder,
            )

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
        """
        Fix series numbers by setting them all to 0 led file format.
        :param input_folder:
        :return:
        """
        os.chdir(input_folder)
        for file in os.listdir(input_folder):
            if re.match(r"^[0-9]_", file):
                os.rename(file, "00" + file)
            elif re.match(r"^[0-9][0-9]_", file):
                os.rename(file, "0" + file)

    @staticmethod
    def handl_cube_conversion():
        """
        Special call to MRICRON isntead of MRICRONGL to handle Cube sequence conversion.
        :return:
        """
        raise NotImplementedError

    @staticmethod
    def to_minc(input_folder, output_folder):
        raise NotImplementedError

    @staticmethod
    def to_BIDS(input_folder, output_folder):
        raise NotImplementedError


if __name__ == "__main__":
    DICOM_convert.fix_series(r"C:\FullyAnonymizedSubjects\Wed3ConvertResult\raw_sorted")
    # DICOM_convert.to_nii(r"C:\FullyAnonymizedSubjects\2018-08-15_TestSubject2\Wed2-Decompressed", r"C:\FullyAnonymizedSubjects\2018-08-15_TestSubject2\Test")
