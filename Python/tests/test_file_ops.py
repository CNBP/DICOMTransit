import os
from ..file_operation import recursive_list_files, copy_files_to_flat_folder


def test_recursive_load():
    file_list = recursive_list_files(os.getcwd())
    print(file_list)
    assert len(file_list) > 87

def test_copy_files_to_flat_folder():

    from pydicom.data import get_testdata_files
    file_list = get_testdata_files("*")

    # Local Computer DICOM test.
    # path1 = r"C:\FullyAnonymizedSubjects\anonymus\brain1"
    # file_list = recursive_list_files(path1)

    # Output DIR:
    tmp_folder = os.getcwd()
    folder_name = "files"
    folder = os.path.join(tmp_folder, folder_name)

    # Create folder before copying.
    os.mkdir(folder)
    copy_files_to_flat_folder(file_list, folder)

    import shutil
    # Remove that folder now.
    shutil.rmtree(folder)



if __name__ == '__main__':
    test_recursive_load()
    test_get_file_name()
    test_copy_files_to_flat_folder()