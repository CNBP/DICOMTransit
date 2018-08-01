import logging
from LORIS.candidates import createCandidateCNBP
from LORIS.query import login
import os
from subprocess import call
import sys
from dotenv import load_dotenv

def test_create_subject():
    logger = logging.getLogger('UT_LORIS_DCCID_check')
    response_success, token = login()

    if not response_success:
        raise ConnectionError

    PSCID = "CNBP9871234"

    success, CandID = createCandidateCNBP(token, PSCID)

    load_dotenv()

    ProxyIP = os.getenv("ProxyIP")
    ProxyUsername = os.getenv("ProxyUsername")
    ProxyPassword = os.getenv("ProxyPassword")
    LORISHostPassword = os.getenv("LORISHostPassword")
    LORISHostUsername = os.getenv("LORISHostUsername")
    LORISHostIP = os.getenv("LORISHostIP")
    DeletionScript = os.getenv("DeletionScript")

    #Export some variables for subsequent deletion clean script against production database (yes... because we could not automate LORIS development...):
    command_string =["sshpass", "-p", ProxyPassword, "ssh", ProxyUsername + "@" + ProxyIP, "-t", "sshpass", "-p", LORISHostPassword, "ssh", "-L", "3001:localhost:22",
          LORISHostUsername + "@" + LORISHostIP, "php", DeletionScript, "delete_candidate", str(CandID), PSCID, "confirm"]

    logger.info(command_string)
    if 'TRAVIS' in os.environ:
        #call(command_string)

if __name__ == "__main__":
    test_create_subject()