#!/usr/local/bin/python

from DICOMTransit.DICOM.sort import DICOM_sort
from DICOMTransit.DICOM.decompress import DICOM_decompress
import os
from PythonUtils.PUFolder import recursive_list
from PythonUtils.PUList import filter_list_str
from PythonUtils.PUFile import flatcopy, unique_name
from DICOMTransit.DICOM.convert import DICOM_convert
from DICOMTransit.DICOM.validate import DICOM_validate
import glob
import logging
import sys
from pathlib import Path

logger = logging.getLogger()

# This class will dump every single thing 2D in a drive into a sorted destination.
# Primarily used to scrape together DICOM data to help generate ground truth .

class DICOM_scraper():


    def __init__(self, path_source, path_output):
        self.path_source = Path(path_source)
        self.path_output = Path(path_output)

        # Instantiate and fill the flist of files.
        self.list_files = []
        self.get_all_files()

        self.list_files = []
        self.filter_for_zip_files()


    def get_all_files(self):
        """
        get all possible files from the source.
        :return:
        """
        self.list_files = recursive_list(self.path_source)

    def filter_for_zip_files(self):
        """
        Filter the list to those only contain .ZIP.
        :return:
        """
        self.list_zips = filter_list_str(self.list_files, ".zip")


    def raw_sorted_decompressed(self):
        """
        FLATCOPY (with timestampe to avoid naming duplications) to a an output folder with raw prefix, then SORT THEM with proper protocole series acquisition number, then decompress everything within the folder.
        :param input_folder:
        :param output_folder:
        :return:
        """
        os.chdir(self.path_output)

        # Check then put into a folder .
        DICOM_sort.into_folder(self.path_source, self.path_output)

        # Decompress entire folder.
        DICOM_decompress.decompress_folder(self.path_output)

        # Sort into subfolder based on TE TR
        DICOM_sort.into_subfolder(self.path_output, self.path_output)


        logger.info("Sorted decompressed files Completed!")


    def unzip_all_zip_files(self):
        """
        Unzip all zip files
        :return:
        """


    def create_TRTE_folder(self, TR:str, TE:str):
        folder_TRTE = self.path_output.joinpath(Path(f"{TR}_{TE}"))
        os.mkdir(folder_TRTE)

    def get_TRTE(self, file):
        """
        Read the DICOM meta data and return its TRTE information for sorting.
        :param file:
        :return:
        """

