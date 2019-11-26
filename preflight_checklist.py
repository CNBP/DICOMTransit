import sys
import subprocess
import os
import time
import dotenv
import webbrowser
from dotenv import load_dotenv
from datagator.config_datagator import get_DataGator_DataBaseURI


# NOTE! This is the setup script to ensure all environment are properly configured and ready to og.
# Run this before anything.


path_module = os.path.dirname(os.path.realpath(__file__))

# Some preliminary work to automaticly source the binaries. Not working yet. @todo: testing in Win and Linux, for subprocesses.
sys.path.append(f"{path_module}/BinDependency/dcm2nii")
sys.path.append(f"{path_module}/BinDependency/dcm2niix")
sys.path.append(f"{path_module}/BinDependency/dcmtoolkit")
sys.path.append(f"{path_module}/datagator")
sys.path.append(f"{path_module}/PythonUtils")
sys.path.append(f"{path_module}/DICOMTransit/")

# Check .env exist.
if not dotenv.load_dotenv():
    raise ValueError(
        ".Env file not found. Contact DICOMTransit author!"
    )  # fixme: be more helpful here.

# Path of the database URL is obtained from the environment or using the default string.
SQLALCHEMY_DATABASE_URI = get_DataGator_DataBaseURI()

os.chdir("DataGator")
os.environ["FLASK_APP"] = "index.py"
os.environ["FLASK_ENV"] = "development"

# Check production and development
# import redcap.production
# import redcap.development

# Creat the local configuration database if it hasn't already exist.
if not os.path.exists(SQLALCHEMY_DATABASE_URI):
    print(f"Flask database path: {SQLALCHEMY_DATABASE_URI}")
    try:
        subprocess.check_output(["flask", "db", "upgrade"])
    except Exception as e:
        raise ValueError("Could not initialize and update the local database!")

# fixme: gotta be platform independent. Need CentOS validation and Ubuntu.
DETACHED_PROCESS = 0x00000008


try:
    if sys.platform == "win32":
        pid = subprocess.Popen(
            ["flask", "run"], creationflags=DETACHED_PROCESS
        ).pid  # @todo: wrap this into a starter function to run at will.
    else:

        # linux might need
        #   sudo lsof -t -i tcp:5000 | xargs kill -9
        # to kill

        pid = subprocess.Popen(["flask", "run"]).pid

except Exception as e:
    raise ValueError

# Wait 5s before opening webbrower.
time.sleep(5)

webbrowser.open("http://127.0.0.1:5000/")  # Open the webpage
