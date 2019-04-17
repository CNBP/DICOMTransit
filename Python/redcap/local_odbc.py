# ----------------------------------------------------------------------------------------------------------------------
#  Imports
# ----------------------------------------------------------------------------------------------------------------------

import pyodbc
from typing import List
from redcap.constants import *
from redcap.enums import Database, Field, DataType
from redcap.transaction import RedcapTransaction


# ----------------------------------------------------------------------------------------------------------------------
#  Local ODBC
# ----------------------------------------------------------------------------------------------------------------------

def get_database_column_names(table_info, transaction: RedcapTransaction) -> List[Field]:
    """
    Returns a list of fields contained within a database table.
    :param table_info: Table Information
    :param transaction: RedcapTransaction
    :return: List of fields or None if table not found.
    """
    if table_info is None:
        return None

    # If this is the first time the column names are requested for this table
    if table_info[DATABASE_TABLE_NAME].lower() not in transaction.database_column_names:
        # Get column names from database.

        conn = pyodbc.connect(get_connection_string(table_info[DATABASE]))
        odbc_cursor = conn.cursor()

        result = odbc_cursor.execute('SELECT * FROM [' + table_info[DATABASE_TABLE_NAME].lower() + '] WHERE 1=0')
        database_columns = [tuple[0] for tuple in result.description]

        odbc_cursor.close()
        conn.close

        # Store a copy of column names for this table in local memory.
        transaction.database_column_names[table_info[DATABASE_TABLE_NAME].lower()] = database_columns

    else:
        # Get column names from cache.
        database_columns = transaction.database_column_names[table_info[DATABASE_TABLE_NAME].lower()]

    return database_columns


def get_case_ids(transaction: RedcapTransaction) -> List[int]:
    """
    Get Case Ids
    :param transaction: RedcapTransaction
    :return: List of all the case ids related to the current hospital record number or None if table not found.
    """

    case_ids = []

    primary_key_filter_name = Field.HospitalRecordNumber.name
    primary_key_filter_value = str(transaction.get_primary_key_value(Field.HospitalRecordNumber.value))

    if primary_key_filter_name == '' or primary_key_filter_value == '' or primary_key_filter_value == 'None':
        return None

    select_statement = ("SELECT [CaseId] FROM [Admission] WHERE [" +
                        primary_key_filter_name +
                        "] = '" +
                        primary_key_filter_value +
                        "'")

    conn = pyodbc.connect(get_connection_string(1))
    odbc_cursor = conn.cursor()

    odbc_cursor.execute(select_statement)

    data = odbc_cursor.fetchall()

    for index_case_id in range(len(data)):

        # Add Case Id to list of Case Ids.
        case_ids.append(data[index_case_id][0])

    odbc_cursor.close()
    conn.close

    return case_ids


def get_cnfun_patient_id(caseid: int) -> int:
    """
    Get cnfun id using the cnn case id
    :param caseid: int (case id into cnn database)
    :return: int cnfun patient id (Return -1 if no match found)
    """

    # Preparing CNN database - SQL request.
    select_statement = ("SELECT baby.PatientUI FROM Admission admission, Baby baby WHERE admission.CaseId = '" + caseid + "' AND admission.BabyId=baby.BabyId")

    # Connecting to CNN database.
    conn = pyodbc.connect(get_connection_string(1))
    odbc_cursor = conn.cursor()

    # Executing SQL request.
    odbc_cursor.execute(select_statement)
    data = odbc_cursor.fetchone()

    # Closing connection.
    odbc_cursor.close()
    conn.close

    # If not found, we return -1.
    if data == None:
        return -1

    # Preparing CNFUN database - SQL request.
    patientui = data[0]
    select_statement = ("SELECT PatientId FROM Patients WHERE CNNPatientUI = '" + patientui + "'")

    # Connecting to CNFUN database.
    conn = pyodbc.connect(get_connection_string(2))
    odbc_cursor = conn.cursor()

    # Executing SQL request.
    odbc_cursor.execute(select_statement)
    data = odbc_cursor.fetchone()

    # Closing connection.
    odbc_cursor.close()
    conn.close

    # If not found, we return -1.
    if data == None:
        return -1

    # Return CNFUN - patient id.
    patientid = data[0]
    return patientid


def get_data_rows_for_patient_table(table_info, transaction: RedcapTransaction) -> list:
    """
    Gets all rows of data for a specific patient table.
    :param table_info: Table Information
    :param transaction: RedcapTransaction
    :return: List of all the rows obtained from the query or None if table not found.
    """
    if table_info is None:
        return None

    if table_info[DATABASE_TABLE_NAME] == '':
        return None

    primary_key_filter_name = str(get_primary_key_name(table_info[PRIMARY_KEY_NAME]))
    primary_key_filter_value = str(transaction.get_primary_key_value(table_info[PRIMARY_KEY_VALUE]))
    primary_key_data_type = get_primary_key_data_type(table_info[PRIMARY_KEY_VALUE])

    if primary_key_filter_name == '' or primary_key_filter_value == '' or primary_key_filter_value == 'None':
        return None

    if primary_key_data_type == DataType.String.value:
        select_statement = ("SELECT * FROM [" +
                            table_info[DATABASE_TABLE_NAME] +
                            "] WHERE [" +
                            primary_key_filter_name +
                            "] = '" +
                            primary_key_filter_value +
                            "'")
    elif primary_key_data_type == DataType.Integer.value:
        select_statement = ("SELECT * FROM [" +
                            table_info[DATABASE_TABLE_NAME] +
                            "] WHERE [" +
                            primary_key_filter_name +
                            "] = " +
                            primary_key_filter_value)
    else:
        select_statement = ''

    if select_statement != '':

        conn = pyodbc.connect(get_connection_string(table_info[DATABASE]))
        odbc_cursor = conn.cursor()

        odbc_cursor.execute(select_statement)

        data = odbc_cursor.fetchall()

        odbc_cursor.close()
        conn.close

        return data

    else:
        return None


def get_data_rows_for_reference_table(table_info) -> list:
    """
    Gets all rows of data for a specific reference table.
    :param table_info: Table Information
    :return: List of all the rows obtained from the query or None if table not found.
    """
    if table_info is not None:
        if table_info[DATABASE_TABLE_NAME] != '':

            select_statement = 'SELECT * FROM [' + table_info[DATABASE_TABLE_NAME] + ']'

            conn = pyodbc.connect(get_connection_string(table_info[DATABASE]))
            odbc_cursor = conn.cursor()

            odbc_cursor.execute(select_statement)

            data = odbc_cursor.fetchall()

            odbc_cursor.close()
            conn.close

            return data

        else:
            return None
    else:
        return None


def get_connection_string(database) -> str:
    """
    Get Connection String
    :param database: Database Configuration Number
    :return: Connection String
    """
    if database == Database.CNN.value:
        return cnn_connection_string
    elif database == Database.CNFUN.value:
        return cnfun_connection_string
    else:
        return ''


def get_primary_key_name(primary_key) -> str:
    """
    Get Primary Key Name
    :param primary_key: Primary Key Configuration Number
    :return: String - Primary Key Name
    """
    if primary_key == Field.BabyId.value:
        return Field.BabyId.name
    elif primary_key == Field.CaseId.value:
        return Field.CaseId.name
    elif primary_key == Field.CNNPatientUI.value:
        return Field.CNNPatientUI.name
    elif primary_key == Field.HospitalRecordNumber.value:
        return Field.HospitalRecordNumber.name
    elif primary_key == Field.MotherId.value:
        return Field.MotherId.name
    elif primary_key == Field.PatientId.value:
        return Field.PatientId.name
    elif primary_key == Field.PatientUI.value:
        return Field.PatientUI.name
    elif primary_key == Field.MasterId.value:
        return Field.MasterId.name
    else:
        return Field.Unknown.name


def get_primary_key_data_type(primary_key) -> str:
    """
    Get Primary Key Data Type
    :param primary_key: Primary Key Configuration Number
    :return: String - Data Type Configuration Value
    """
    if primary_key == Field.BabyId.value:
        return DataType.Integer.value
    elif primary_key == Field.CaseId.value:
        return DataType.String.value
    elif primary_key == Field.CNNPatientUI.value:
        return DataType.String.value
    elif primary_key == Field.HospitalRecordNumber.value:
        return DataType.String.value
    elif primary_key == Field.MotherId.value:
        return DataType.Integer.value
    elif primary_key == Field.PatientId.value:
        return DataType.Integer.value
    elif primary_key == Field.PatientUI.value:
        return DataType.String.value
    elif primary_key == Field.MasterId.value:
        return DataType.Integer.value
    else:
        return DataType.Unknown.value
