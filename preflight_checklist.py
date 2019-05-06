import sys
import subprocess
import os
import time
import dotenv
import webbrowser

# Run this before anything.

# Some preliminary work to automaticly source the binaries. Not working yet. todo: testing in Win and Linux, for subprocesses.
sys.path.append("BinDependency/dcm2nii")
sys.path.append("BinDependency/dcm2niix")
sys.path.append("BinDependency/dcmtoolkit")
sys.path.append("Python/PythonUtils")
sys.path.append("Python/")
sys.path.append("Python/configurator")

os.environ["FLASK_APP"] = "configurator.dtconfigure"
os.environ["FLASK_ENV"] = "development"

# Check .env exist.
if not dotenv.load_dotenv():
    raise ValueError(".Env file not found. Contact DICOMTransit author!")

# Check production and development
import redcap.production
import redcap.development

# Creat the local configuration database if it hasn't already exist.
if not os.path.exists("LocalDB/dtconfigure.sqlite"):
    try:
        os.chdir('Python')
        subprocess.check_output(['flask', "--help"])
        subprocess.check_output(['flask', "init-db"])
    except Exception as e:
        raise ValueError("Could not initialize local database")

# fixme: gotta be platform independent. Need CentOS validation and Ubuntu.
DETACHED_PROCESS = 0x00000008


try:
    if sys.platform == "win32":
        pid = subprocess.Popen(['flask', "run"], creationflags=DETACHED_PROCESS).pid #todo: wrap this into a starter function to run at will.
    else:

        # linus might need
        #   sudo lsof -t -i tcp:5000 | xargs kill -9
        # to kill

        pid = subprocess.Popen(['flask', "run"]).pid

except Exception as e:
    raise ValueError

# Wait 5s before opening webbrower.
time.sleep(5)

webbrowser.open('http://127.0.0.1:5000/')  # Open the webpage
