import subprocess
import sys


def install_dependencies():
    # Install all dependencies.
    subprocess.call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])

    # Upgrade Pip
    subprocess.call([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])

    # fixme: install configurator:
    # Python / configurator / setup.py

    # fixme: ubuntu need python3-dev to install properly. Might also require CentOS
    # Setup path dependency for Python folder.
    # sudo apt-get install python3-dev required for pyodbc

    # fixme: CenTOS check.
    subprocess.call([sys.executable, "setup.py", "install"])

    # fixme: CenTOS check.
    subprocess.call([sys.executable, "Python\configurator\setup.py", "install"])


if __name__ == "__main__":
    install_dependencies()
