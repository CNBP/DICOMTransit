import pydicom
import sys
import os
import argparse
import getpass
import logging

logging.basicConfig(stream=sys.stdout, level=logging.INFO)

def DICOM_decompressor(path):
    """
    Decompress the dicoms in case they are compressed.
    :param path:
    :return:
    """


def DICOM_anonymizer(path, PSCID):
    """
    Anonymize the DICOMS to remove any identifiable information
    :param path:
    :param PSCID:
    :return:
    """


def DICOM_recursive_loader(path, action):
    """
    load all the files, validate and then pass to decompress or anonimize.
    :param path:
    :return:
    """

def DICOM_validator(file_path):
    """
    validate to check if the DICOM file is an actual DICOM file.
    :param file_path:
    :return: boolean value.
    """