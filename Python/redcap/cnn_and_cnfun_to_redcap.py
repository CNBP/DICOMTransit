########################################################################################################################
#
# Canadian Neonatal Brain Platform:
#   CNN/CNFUN to REDCap Data Update Script
#
# Author:
#   Applied Clinical Research Unit (URCA) - CHU Sainte-Justine Research Center
#
# History:
#   -> Summer 2018 - Initial Creation
#   -> Fall 2018 - Code completion and cleanup
#   -> TBD - Final version
#
# Note:
#   Developed for Python 3.6.7
#
########################################################################################################################


# ----------------------------------------------------------------------------------------------------------------------
#  Imports
# ----------------------------------------------------------------------------------------------------------------------

from enum import Enum
from json import dumps
from operator import itemgetter
from requests import post  # To install this module (Windows Command Prompt): python -m pip install requests
from tkinter import *

import pyodbc  # To install this module (Windows Command Prompt): python -m pip install pyodbc
import sqlite3


# ----------------------------------------------------------------------------------------------------------------------
#  Custom Modules
# ----------------------------------------------------------------------------------------------------------------------

import globalvars

# Note: You may tell the script to use the values of the development or production constants simply by commenting out
#       one of the two lines below.
import development as environment
# import production as environment


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


# ----------------------------------------------------------------------------------------------------------------------
#  Constants
# ----------------------------------------------------------------------------------------------------------------------

redcap_api_url = environment.REDCAP_API_URL

redcap_token_cnn_admission = environment.REDCAP_TOKEN_CNN_ADMISSION
redcap_token_cnn_baby = environment.REDCAP_TOKEN_CNN_BABY
redcap_token_cnn_mother = environment.REDCAP_TOKEN_CNN_MOTHER
redcap_token_cnn_master = environment.REDCAP_TOKEN_CNN_MASTER
redcap_token_cnfun_patient = environment.REDCAP_TOKEN_CNFUN_PATIENT

redcap_repeat_instrument_key_name = "redcap_repeat_instrument"
redcap_repeat_instance_key_name = "redcap_repeat_instance"

cnn_connection_string = environment.CNN_CONNECTION_STRING
cnfun_connection_string = environment.CNFUN_CONNECTION_STRING


# ----------------------------------------------------------------------------------------------------------------------
#  Functions
# ----------------------------------------------------------------------------------------------------------------------


def update_redcap_data():
    """
    This method is the main method of this script. It calls all methods necessary to transfer CNN and CNFUN data
    to REDCap.
    :return: None
    """

    window.config(cursor="wait")

    # Insert blank line.
    label = Label(window, text='')
    label.pack()

    # Initialize the data import configuration matrix.
    label = Label(window, text='Loading Data Import Configuration...')
    label.pack()
    initialize_data_import_configuration_matrix()
    label = Label(window, text='Done.')
    label.pack()

    # Get all information about redcap tables name and variables.
    label = Label(window, text='Loading REDCap Metadata...')
    label.pack()
    load_redcap_metadata()
    label = Label(window, text='Done.')
    label.pack()

    # Get all hospital record numbers.
    label = Label(window, text='Loading Hospital Record Numbers...')
    label.pack()
    load_hospital_record_numbers()
    label = Label(window, text='Done.')
    label.pack()

    # Update Reference Tables.
    label = Label(window, text='Updating Reference Tables...')
    label.pack()
    import_reference_tables()
    label = Label(window, text='Done.')
    label.pack()

    # Update Patient Tables.
    label = Label(window, text='Updating Patient Tables...')
    label.pack()
    import_patient_tables()
    label = Label(window, text='Done.')
    label.pack()

    # Insert blank line.
    label = Label(window, text='')
    label.pack()

    label = Label(window, text='Command completed.')
    label.pack()

    window.config(cursor="")

    return


def load_redcap_metadata():
    """
    Get all information about redcap table names and fields.
    :return: None
    """
    globalvars.redcap_metadata = []

    for i in range(1,len(Project) + 1):
        payload = {'token': get_project_token(i), 'format': 'json', 'content': 'metadata'}
        response = post(redcap_api_url, data=payload)
        metadata = response.json()

        for field in metadata:
            globalvars.redcap_metadata.append(
                [field['field_name'], field['field_type'], field['field_label'], field['form_name']])

    return


def load_hospital_record_numbers():
    """
    Loads a list of all hospital record numbers.
    :return: None
    """
    globalvars.hospital_record_numbers = []

    if environment.USE_LOCAL_HOSPITAL_RECORD_NUMBERS_LIST == 0:
        db = sqlite3.connect('Local_id_table.sqlite')
        cursor = db.cursor()
        cursor.execute('select study_id, MNR from Local_id_table')

        all_rows = cursor.fetchall()

        for row in all_rows:
            globalvars.hospital_record_numbers.append(row[1])

        cursor.close
        db.close
    else:
        globalvars.hospital_record_numbers = [
            3143750,
            3144235,
            3147383,
            3149523,
            3152931,
            3153280,
            3154386,
            3154822,
            3156430,
            3160223,
            3161091,
            3161116,
            3161146,
            3162999,
            3163000,
            3163509,
            3163750,
            3165201,
            3165984,
            3166489,
            3170659,
            3171022,
            3172805,
            3173436,
            3174439,
            3176163,
            3178972,
            3181830,
            3187252,
            3190535,
            3191237,
            3191976,
            3193639,
            3202977
        ]
    return


def initialize_data_import_configuration_matrix():
    """
    Initialize the data import configuration matrix.
    Columns: import_sequence, is_import_enabled, is_reference_table, redcap_project, table_name, database,
             primary_key_name, primary_key_value, authority_on_ids, is_repeatable_instrument
    :return: None
    """
    globalvars.data_import_configuration = [
        [1, 1, 0, 1, 'admission', 1, 1, 1, [2, 3], 0],
        [2, 1, 0, 1, 'admissionChart', 1, 2, 2, None, 1],
        [3, 1, 0, 1, 'admissionstate', 1, 2, 2, None, 1],
        [4, 1, 0, 1, 'Born', 1, 2, 2, None, 1],
        [5, 1, 0, 1, 'Borndiagnosis', 1, 2, 2, None, 1],
        [6, 1, 0, 1, 'Caffeine', 1, 2, 2, None, 1],
        [7, 1, 0, 1, 'Congenitalanomalies', 1, 2, 2, None, 1],
        [8, 1, 0, 1, 'Culturestransfusions', 1, 2, 2, None, 1],
        [9, 1, 0, 1, 'Diagnosisofinfection', 1, 2, 2, None, 1],
        [10, 1, 0, 1, 'Diagnosisprocedures', 1, 2, 2, None, 1],
        [11, 1, 0, 1, 'Discharge', 1, 2, 2, None, 1],
        [12, 1, 0, 1, 'Encephalopathy', 1, 2, 2, None, 1],
        [13, 1, 0, 1, 'Eol', 1, 2, 2, None, 1],
        [14, 1, 0, 1, 'Epiqcentrallines', 1, 2, 2, None, 1],
        [15, 1, 0, 1, 'Formreviewed', 1, 2, 2, None, 1],
        [16, 1, 0, 1, 'Ivh', 1, 2, 2, None, 1],
        [17, 1, 0, 1, 'Nropexams', 1, 2, 2, None, 1],
        [18, 1, 0, 1, 'Nroptreatments', 1, 2, 2, None, 1],
        [19, 1, 0, 1, 'Ntiss1', 1, 2, 2, None, 1],
        [20, 1, 0, 1, 'Ntiss3', 1, 2, 2, None, 1],
        [21, 1, 0, 1, 'Otherdiagnosis', 1, 2, 2, None, 1],
        [22, 1, 0, 1, 'Pdatreatment', 1, 2, 2, None, 1],
        [23, 1, 0, 1, 'Posbloodcsfcultures', 1, 2, 2, None, 1],
        [24, 1, 0, 1, 'Postnatalsteroids', 1, 2, 2, None, 1],
        [25, 1, 0, 1, 'Posttransfer', 1, 2, 2, None, 1],
        [26, 1, 0, 1, 'Rop', 1, 2, 2, None, 1],
        [27, 1, 0, 1, 'Screenlog', 1, 2, 2, None, 1],
        [28, 1, 0, 1, 'Snap', 1, 2, 2, None, 1],
        [29, 1, 0, 1, 'Surfactant', 1, 2, 2, None, 1],
        [30, 1, 0, 1, 'Transport', 1, 2, 2, None, 1],
        [31, 1, 0, 1, 'Trips', 1, 2, 2, None, 1],
        [32, 1, 0, 1, 'Validate', 1, 2, 2, None, 1],
        [33, 1, 0, 2, 'Baby', 1, 3, 3, [4, 5], 0],
        [34, 1, 0, 2, 'Bornbaby', 1, 3, 3, None, 1],
        [35, 1, 0, 2, 'Epiq', 1, 3, 3, None, 1],
        [36, 1, 0, 2, 'Resuscitation', 1, 3, 3, None, 1],
        [37, 1, 0, 2, 'Antenatalinterventions', 1, 3, 3, None, 1],
        [38, 1, 0, 3, 'Mother', 1, 4, 4, None, 0],
        [39, 1, 0, 3, 'Antenatalintervention', 1, 4, 4, None, 1],
        [40, 1, 0, 3, 'Bornmother', 1, 4, 4, None, 1],
        [41, 1, 0, 4, 'Patients', 2, 6, 5, [7], 0],
        [42, 1, 0, 4, '18MonthAssessments', 2, 7, 7, None, 1],
        [43, 1, 0, 4, '36MonthAssessments', 2, 7, 7, None, 1],
        [44, 1, 0, 4, '36MonthStatus', 2, 7, 7, None, 1],
        [45, 1, 0, 4, '3YearAuditoryAssessments', 2, 7, 7, None, 1],
        [46, 1, 0, 4, '3YearFamilyInfo', 2, 7, 7, None, 1],
        [47, 1, 0, 4, '3YearMedicalHistories', 2, 7, 7, None, 1],
        [48, 1, 0, 4, '3YearPrimaryCaregivers', 2, 7, 7, None, 1],
        [49, 1, 0, 4, '3YearVisionAssessments', 2, 7, 7, None, 1],
        [50, 1, 0, 4, 'AuditoryAssessments', 2, 7, 7, None, 1],
        [51, 1, 0, 4, 'FamilyInfo', 2, 7, 7, None, 1],
        [52, 1, 0, 4, 'FollowupReasons', 2, 7, 7, None, 1],
        [53, 1, 0, 4, 'MedicalHistories', 2, 7, 7, None, 1],
        [54, 1, 0, 4, 'PrimaryCaregivers', 2, 7, 7, None, 1],
        [55, 1, 0, 4, 'PsychologicalExaminations', 2, 7, 7, None, 1],
        [56, 1, 0, 4, 'VisionAssessments', 2, 7, 7, None, 1],
        [57, 1, 1, 5, 'mstadmissioncasetype', 1, 8, 8, None, 1],
        [58, 1, 1, 5, 'mstadmissioninfantsex', 1, 8, 8, None, 1],
        [59, 1, 1, 5, 'mstadmissioninternal', 1, 8, 8, None, 1],
        [60, 1, 1, 5, 'mstadmissionpayor', 1, 8, 8, None, 1],
        [61, 1, 1, 5, 'mstadmissionstat', 1, 8, 8, None, 1],
        [62, 1, 1, 5, 'mstborncordbloodteststatus', 1, 8, 8, None, 1],
        [63, 1, 1, 5, 'mstborncountries', 1, 8, 8, None, 1],
        [64, 1, 1, 5, 'mstborndrugscreenresult', 1, 8, 8, None, 1],
        [65, 1, 1, 5, 'mstbornhealthcardtype', 1, 8, 8, None, 1],
        [66, 1, 1, 5, 'mstbornnewbornfeeding', 1, 8, 8, None, 1],
        [67, 1, 1, 5, 'mstbornscreeningoffered', 1, 8, 8, None, 1],
        [68, 1, 1, 5, 'mstbornynu', 1, 8, 8, None, 1],
        [69, 1, 1, 5, 'mstbpdgrade', 1, 8, 8, None, 1],
        [70, 1, 1, 5, 'mstcities', 1, 8, 8, None, 1],
        [71, 1, 1, 5, 'mstcitygroups', 1, 8, 8, None, 1],
        [72, 1, 1, 5, 'mstcnfunhospitallist', 1, 8, 8, None, 1],
        [73, 1, 1, 5, 'mstculturesculture', 1, 8, 8, None, 1],
        [74, 1, 1, 5, 'mstculturesdiagnosis', 1, 8, 8, None, 1],
        [75, 1, 1, 5, 'mstculturesorganism', 1, 8, 8, None, 1],
        [76, 1, 1, 5, 'mstdiagnosiscongenitaltype', 1, 8, 8, None, 1],
        [77, 1, 1, 5, 'mstdiagnosisdiagnosistype', 1, 8, 8, None, 1],
        [78, 1, 1, 5, 'mstdiagnosishie', 1, 8, 8, None, 1],
        [79, 1, 1, 5, 'mstdiagnosisintperforation', 1, 8, 8, None, 1],
        [80, 1, 1, 5, 'mstdiagnosisnecstages', 1, 8, 8, None, 1],
        [81, 1, 1, 5, 'mstdiagnosispdayes', 1, 8, 8, None, 1],
        [82, 1, 1, 5, 'mstdiagnosisrds', 1, 8, 8, None, 1],
        [83, 1, 1, 5, 'mstdiagnosisseizures', 1, 8, 8, None, 1],
        [84, 1, 1, 5, 'mstdiagnosisthrombosislocationarterial', 1, 8, 8, None, 1],
        [85, 1, 1, 5, 'mstdiagnosisthrombosislocationvenous', 1, 8, 8, None, 1],
        [86, 1, 1, 5, 'mstdiagnosisthrombosismethod', 1, 8, 8, None, 1],
        [87, 1, 1, 5, 'mstdiagnosisthrombosistreatment', 1, 8, 8, None, 1],
        [88, 1, 1, 5, 'mstdischargedestination', 1, 8, 8, None, 1],
        [89, 1, 1, 5, 'mstdischargeinpatientarea', 1, 8, 8, None, 1],
        [90, 1, 1, 5, 'mstdischargeresult', 1, 8, 8, None, 1],
        [91, 1, 1, 5, 'mstencephalopathyclinicalstatus', 1, 8, 8, None, 1],
        [92, 1, 1, 5, 'mstencephalopathyclinicalstatusatcompletion', 1, 8, 8, None, 1],
        [93, 1, 1, 5, 'mstencephalopathymethod', 1, 8, 8, None, 1],
        [94, 1, 1, 5, 'mstencephalopathyreasonxprematurediscont', 1, 8, 8, None, 1],
        [95, 1, 1, 5, 'mstencephalopathytargettemp', 1, 8, 8, None, 1],
        [96, 1, 1, 5, 'msteol', 1, 8, 8, None, 1],
        [97, 1, 1, 5, 'mstepiqchecklistused', 1, 8, 8, None, 1],
        [98, 1, 1, 5, 'mstfacilitytype', 1, 8, 8, None, 1],
        [99, 1, 1, 5, 'msthospitals', 1, 8, 8, None, 1],
        [100, 1, 1, 5, 'mstivhresponse', 1, 8, 8, None, 1],
        [101, 1, 1, 5, 'mstivhventricular', 1, 8, 8, None, 1],
        [102, 1, 1, 5, 'mstmotherantecort', 1, 8, 8, None, 1],
        [103, 1, 1, 5, 'mstmotheranteintervention', 1, 8, 8, None, 1],
        [104, 1, 1, 5, 'mstmotherdeliverytype', 1, 8, 8, None, 1],
        [105, 1, 1, 5, 'mstmotherdiabetes', 1, 8, 8, None, 1],
        [106, 1, 1, 5, 'mstmotherethnicity', 1, 8, 8, None, 1],
        [107, 1, 1, 5, 'mstmotherhypertension', 1, 8, 8, None, 1],
        [108, 1, 1, 5, 'mstmotherlabourinit', 1, 8, 8, None, 1],
        [109, 1, 1, 5, 'mstmotherpresentation', 1, 8, 8, None, 1],
        [110, 1, 1, 5, 'mstmotherrom', 1, 8, 8, None, 1],
        [111, 1, 1, 5, 'mstmothertotalacgiven', 1, 8, 8, None, 1],
        [112, 1, 1, 5, 'mstnropcomplications', 1, 8, 8, None, 1],
        [113, 1, 1, 5, 'mstnropdurations', 1, 8, 8, None, 1],
        [114, 1, 1, 5, 'mstnropfollowup', 1, 8, 8, None, 1],
        [115, 1, 1, 5, 'mstnropplus', 1, 8, 8, None, 1],
        [116, 1, 1, 5, 'mstnropstage', 1, 8, 8, None, 1],
        [117, 1, 1, 5, 'mstnroptreatmenteyes', 1, 8, 8, None, 1],
        [118, 1, 1, 5, 'mstnroptreatmentlocations', 1, 8, 8, None, 1],
        [119, 1, 1, 5, 'mstnroptreatmenttypes', 1, 8, 8, None, 1],
        [120, 1, 1, 5, 'mstnropzone', 1, 8, 8, None, 1],
        [121, 1, 1, 5, 'mstntissantibiotics', 1, 8, 8, None, 1],
        [122, 1, 1, 5, 'mstntisschesttube', 1, 8, 8, None, 1],
        [123, 1, 1, 5, 'mstntisspacemaker', 1, 8, 8, None, 1],
        [124, 1, 1, 5, 'mstntisstracheostomy', 1, 8, 8, None, 1],
        [125, 1, 1, 5, 'mstpatientchart', 1, 8, 8, None, 1],
        [126, 1, 1, 5, 'mstpdatreatment', 1, 8, 8, None, 1],
        [127, 1, 1, 5, 'mstpostnatalsteroidsindication', 1, 8, 8, None, 1],
        [128, 1, 1, 5, 'mstpostnatalsteroidsroute', 1, 8, 8, None, 1],
        [129, 1, 1, 5, 'mstpostnatalsteroidstype', 1, 8, 8, None, 1],
        [130, 1, 1, 5, 'mstpostnatalsteroidstypeindication', 1, 8, 8, None, 1],
        [131, 1, 1, 5, 'mstposttransferdest', 1, 8, 8, None, 1],
        [132, 1, 1, 5, 'mstprovinces', 1, 8, 8, None, 1],
        [133, 1, 1, 5, 'mstresponse', 1, 8, 8, None, 1],
        [134, 1, 1, 5, 'mstresponsetostimuli', 1, 8, 8, None, 1],
        [135, 1, 1, 5, 'mstrespstatus', 1, 8, 8, None, 1],
        [136, 1, 1, 5, 'mstresuscitationinitialgas', 1, 8, 8, None, 1],
        [137, 1, 1, 5, 'mstropplus', 1, 8, 8, None, 1],
        [138, 1, 1, 5, 'mstropstage', 1, 8, 8, None, 1],
        [139, 1, 1, 5, 'mstroptreatmenteye', 1, 8, 8, None, 1],
        [140, 1, 1, 5, 'mstroptreatmenttype', 1, 8, 8, None, 1],
        [141, 1, 1, 5, 'mstropzone', 1, 8, 8, None, 1],
        [142, 1, 1, 5, 'mstsearchgridcolumns', 1, 8, 8, None, 1],
        [143, 1, 1, 5, 'mstsnapeffectivefio2', 1, 8, 8, None, 1],
        [144, 1, 1, 5, 'mstsnapfactor', 1, 8, 8, None, 1],
        [145, 1, 1, 5, 'mstsnapseizures', 1, 8, 8, None, 1],
        [146, 1, 1, 5, 'mstsurfactanttype', 1, 8, 8, None, 1],
        [147, 1, 1, 5, 'mstsystolicbp', 1, 8, 8, None, 1],
        [148, 1, 1, 5, 'msttemperature', 1, 8, 8, None, 1],
        [149, 1, 1, 5, 'mstvegfdrugs', 1, 8, 8, None, 1]
    ]

    # Sort data import configuration matrix.
    globalvars.data_import_configuration = sorted(globalvars.data_import_configuration, key=itemgetter(0))

    return


def import_reference_tables():
    """
    Transfers the data of all reference tables to REDCap.
    :return: None
    """
    # For each table in the import configuration matrix
    for i in range(len(globalvars.data_import_configuration)):

        # If the current table is set to be imported
        if globalvars.data_import_configuration[i][1]:

            # If the current table is a reference table
            if globalvars.data_import_configuration[i][2]:

                # Get current table redcap fields.
                current_table_redcap_fields = get_redcap_fields(globalvars.data_import_configuration[i][4])

                # Get database columns list.
                database_column_list = get_database_column_names(globalvars.data_import_configuration[i])

                # Get all the data contained in this table.
                rows = get_data_rows(globalvars.data_import_configuration[i])

                # Clear REDCap Queue.
                clear_redcap_queue()

                # For each row in this table
                for j in range(len(rows)):

                    # Create a blank dictionary.
                    record_text = {}

                    # Add the ID (always 1 for a reference table)
                    record_text[get_primary_key_name(globalvars.data_import_configuration[i][6]).lower()] = str(1)

                    # Set repeatable data (if applicable).
                    if globalvars.data_import_configuration[i][9] == 1:
                        record_text[redcap_repeat_instrument_key_name] = globalvars.data_import_configuration[i][4].lower()
                        record_text[redcap_repeat_instance_key_name] = str(j+1)

                    # For each REDCap field in this table
                    for k in range(len(current_table_redcap_fields)):

                        try:

                            # 0 is for redcap field_label
                            position_in_database_table = \
                                database_column_list.index(current_table_redcap_fields[k][0])

                            if str(rows[j][position_in_database_table]) == 'False':
                                value = '0'
                            elif str(rows[j][position_in_database_table]) == 'True':
                                value = '1'
                            elif str(rows[j][position_in_database_table]) == 'None':
                                value = ''
                            else:
                                value = str(rows[j][position_in_database_table])

                            # 1 is for redcap field_name
                            record_text[current_table_redcap_fields[k][1]] = str(value)

                        except ValueError:

                            pass

                    # Add this item to the REDCap queue.
                    add_record_to_redcap_queue(record_text)

                    if (j + 1) % environment.NUMBER_OF_RECORDS_PER_BATCH == 0:
                        # Send records to REDCap
                        send_data_to_redcap(get_project_token(globalvars.data_import_configuration[i][3]))

                # Send records to REDCap
                send_data_to_redcap(get_project_token(globalvars.data_import_configuration[i][3]))

    return


def import_patient_tables():
    """
    Transfers the data of all patient tables to REDCap (only for each hospital record number loaded).
    :return: None
    """
    # For each hospital record number
    for i in range(len(globalvars.hospital_record_numbers)):

        # Initialize ids.
        initialize_ids(globalvars.hospital_record_numbers[i])

        # For each table in the import configuration matrix
        for j in range(len(globalvars.data_import_configuration)):

            # If the current table is set to be imported
            if globalvars.data_import_configuration[j][1]:

                # If the current table is NOT a reference table
                if not globalvars.data_import_configuration[j][2]:

                    # Get current table redcap fields.
                    current_table_redcap_fields = get_redcap_fields(globalvars.data_import_configuration[j][4])

                    # Get database columns list.
                    database_column_list = get_database_column_names(globalvars.data_import_configuration[j])

                    # Get all data for this patient in this table
                    rows = get_data_rows_for_patient(globalvars.data_import_configuration[j])

                    # If some data was retrieved from the database
                    if rows is not None:

                        # Clear REDCap Queue.
                        clear_redcap_queue()

                        # For each row of data retrieved from the database
                        for k in range(len(rows)):

                            # If this is the first row of data and the current table has authority on any ids
                            if k == 0 and globalvars.data_import_configuration[j][8] is not None:
                                for index in range(len(globalvars.data_import_configuration[j][8])):

                                    pk = globalvars.data_import_configuration[j][8][index]

                                    position = database_column_list.index(get_primary_key_name(pk))

                                    if pk == Field.BabyId.value:
                                        globalvars.BabyId = str(rows[k][position])
                                    elif pk == Field.CaseId.value:
                                        globalvars.CaseId = str(rows[k][position])
                                    elif pk == Field.CNNPatientUI.value:
                                        globalvars.CNNPatientUI = str(rows[k][position])
                                    elif pk == Field.HospitalRecordNumber.value:
                                        globalvars.HospitalRecordNumber = str(rows[k][position])
                                    elif pk == Field.MotherId.value:
                                        globalvars.MotherId = str(rows[k][position])
                                    elif pk == Field.PatientId.value:
                                        globalvars.PatientId = str(rows[k][position])
                                    elif pk == Field.PatientUI.value:
                                        globalvars.PatientUI = str(rows[k][position])
                                    elif pk == Field.MasterId.value:
                                        globalvars.MasterId = str(rows[k][position])

                            # Create a blank dictionary.
                            record_text = {}

                            # Add the ID
                            pk_for_filter = globalvars.data_import_configuration[j][6]
                            pk_for_value = globalvars.data_import_configuration[j][7]

                            if pk_for_value == Field.BabyId.value:
                                record_text[get_primary_key_name(pk_for_filter).lower()] = globalvars.BabyId
                            elif pk_for_value == Field.CaseId.value:
                                record_text[get_primary_key_name(pk_for_filter).lower()] = globalvars.CaseId
                            elif pk_for_value == Field.CNNPatientUI.value:
                                record_text[get_primary_key_name(pk_for_filter).lower()] = globalvars.CNNPatientUI
                            elif pk_for_value == Field.HospitalRecordNumber.value:
                                # Special Case: We do not save the Hospital Record Number in REDCap.
                                # Instead, we save the CaseId.'
                                record_text[Field.CaseId.name.lower()] = globalvars.CaseId
                            elif pk_for_value == Field.MotherId.value:
                                record_text[get_primary_key_name(pk_for_filter).lower()] = globalvars.MotherId
                            elif pk_for_value == Field.PatientId.value:
                                record_text[get_primary_key_name(pk_for_filter).lower()] = globalvars.PatientId
                            elif pk_for_value == Field.PatientUI.value:
                                record_text[get_primary_key_name(pk_for_filter).lower()] = globalvars.PatientUI
                            elif pk_for_value == Field.MasterId.value:
                                record_text[get_primary_key_name(pk_for_filter).lower()] = globalvars.MasterId

                            # Set repeatable data (if applicable).
                            if globalvars.data_import_configuration[j][9] == 1:
                                record_text[redcap_repeat_instrument_key_name] = globalvars.data_import_configuration[j][
                                    4].lower()
                                record_text[redcap_repeat_instance_key_name] = str(k + 1)

                            # For each REDCap field in this table
                            for m in range(len(current_table_redcap_fields)):

                                try:

                                    # 0 is for redcap field_label
                                    position_in_database_table = \
                                        database_column_list.index(current_table_redcap_fields[m][0])

                                    if str(rows[k][position_in_database_table]) == 'False':
                                        value = '0'
                                    elif str(rows[k][position_in_database_table]) == 'True':
                                        value = '1'
                                    elif str(rows[k][position_in_database_table]) == 'None':
                                        value = ''
                                    else:
                                        value = str(rows[k][position_in_database_table])

                                    # 1 is for redcap field_name
                                    record_text[current_table_redcap_fields[m][1]] = str(value)

                                except ValueError:

                                    pass

                            # Add this item to the REDCap queue.
                            add_record_to_redcap_queue(record_text)

                            if (k + 1) % environment.NUMBER_OF_RECORDS_PER_BATCH == 0:
                                # Send records to REDCap
                                send_data_to_redcap(get_project_token(globalvars.data_import_configuration[j][3]))

                        # Send records to REDCap
                        send_data_to_redcap(get_project_token(globalvars.data_import_configuration[j][3]))

    return


def add_record_to_redcap_queue(record_text):
    """
    Adds a record to the list of records to send to REDCap.
    :param record_text: Record data
    :return: None
    """
    globalvars.redcap_queue.append(record_text)

    return


def get_data_rows(table_info):
    """
    Gets all rows of data for a reference table.
    :param table_info: Table Information
    :return: List of all the rows obtained from the query.
    """
    if table_info is not None:
        if table_info[4] != '':

            select_statement = 'SELECT * FROM [' + table_info[4] + ']'

            conn = pyodbc.connect(get_connection_string(table_info[5]))
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


def get_data_rows_for_patient(table_info):
    """
    Gets all rows of data for a patient table.
    :param table_info: Table Information
    :return: List of all the rows obtained from the query.
    """
    if table_info is not None:
        if table_info[4] != '':

            primary_key_filter_name = str(get_primary_key_name(table_info[6]))
            primary_key_filter_value = str(get_primary_key_value(table_info[7]))
            primary_key_data_type = str(get_primary_key_data_type(table_info[7]))

            if primary_key_filter_name != '' and primary_key_filter_value != '' and primary_key_filter_value != 'None':

                if primary_key_data_type == str(DataType.String.value):
                    select_statement = ("SELECT * FROM [" +
                                        table_info[4] +
                                        "] WHERE [" +
                                        primary_key_filter_name +
                                        "] = " +
                                        "'" +
                                        primary_key_filter_value +
                                        "'")
                elif primary_key_data_type == str(DataType.Integer.value):
                    select_statement = ("SELECT * FROM [" +
                                        table_info[4] +
                                        "] WHERE [" +
                                        primary_key_filter_name +
                                        "] = " +
                                        primary_key_filter_value)
                else:
                    select_statement = ''

                try:

                    conn = pyodbc.connect(get_connection_string(table_info[5]))
                    odbc_cursor = conn.cursor()

                    odbc_cursor.execute(select_statement)

                    data = odbc_cursor.fetchall()

                    odbc_cursor.close()
                    conn.close

                except ValueError:

                    raise

                return data

            else:
                return None
        else:
            return None
    else:
        return None


def get_redcap_fields(table_name):
    """
    Returns a list of fields contained within a REDCap questionnaire (table)
    :param table_name: Name of table
    :return: A dictionary (key: Name of field in the database, value: Name of field in REDCap)
    """
    redcap_fields = []

    if len(globalvars.redcap_metadata) > 0 and not table_name == '':

        # For each REDCap field
        for i in range(len(globalvars.redcap_metadata)):

            # globalvars.redcap_metadata[i][0] is field_name
            # globalvars.redcap_metadata[i][2] is field_label
            # globalvars.redcap_metadata[i][3] is form_name

            if ([globalvars.redcap_metadata[i][2], globalvars.redcap_metadata[i][0]] not in
                    redcap_fields
                    and globalvars.redcap_metadata[i][3].lower() == table_name.lower()):

                redcap_fields.append([globalvars.redcap_metadata[i][2],
                                      globalvars.redcap_metadata[i][0]])

    return redcap_fields


def get_database_column_names(table_info):
    """
    Returns a list of fields contained within a database table.
    :param table_info: Table Information
    :return: List of fields
    """
    if table_info is not None:

        database_columns = ((),)

        if table_info[4].lower() not in globalvars.database_column_names:

            conn = pyodbc.connect(get_connection_string(table_info[5]))
            odbc_cursor = conn.cursor()

            result = odbc_cursor.execute('SELECT * FROM [' + table_info[4].lower() + '] WHERE 1=0')
            database_columns = [tuple[0] for tuple in result.description]

            odbc_cursor.close()
            conn.close

            globalvars.database_column_names[table_info[4].lower()] = database_columns

        else:

            database_columns = globalvars.database_column_names[table_info[4].lower()]

        return database_columns

    else:

        return None


def get_project_token(project):
    """
    Get Project Token
    :param project: Project Configuration Number
    :return: Project Token
    """
    if project == Project.admission.value:
        return redcap_token_cnn_admission
    elif project == Project.baby.value:
        return redcap_token_cnn_baby
    elif project == Project.mother.value:
        return redcap_token_cnn_mother
    elif project == Project.master.value:
        return redcap_token_cnn_master
    elif project == Project.patient.value:
        return redcap_token_cnfun_patient
    else:
        return ''


def get_connection_string(database):
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


def get_primary_key_name(primary_key):
    """
    Get Primary Key Name
    :param primary_key: Primary Key Configuration Number
    :return: Primary Key Name
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


def get_primary_key_value(primary_key):
    """
    Get Primary Key Value
    :param primary_key: Primary Key Configuration Number
    :return: Primary Key Value
    """
    if primary_key == Field.BabyId.value:
        return globalvars.BabyId
    elif primary_key == Field.CaseId.value:
        return globalvars.CaseId
    elif primary_key == Field.CNNPatientUI.value:
        return globalvars.CNNPatientUI
    elif primary_key == Field.HospitalRecordNumber.value:
        return globalvars.HospitalRecordNumber
    elif primary_key == Field.MotherId.value:
        return globalvars.MotherId
    elif primary_key == Field.PatientId.value:
        return globalvars.PatientId
    elif primary_key == Field.PatientUI.value:
        return globalvars.PatientUI
    elif primary_key == Field.MasterId.value:
        return globalvars.MasterId
    else:
        return -1


def get_primary_key_data_type(primary_key):
    """
    Get Primary Key Data Type
    :param primary_key: Primary Key Configuration Number
    :return: Data Type Configuration Value
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


def clear_redcap_queue():
    """
    Erase all records in the queue.
    :return: None
    """
    globalvars.redcap_queue = []

    return


def send_data_to_redcap(project_token):
    """
    Sends all records in the queue to REDCap.
    :param project_token: Token of project to update
    :return: None
    """
    # If there is at least one record in the queue waiting to be sent to REDCap
    if len(globalvars.redcap_queue) > 0:
        # If a token was provided
        if not project_token == '':
            # Prepare HTTP request
            payload = {'token': project_token, 'format': 'json', 'content': 'record', 'type': 'flat',
                       'overwriteBehavior': 'overwrite'}
            to_import_json = dumps([globalvars.redcap_queue], separators=(',', ':'))
            if to_import_json.startswith("[["):
                to_import_json = to_import_json[1:]
            if to_import_json.endswith("]]"):
                to_import_json = to_import_json[:-1]
            payload['data'] = to_import_json
            # Send HTTP request
            response = post(redcap_api_url, data=payload)
            # If the request was successful
            if response.status_code == 200:
                # Empty the queue.
                clear_redcap_queue()

    return


def initialize_ids(hospital_record_number):
    """
    Sets the hospital record number and reset all ids related to this hospital record number.
    :param hospital_record_number: Hospital Record Number
    :return: None
    """
    globalvars.HospitalRecordNumber = hospital_record_number
    globalvars.CaseId = -1
    globalvars.BabyId = -1
    globalvars.MotherId = -1
    globalvars.PatientUI = -1
    globalvars.CNNPatientUI = -1
    globalvars.PatientId = -1
    globalvars.MasterId = -1

    return


# ----------------------------------------------------------------------------------------------------------------------
#  UI Code
# ----------------------------------------------------------------------------------------------------------------------

# Initialize the tcl/tk interpreter and create the root window.
window = Tk()

# Adjust size of window.
window.geometry("1024x768")

# Add a title label to the root window.
label = Label(window, text="CNN/CNFUN to REDCap - Data Update")
label.pack()

# Add all buttons to the root window.
button = Button(window, text="Update REDCap Data", command=update_redcap_data, height=1, width=25)
button.pack()

# Set window title.
window.title("CNN/CNFUN to REDCap - Data Update")

# Display window.
window.mainloop()