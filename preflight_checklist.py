import sys
import subprocess
import os
import time
import webbrowser
from dotenv import load_dotenv, find_dotenv
from datagator.config import get_DataGator_DataBaseURI
from pathlib import Path


# NOTE! This is the setup script to ensure all environment are properly configured and ready to og.
# Run this before anything.

path_module = Path(os.path.dirname(os.path.realpath(__file__)))

# Some preliminary work to automaticly source the binaries. Not working yet. @todo: testing in Win and Linux, for subprocesses.
sys.path.append(f"{path_module}/BinDependency/dcm2nii")
sys.path.append(f"{path_module}/BinDependency/dcm2niix")
sys.path.append(f"{path_module}/BinDependency/dcmtoolkit")
sys.path.append(f"{path_module}/datagator")
sys.path.append(f"{path_module}/PythonUtils")
sys.path.append(f"{path_module}/DICOMTransit/")


load_dotenv(find_dotenv())

# Path of the database URL is obtained from the environment or using the default string.
SQLALCHEMY_DATABASE_URI = get_DataGator_DataBaseURI()

os.chdir("datagator")

# Check datagator .env exist, if not exist, creates it.
path_datagator_env = path_module / "datagator" / ".env"
if not path_datagator_env.exists():
    print("DataGator .env does not appear to exist. Create empty place holder.")
    path_datagator_env.touch()

# Check dictomtransit .env exist.
path_dicomtransit_env = path_module / ".env"
if not path_dicomtransit_env.exists():
    print("DICOMTransit .env does not appear to exist. Create empty place holder.")
    path_dicomtransit_env.touch()
    with open(path_dicomtransit_env, "w") as file_env:
        file_env.write(
            f"datagator_database={path_module / 'LocalDB' / 'dtconfigure.sqlite'}\nconfig_table=configuration"
        )
        print(
            "DICOMTransit .env updated with the default relative 'LocalDB' folder path, and configuration table."
        )
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
