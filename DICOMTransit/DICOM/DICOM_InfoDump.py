import csv
from PythonUtils.PUFolder import recursive_list
from DICOMTransit.DICOM.validate import DICOM_validate
from DICOMTransit.DICOM.elements import DICOM_elements

output = []

"""
A batch script to download study date and patient birth date information into files. 
"""


def BatchDateCalculation(path):
    file_list = recursive_list(path)
    for file in file_list:

        if DICOM_validate.file(file):

            # Try to extract these information from the files.
            success1, StudyDate = DICOM_elements.retrieve(file, "StudyDate")
            success2, PatientBirthDate = DICOM_elements.retrieve(
                file, "PatientBirthDate"
            )
            success3, age = DICOM_elements.compute_age(file)

            # Skip this file if it is not successful.
            if not success1 or not success2 or not success3:
                continue

            # Print, store and append the information acquired.
            A = [file, StudyDate, PatientBirthDate, str(age)]
            print(A)
            output.append(A)

    with open("output.csv", "w") as resultFile:
        wr = csv.writer(resultFile, dialect="excel")
        wr.writerow(output)


if __name__ == "__main__":
    BatchDateCalculation(r"C:\FullyAnonymizedSubjects\BDP Subjects\BDP_TSE_T2")
