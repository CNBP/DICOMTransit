import sys
import os
import json
import argparse
import getpass
import logging


logging.basicConfig(stream=sys.stdout, level=logging.INFO)
#logger = logging.getLogger('LORISQuery')


def number_extraction(string):
    import re
    return re.findall(r'\d+', string)

if __name__ == '__main__':
    print(number_extraction("T4"))

