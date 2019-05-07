import os, sys

def setup():
    """
    OS neutral approach to add the dependency path to the OS enviromnet to ensure the SUBPROCESSES can access them and carry forth.
    :return:
    """
    project_root = os.path.dirname(
        os.path.dirname(
            os.path.dirname(
                os.path.abspath(__file__)
            )
        )
    )
    sys.path.append(project_root)
    path_nii = os.path.join(project_root, "BinDependency", "dcm2niix")
    os.environ["PATH"] += os.pathsep + path_nii
    path_dcm = os.path.join(project_root, "BinDependency", "dcmtoolkit")
    os.environ["PATH"] += os.pathsep + path_dcm

