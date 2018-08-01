import sys
import json
import logging


logging.basicConfig(stream=sys.stdout, level=logging.INFO)
#logger = logging.getLogger('LORISQuery')


def number_extraction(string):
    """
    Return
    :param string:
    :return: a LIST of strings of number!
    """
    import re
    return re.findall(r'\d+', string)

if __name__ == '__main__':
    print(number_extraction("T4"))


def is_response_success(status_code, expected_code):
    """
    A simple function to determine the success of the status code
    :param status_code:
    :return: boolean value
    """
    if status_code == expected_code:
        return True
    else:
        return False


def check_json(data):
    """
    Check if the data input is JSON format compatible.
    :param data:
    :return:
    """
    try:
        JSON = json.loads(data)
        return True, JSON
    except ValueError:
        return False, None
    except Exception as e:
        return False, None
