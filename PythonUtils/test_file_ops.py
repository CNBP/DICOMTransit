import os
from PythonUtils.file import flatcopy, is_name_unique, full_file_path
from PythonUtils.folder import recursive_list, create
import unittest
import tempfile


class UT_file_ops(unittest.TestCase):
    @staticmethod
    def test_recursive_load():
        path = full_file_path(__file__)
        file_list = recursive_list(path)
        print(file_list)
        assert (
            len(file_list) > 5
        )  # the current files within the source code, it has at least 6 files in PythonUtils.

    @staticmethod
    def test_flatcopy():

        from pydicom.data import get_testdata_files

        file_list = get_testdata_files("*")

        # Local Computer DICOM test.
        # path1 = r"C:\FullyAnonymizedSubjects\anonymus\brain1"
        # file_list = recursive_list(path1)

        # Output DIR:
        with tempfile.TemporaryDirectory() as tmp_folder:
            flatcopy(file_list, tmp_folder, None)
            assert len(os.listdir(tmp_folder)) > 96

    @staticmethod
    def test_uniqueFileIdentifier():
        file = "Test.txt"
        open(file, "a").close()
        isUnique, unique_name = is_name_unique(file)
        assert not isUnique
        print(unique_name)
        os.remove(file)
        isUnique, unique_name = is_name_unique(file)
        assert isUnique


if __name__ == "__main__":
    # test_recursive_load()
    # test_copy_files_to_flat_folder()
    UT_file_ops.test_uniqueFileIdentifier()
