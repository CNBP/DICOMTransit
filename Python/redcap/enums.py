# ----------------------------------------------------------------------------------------------------------------------
#  Imports
# ----------------------------------------------------------------------------------------------------------------------

from enum import Enum


# ----------------------------------------------------------------------------------------------------------------------
#  Enums
# ----------------------------------------------------------------------------------------------------------------------

class Project(Enum):
    admission = 1
    baby = 2
    mother = 3
    patient = 4
    master = 5


class Database(Enum):
    CNN = 1
    CNFUN = 2


class Field(Enum):
    Unknown = -1
    HospitalRecordNumber = 1
    CaseId = 2
    BabyId = 3
    MotherId = 4
    PatientUI = 5
    CNNPatientUI = 6
    PatientId = 7
    MasterId = 8


class DataType(Enum):
    Unknown = -1
    Integer = 1
    String = 2


class MySQLType(Enum):
    unknown = "unknown"
    yesno = "tinyint(1)"
    text = "text"
    textprimary = "text PRIMARY KEY"
