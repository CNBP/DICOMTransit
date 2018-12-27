import sys
import json
import requests
import development as environment
import logging

redcap_api_url = environment.REDCAP_API_URL
logging.basicConfig(stream=sys.stdout, level=logging.INFO)

class redcap_query():

    @staticmethod
    def post(token_project, record_text):
        """
        Post a record based content to RedCap using the project API token provided.
        :param logger:
        :param record_text:
        :param token_project:
        :return:
        """
        # record_text=record_text[:-1]
        logger = logging.getLogger(__name__)

        # Log the actual JSON posted.
        logger.info(json.dumps(record_text, ensure_ascii=False))

        # Construct payload
        payload = {'token': token_project, 'format': 'json', 'content': 'record', 'type': 'flat'}

        # Load the JSON content
        to_import_json = json.dumps([record_text], separators=(',', ':'))

        # Update payload content.
        payload['data'] = to_import_json

        # Record the response.
        response = requests.post(redcap_api_url, data=payload)
        logger.info(response.json())