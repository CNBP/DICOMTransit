import json
import logging
import requests

from DICOMTransit.LORIS.helper import LORIS_helper
from DICOMTransit.settings import config_get
from urllib.parse import urljoin

logger = logging.getLogger()


class LORIS_instrument:

    @staticmethod
    def upload_entry():




# Only executed when running directly.
if __name__ == "__main__":
    # print(login())
    # getCNBP("projects")
    Success, token = LORIS_query.login()
    # print("Test complete")
