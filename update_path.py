import sys
import subprocess
import os

# Some preliminary work to automaticly source the binaries. Not working yet. todo: testing in Win and Linux, for subprocesses.
sys.path.append("BinDependency/dcm2niix")
sys.path.append("BinDependency/dcmtoolkit")
sys.path.append("Python/PythonUtils")
sys.path.append("Python/")
sys.path.append("Python/configurator")

os.environ["FLASK_APP"] = "configurator.dtconfigure"
os.environ["FLASK_ENV"] = "development"

try:
    subprocess.check_output(['flask', "init-db"]) #todo: make sure this process is ONE time only. Check existing db.
except Exception as e:
    raise ValueError

# fixme:
DETACHED_PROCESS = 0x00000008
try:
    pid=subprocess.Popen(['flask', "run"], creationflags=DETACHED_PROCESS).pid #todo: wrap this into a starter function to run at will.
except Exception as e:
    raise ValueError
