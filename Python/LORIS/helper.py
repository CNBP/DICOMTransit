import sys
import json
import logging


logging.basicConfig(stream=sys.stdout, level=logging.INFO)
#logger = logging.getLogger('LORISQuery')

class LORIS_helper:

    @staticmethod
    def number_extraction(string):
        """
        Return
        :param string:
        :return: a LIST of strings of number!
        """
        import re
        return re.findall(r'\d+', string)

    @staticmethod
    def is_response_success(status_code, expected_code):
        """
        A simple function to determine the success of the status code
        :param status_code:
        :param expected_code:
        :return: boolean value
        """
        if status_code == expected_code:
            return True
        else:
            return False

    @staticmethod
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


if __name__ == '__main__':
    print(LORIS_helper.number_extraction("T4"))
