import os
from file_operation import recursive_list_files, get_file_name


def test_recursive_load():
    file_list = recursive_list_files(os.getcwd())
    print(file_list)
    assert len(file_list) > 1000

def test_get_file_name():
    path1 = "C:\Windows\Sysmte32\Crapware"
    path2 = "C:\Windows\Sysmte32\Crapware\\"
    path3 = "C:\Windows\Sysmte32\Crapware\Shittyexe.exe"
    path4 = "/bin/dir/var/mnt/usr/queenbee"
    path5 = "/bin/dir/var/mnt/usr/queenbee/"
    path6 = "/bin/dir/var/mnt/usr/queenbee/notmyproblem.tif"

    assert get_file_name(path1) == "Crapware"
    assert get_file_name(path2) == ''
    assert get_file_name(path3) == "Shittyexe.exe"
    assert get_file_name(path4) == "queenbee"
    assert get_file_name(path5) == ''
    assert get_file_name(path6) == "notmyproblem.tif"

if __name__ == '__main__':
    test_recursive_load()
    test_get_file_name()