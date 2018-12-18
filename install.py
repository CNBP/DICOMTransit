import subprocess
import sys

def install_dependencies():
    # Install all dependencies.
    subprocess.call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])

    # Upgrade Pip
    subprocess.call([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])

if __name__ == "__main__":
    install_dependencies()