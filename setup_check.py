import subprocess
import logging
import sys
from dotenv import load_dotenv

logger = logging.getLogger()


def nii2nifty_check():
    """
    Sanity check function that ensure the dcm2niix executable is found in the system OS path!
    :return:
    """

    sys.path.append("/opt/mricrogl/")

    # sys.path.append("/opt/DCMTK")
    try:
        logger.debug("Nifty Check")

        # SUPER IMPORTANT! MAKE SURE dcm2niix by Chris Roden is in the system path!
        subprocess.check_output(["dcm2niix", "-h"])

    # When dcmdjpeg has errors
    except subprocess.CalledProcessError as e:
        logger.info(e)
        ErrorMessage = "File type not compatible"
        logger.info(ErrorMessage)
        return False, ErrorMessage
    except Exception as e:
        logger.info(e)
        ErrorMessage = "dcm2niix decompression call failed! Make sure dcm2niix is in your SYSTEM OS PATH and then check your input file"
        logger.info(ErrorMessage)
        return False, ErrorMessage

    return True, "nii2nifty dependency check past!"


def env_check():
    """
    Ensure a .env file is SOMEWHERE.
    :return:
    """
    return load_dotenv()


def dcmdjpeg_check():

    try:
        # SUPER IMPORTANT! MAKE SURE DCMDJPEG is in the system path!
        subprocess.check_output(["dcmdjpeg"])
    except Exception as e:
        logger.info(e)
        ErrorMessage = "dcmdjpeg decompression call failed! Make sure dcmdjpeg is in your SYSTEM OS PATH and then check your input file"
        logger.info(ErrorMessage)
        return False, ErrorMessage

    return True, "dcmdjpeg dependency check past!"


def pythonutil_check():
    """
    Check to see if we can import from PythonUtils
    :return:
    """
    import PythonUtils.PUFolder
    import PythonUtils.PUFile

    return True


if __name__ == "__main__":
    import preflight_checklist

    assert nii2nifty_check()[0]
    assert dcmdjpeg_check()[0]
    assert env_check()
    pythonutil_check()
