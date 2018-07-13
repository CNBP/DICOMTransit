import sys
import os
import argparse
import getpass
import logging
import requests
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logger = logging.getLogger('LORISQuery')


#This function should obtain the tokens
def login():

    load_dotenv()

    username = os.getenv("LORISusername")
    password = os.getenv("LORISpassword")
    url = os.getenv("LORISurl")
    updatedurl = url+"login"
    updatedurl = 'http://httpbin.org/post'


    #r = requests.post(updatedurl, data={'username': username, 'password': password})
    r = requests.post(updatedurl, auth=(username, password))
    print(r.status_code, r.reason)
    print(r.json())
    return r.json()

# Only executed when running directly.
if __name__ == '__main__':
    login()