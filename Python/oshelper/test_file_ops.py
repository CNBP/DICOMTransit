import os
from oshelper.file_operation import oshelper_files
import unittest

class UT_file_ops(unittest.TestCase):

    @staticmethod
    def test_recursive_load():
        file_list = oshelper_files.recursive_list(os.getcwd())
        print(file_list)
        assert len(file_list) > 56 # the current files within the source code

    @staticmethod
    def test_copy_files_to_flat_folder():

        from pydicom.data import get_testdata_files
        file_list = get_testdata_files("*")

        # Local Computer DICOM test.
        # path1 = r"C:\FullyAnonymizedSubjects\anonymus\brain1"
        # file_list = recursive_list(path1)

        # Output DIR:
        tmp_folder = os.getcwd()
        folder_name = "files"
        folder = os.path.join(tmp_folder, folder_name)

        # Create folder before copying.
        os.mkdir(folder)
        oshelper_files.copy_files_to_flat_folder(file_list, folder)

        import shutil
        # Remove that folder now.
        shutil.rmtree(folder)

    @staticmethod
    def test_uniqueFileIdentifier():
        file = "Test.txt"
        open(file, 'a').close()
        isUnique, unique_name = oshelper_files.is_name_unique(file)
        assert not isUnique
        print(unique_name)
        os.remove(file)
        isUnique, unique_name = oshelper_files.is_name_unique(file)
        assert isUnique


if __name__ == '__main__':
    #test_recursive_load()
    #test_copy_files_to_flat_folder()
    UT_file_ops.test_uniqueFileIdentifier()