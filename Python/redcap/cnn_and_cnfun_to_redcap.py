#!/usr/bin/env python

"""
Canadian Neonatal Brain Platform: CNN/CNFUN to REDCap Data Update Script

History:
	-> Summer 2018 - Initial Creation
	-> November 2018 - Code completion and cleanup
  -> TBD - Final version

Note:
	Developed for Python 3.6.7
"""

__author__ = "Martin Lamarche, of Applied Clinical Research Unit (URCA)"
__license__ = "GPL"
__version__ = "0.2"
__maintainer__ = "Martin Lamarche"
__email__ = "martin.lamarche.urca@gmail.com"
__status__ = "Prototype"

# -----------------------------------------------------------------------------------------------------------------------
# General Imports
# -----------------------------------------------------------------------------------------------------------------------

import json
import sqlite3
from json import dumps
from tkinter import *
from LocalDB.API import get_list_MRN
import development as environment
import pyodbc  # To install this module (Windows Command Prompt): python -m pip install pyodbc
from requests import post  # To install this module (Windows Command Prompt): python -m pip install requests
import logging
logging.basicConfig(stream=sys.stdout, level=logging.INFO)
from redcap.query import redcap_query
# -----------------------------------------------------------------------------------------------------------------------
# Environments
# -----------------------------------------------------------------------------------------------------------------------
# import production as environment

# -----------------------------------------------------------------------------------------------------------------------
# Constants
# -----------------------------------------------------------------------------------------------------------------------

admission_group = ['admission',
                   'admissionChart',
                   'admissionstate',
                   'Born',
                   'Borndiagnosis',
                   'Caffeine',
                   'Congenitalanomalies',
                   'Culturestransfusions',
                   'Diagnosisofinfection',
                   'Diagnosisprocedures',
                   'Discharge',
                   'Encephalopathy',
                   'Eol',
                   'Epiqcentrallines',
                   'Formreviewed',
                   'Ivh',
                   'Nropexams',
                   'Nroptreatments',
                   'Ntiss1',
                   'Ntiss3',
                   'Otherdiagnosis',
                   'Pdatreatment',
                   'Posbloodcsfcultures',
                   'Postnatalsteroids',
                   'Posttransfer',
                   'Rop',
                   'Screenlog',
                   'Snap',
                   'Surfactant',
                   'Transport',
                   'Trips',
                   'Validate']

baby_group = ['Baby',
              'Bornbaby',
              'Epiq',
              'Resuscitation',
              'Antenatalinterventions']

mother_group = ['Mother',
                'Antenatalintervention',
                'Bornmother']

master_group = ['mstadmissioncasetype',
                'mstadmissioninfantsex',
                'mstadmissioninternal',
                'mstadmissionpayor',
                'mstadmissionstat',
                'mstborncordbloodteststatus',
                'mstborncountries',
                'mstborndrugscreenresult',
                'mstbornhealthcardtype',
                'mstbornnewbornfeeding',
                'mstbornscreeningoffered',
                'mstbornynu',
                'mstbpdgrade',
                'mstcities',
                'mstcitygroups',
                'mstcnfunhospitallist',
                'mstculturesculture',
                'mstculturesdiagnosis',
                'mstculturesorganism',
                'mstdiagnosiscongenitaltype',
                'mstdiagnosisdiagnosistype',
                'mstdiagnosishie',
                'mstdiagnosisintperforation',
                'mstdiagnosisnecstages',
                'mstdiagnosispdayes',
                'mstdiagnosisrds',
                'mstdiagnosisseizures',
                'mstdiagnosisthrombosislocationarterial',
                'mstdiagnosisthrombosislocationvenous',
                'mstdiagnosisthrombosismethod',
                'mstdiagnosisthrombosistreatment',
                'mstdischargedestination',
                'mstdischargeinpatientarea',
                'mstdischargeresult',
                'mstencephalopathyclinicalstatus',
                'mstencephalopathyclinicalstatusatcompletion',
                'mstencephalopathymethod',
                'mstencephalopathyreasonxprematurediscont',
                'mstencephalopathytargettemp',
                'msteol',
                'mstepiqchecklistused',
                'mstfacilitytype',
                'msthospitals',
                'mstivhresponse',
                'mstivhventricular',
                'mstmotherantecort',
                'mstmotheranteintervention',
                'mstmotherdeliverytype',
                'mstmotherdiabetes',
                'mstmotherethnicity',
                'mstmotherhypertension',
                'mstmotherlabourinit',
                'mstmotherpresentation',
                'mstmotherrom',
                'mstmothertotalacgiven',
                'mstnropcomplications',
                'mstnropdurations',
                'mstnropfollowup',
                'mstnropplus',
                'mstnropstage',
                'mstnroptreatmenteyes',
                'mstnroptreatmentlocations',
                'mstnroptreatmenttypes',
                'mstnropzone',
                'mstntissantibiotics',
                'mstntisschesttube',
                'mstntisspacemaker',
                'mstntisstracheostomy',
                'mstpatientchart',
                'mstpdatreatment',
                'mstpostnatalsteroidsindication',
                'mstpostnatalsteroidsroute',
                'mstpostnatalsteroidstype',
                'mstpostnatalsteroidstypeindication',
                'mstposttransferdest',
                'mstprovinces',
                'mstresponse',
                'mstresponsetostimuli',
                'mstrespstatus',
                'mstresuscitationinitialgas',
                'mstropplus',
                'mstropstage',
                'mstroptreatmenteye',
                'mstroptreatmenttype',
                'mstropzone',
                'mstsearchgridcolumns',
                'mstsnapeffectivefio2',
                'mstsnapfactor',
                'mstsnapseizures',
                'mstsurfactanttype',
                'mstsystolicbp',
                'msttemperature',
                'mstvegfdrugs']

patient_group = ['Patients',
                 'Monthassessments',
                 'MonthStatus',
                 'Yearauditoryassessments',
                 'YearFamilyInfo',
                 'Yearmedicalhistories',
                 'YearPrimaryCaregivers',
                 'Yearvisionassessments',
                 'AuditoryAssessments',
                 'FamilyInfo',
                 'FollowupReasons',
                 'MedicalHistories',
                 'PrimaryCaregivers',
                 'PsychologicalExaminations',
                 'VisionAssessments']



# Environmental Variables:
redcap_api_url = environment.REDCAP_API_URL

redcap_token_cnn_admission = environment.REDCAP_TOKEN_CNN_ADMISSION
redcap_token_cnn_baby = environment.REDCAP_TOKEN_CNN_BABY
redcap_token_cnn_mother = environment.REDCAP_TOKEN_CNN_MOTHER
redcap_token_cnn_master = environment.REDCAP_TOKEN_CNN_MASTER

redcap_token_cnfun_patient = environment.REDCAP_TOKEN_CNFUN_PATIENT

tokens_all = []

cnn_connection_string = environment.CNN_CONNECTION_STRING
cnfun_connection_string = environment.CNFUN_CONNECTION_STRING


# -----------------------------------------------------------------------------------------------------------------------
# Functions
# -----------------------------------------------------------------------------------------------------------------------


def displaySqliteContent():
    """
     Purpose: Display content of SQLite DB
    :return:
    """
    logger = logging.getLogger(__name__)
    db = sqlite3.connect('Local_id_table.sqlite')

    cursor = db.cursor()
    cursor.execute(
        'select ID,study_id, MNR,National_id,National_id_temp,Study_name,hashing,CnnPatientUI from Local_id_table')

    all_rows = cursor.fetchall()

    cursor.close
    db.close

    for row in all_rows:
        label = Label(window,
                      text='{0},{1},{2},{3},{4},{5},{6},{7}'.format(row[0], row[1], row[2], row[3], row[4], row[5],
                                                                    row[6], row[7]))
        label.config(height=2, width=9000)
        label.pack()


def updateRedcapData():
    """

    :return:
    """
    logger = logging.getLogger(__name__)

    global admission_group
    # Connect to distant CNN database
    window.config(cursor="wait")
    conn = pyodbc.connect(cnn_connection_string)
    cursor = conn.cursor()

    # Start of code for CNN - Admission
    # Get all information about redcap tables name and variables
    list_meta = RedcaApiProjectMetatdata(redcap_token_cnn_admission, redcap_api_url)

    list_records = get_list_MRN()

    # Call function to update data
    UpdateDataForSpecificRedcapProject(admission_group, list_records, list_meta, cursor,
                                       redcap_token_cnn_admission)
    label = Label(window, text='Admission tables done ..')
    label.pack()
    # End of code for CNN - Admission

    window.config(cursor="")
    label = Label(window, text='Done..')
    label.pack()

    cursor.close()
    return


def RedcaApiProjectMetatdata(ProjectToken, url):
    """

    :param ProjectToken:
    :param url:
    :return:
    """
    logger = logging.getLogger(__name__)
    list_metafields = [[]]
    payload = {'token': ProjectToken, 'format': 'json', 'content': 'metadata'}
    response = post(url, data=payload)
    metadata = response.json()
    i = 0
    for field in metadata:
        list_metafields.append([field['field_name'], field['field_type'], field['field_label'], field['form_name']])
    return list_metafields


def UpdateDataForSpecificRedcapProject(list_tables, list_records, list_meta, cursor, token_project):
    """
    Update RedCap project for some particular data.
    :param list_tables:
    :param list_records:
    :param list_meta:
    :param cursor:
    :param token_project:
    :return:
    """
    logger = logging.getLogger(__name__)
    originalIdFieldName = ''
    caseId = ''

    # Create a list of label/field/form

    # for each records retrieved from the local id table
    for index_record in range(len(list_records)):

        current_record = list_records[index_record]

        # for each tables in Access
        for index_table in range(len(list_tables)):

            list_redcapfields = [[]]

            current_table = list_tables[index_table].lower()

            # Admission table are indexed using hospital record number.
            if current_table == 'admission':
                originalIdFieldName = 'HospitalRecordNumber'
            # All other tables are using CaseID
            else:
                originalIdFieldName = 'CaseId'

            # ????????
            for index_meta in range(len(list_meta)):
                current_meta = list_meta[index_meta]

                for m in range(len(current_meta)):
                    if [current_meta[2], current_meta[0]] not in list_redcapfields and \
                            current_meta[3].lower() == current_table:
                        list_redcapfields.append([current_meta[2], current_meta[0]])

            # Create a sql query to extract data from specific table in
            # Table_List

            res = cursor.execute("SELECT * FROM " + current_table + " WHERE 1=0")
            list_columns = [tuple[0] for tuple in res.description]
            print(list_columns)

            selectStatement = 'SELECT '
            for row in list_columns:
                selectStatement = selectStatement + '[' + row + '], '
            selectStatement = selectStatement[:-2]
            selectStatement = selectStatement + ' FROM [' + list_tables[index_table] + '] WHERE [' + originalIdFieldName + ']= ?'


            print(current_table)
            print(selectStatement)

            # select data for each record in the list
            if current_table == 'admission':
                cursor.execute(selectStatement, current_record)
                num_fields = len(cursor.description)
                process_admission(cursor, list_redcapfields, token_project)
            else:
                cursor.execute(selectStatement, caseId)
                num_fields = len(cursor.description)
                process_form(caseId, current_table, cursor, list_redcapfields, token_project)

    return


def process_admission(cursor, list_redcapfields, token_project):
    """
    Process admission table.
    :param caseId:
    :param cursor:
    :param list_redcapfields:
    :param token_project:
    :return:
    """

    # all fields in the records retrieved from Access
    field_names = [i[0] for i in cursor.description]

    # index = 1
    for row in cursor.fetchall():
        record_text = process_row_admission(field_names, list_redcapfields, row)
        redcap_query.post(token_project, record_text)


def process_row_admission(field_names, list_redcapfields, row):
    """
    This function is used to process one row within the the admission record?
    :param caseId:
    :param field_names:
    :param list_redcapfields:
    :param row:
    :param token_project:
    :return:
    """
    logger = logging.getLogger(__name__)
    caseId = row[0]
    record_text = {}
    record_text["caseid"] = str(caseId)
    # for each fields in the Redcap liste => need to find if this field exist in
    for index_redcapfield in range(len(list_redcapfields)):
        current_redcapfield = list_redcapfields[index_redcapfield]

        #  Access list then we concatenate the json-record content
        once = 0
        for t in range(len(current_redcapfield)):
            try:
                # order =
                # field_names.index(FieldLabelList[l])
                # if order == index :
                # record_text = record_text +
                # field_names[index]+ ':' +
                # str(row[index])+ ','
                order = field_names.index(current_redcapfield[0])
                if once == 0:

                    if str(row[order]) == 'False':
                        value = '0'
                    elif str(row[order]) == 'True':
                        value = '1'
                    else:
                        value = str(row[order])

                    # record_text =
                    # record_text +
                    # chr(39)+
                    # list_redcapfields[l][1]+
                    # chr(39)+': '
                    # +chr(39)+
                    # str(value)
                    # +chr(39)+ ','
                    if str(value) == "None": value = ""
                    record_text[current_redcapfield[1]] = str(value)
                    once += 1
            except ValueError:
                logger.warning("Value Error Encountered!")
                # todo: add more information here.
                pass

    return record_text


def process_form(caseId, current_table, cursor, list_redcapfields, token_project):
    """
    Process the form.
    :param caseId:
    :param current_table:
    :param cursor:
    :param list_redcapfields:
    :param token_project:
    :return:
    """

    # all fields in the records retrieved from Access
    field_names = [i[0] for i in cursor.description]

    index = 2 #???
    for row in cursor.fetchall():

        record_text = process_row_other_form(caseId, current_table, field_names, index, list_redcapfields, row)
        redcap_query.post(token_project, record_text)


def process_row_other_form(caseId, current_table, field_names, index, list_redcapfields, row):
    """
    Process one row from forms other than admission
    :param caseId:
    :param current_table:
    :param field_names:
    :param index:
    :param list_redcapfields:
    :param row:
    :return:
    """
    logger = logging.getLogger(__name__)
    if caseId == '':
        caseId = row[0]
    record_text = {}
    record_text["caseid"] = str(caseId)
    once = 0
    if (current_table == 'admissionchart'
            or current_table == 'formreviewed'
            or current_table == 'otherdiagnosis'
            or current_table == 'screenlog'
            or current_table == 'epiq'
            or current_table == 'antenatalinterventions'
            or current_table == 'antenatalintervention'):
        if once == 0:
            record_text["redcap_repeat_instrument"] = str(current_table)
            once = 1
        record_text["redcap_repeat_instance"] = str(index)
        index = index + 1

    # for each fields in the Redcap liste => need to find if this field exist in
    for index_redcapfield in range(len(list_redcapfields)):
        current_redcapfield = list_redcapfields[index_redcapfield]
        #  Access list then we concatenate the json-record content
        once = 0

        for t in range(len(current_redcapfield)):
            try:
                # order =
                # field_names.index(FieldLabelList[index_redcapfield])
                # if order == index :
                # record_text = record_text +
                # field_names[index]+ ':' +
                # str(row[index])+ ','
                order = field_names.index(current_redcapfield[0])
                if once == 0:

                    if str(row[order]) == 'False':
                        value = '0'
                    elif str(row[order]) == 'True':
                        value = '1'
                    else:
                        value = str(row[order])
                    if str(value) == "None": value = ""
                    record_text[current_redcapfield[1]] = str(value)
                    once += 1
            except ValueError:

                logger.warning("Value Error Encountered!")
                # todo: add more information here.

                pass
    return record_text

"""

# -----------------------------------------------------------------------------------------------------------------------
# UI Code
# -----------------------------------------------------------------------------------------------------------------------

# Initialize the tcl/tk interpreter and create the root window.
window = Tk()

# Ajust size of window.
window.geometry("1024x768")

# Add a title label to the root window.
label = Label(window, text="CNN/CNFUN to REDCap - Data Update")
label.pack()

# Add all buttons to the root window.
button = Button(window, text="Display SQLite Content", command=displaySqliteContent, height=1, width=25)
button.pack()
button = Button(window, text="Update REDCap Data", command=updateRedcapData, height=1, width=25)
button.pack()

# Set window title.
window.title("CNN/CNFUN to REDCap - Data Update")

# Display window.
window.mainloop()
"""

if __name__ == "__main__":

    global admission_group

    # Connect to distant CNN database
    conn = pyodbc.connect(cnn_connection_string)
    cursor = conn.cursor()

    # Start of code for CNN - Admission
    # Get all information about redcap tables name and variables
    list_meta = RedcaApiProjectMetatdata(redcap_token_cnn_admission, redcap_api_url)

    tokens = [redcap_token_cnn_admission,
              redcap_token_cnn_baby,
              redcap_token_cnn_mother,
              redcap_token_cnn_master,
              redcap_token_cnfun_patient
              ]

    list_records = get_list_MRN()

    for token in tokens:
        # Call function to update data
        UpdateDataForSpecificRedcapProject(admission_group,
                                           list_records,
                                           list_meta,
                                           cursor,
                                           token)
