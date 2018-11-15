########################################################################################################################
#
# Canadian Neonatal Brain Platform: 
#	CNN/CNFUN to REDCap Data Update Script
#
# Author:
#	Applied Clinical Research Unit (URCA)
#
# History:
# 	-> Summer 2018 - Initial Creation
# 	-> November 2018 - Code completion and cleanup
#   -> TBD - Final version
#
# Note:
#	Developed for Python 3.6.7
#
########################################################################################################################


#-----------------------------------------------------------------------------------------------------------------------
# General Imports
#-----------------------------------------------------------------------------------------------------------------------

from array import *
from io import StringIO
from json import dumps
from requests import post	# To install this module (Windows Command Prompt): python -m pip install requests
from tkinter import *
from tkinter.messagebox import *

import io
import json
import pycurl # To install this module (Windows Command Prompt): python -m pip install pycurl
import pyodbc # To install this module (Windows Command Prompt): python -m pip install pyodbc
import sqlite3
import sys
import time


#-----------------------------------------------------------------------------------------------------------------------
# Environments
#-----------------------------------------------------------------------------------------------------------------------

import development as environment
#import production as environment

#-----------------------------------------------------------------------------------------------------------------------
# Constants
#-----------------------------------------------------------------------------------------------------------------------

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

redcap_api_url = environment.REDCAP_API_URL

redcap_token_cnn_admission = environment.REDCAP_TOKEN_CNN_ADMISSION
redcap_token_cnn_baby = environment.REDCAP_TOKEN_CNN_BABY
redcap_token_cnn_mother = environment.REDCAP_TOKEN_CNN_MOTHER
redcap_token_cnn_master = environment.REDCAP_TOKEN_CNN_MASTER

redcap_token_cnfun_patient = environment.REDCAP_TOKEN_CNFUN_PATIENT

cnn_connection_string = environment.CNN_CONNECTION_STRING
cnfun_connection_string = environment.CNFUN_CONNECTION_STRING


#-----------------------------------------------------------------------------------------------------------------------
# Functions
#-----------------------------------------------------------------------------------------------------------------------


"""
 Purpose: Display content of SQLite DB
"""
def displaySqliteContent():
    
    db = sqlite3.connect('Local_id_table.sqlite')
    
    cursor = db.cursor()
    cursor.execute('select ID,study_id, MNR,National_id,National_id_temp,Study_name,hashing,CnnPatientUI from Local_id_table')

    all_rows = cursor.fetchall()
    
    cursor.close
    db.close

    for row in all_rows:        
        label = Label(window, text= '{0},{1},{2},{3},{4},{5},{6},{7}'.format(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7]))
        label.config(height=2, width=9000)
        label.pack()

"""
 Purpose:
"""    
def updateRedcapData():

         global admission_group
         # Connect to distant CNN database
         window.config(cursor="wait")
         conn = pyodbc.connect(cnn_connection_string)
         cursor = conn.cursor()


         # Start of code for CNN - Admission
         # Get all information about redcap tables name and variables
         ListeMetaData = RedcaApiProjectMetatdata(redcap_token_cnn_admission,redcap_api_url)
         # Call function to update data
         UpdateDataForSpecificRedcapProject(admission_group,GetListRecords(),ListeMetaData,cursor,redcap_token_cnn_admission,redcap_api_url)
         label = Label(window, text='Admission tables done ..')
         label.pack()
         # End of code for CNN - Admission

       

         window.config(cursor="")          
         label = Label(window, text='Done..')
         label.pack()


         cursor.close()
         conn.close        
         return        

"""
 Purpose:
"""  
def RedcaApiProjectMetatdata(ProjectToken, url):
     ListeFieldMetadata = [[]]
     payload = {'token': ProjectToken, 'format': 'json', 'content': 'metadata'}
     response = post(url, data=payload)
     metadata = response.json()
     i = 0
     for field in metadata:
            ListeFieldMetadata.append([field['field_name'],field['field_type'],field['field_label'],field['form_name']])
     return ListeFieldMetadata

"""
 Purpose: Retrieve list of records from local table-id to be updated
"""  
def GetListRecords():

    liste = []

    db = sqlite3.connect('Local_id_table.sqlite')
    cursor = db.cursor()
    cursor.execute('select study_id, MNR from Local_id_table')
    
    all_rows = cursor.fetchall()
    
    for row in all_rows:
        liste.append(row[1])

    cursor.close
    db.close
    
    return liste

"""
 Purpose:
"""  
def UpdateDataForSpecificRedcapProject(Table_Liste, listeRecords,ListeMetaData,cursor, Project_token, Project_url):
    
     originalIdFieldName = ''
     caseId = ''

     # Create a list of label/field/form
             
     for j in range(len(listeRecords)):  # for each records retrieved from the local id table
      for i in range(len(Table_Liste)):  # for each tables in Access
            
                ListFieldRedcap = [[]]
            
                if Table_Liste[i] == 'admission' :
                   originalIdFieldName = 'HospitalRecordNumber'     
                else :
                   originalIdFieldName = 'CaseId'
 
                for k in range(len(ListeMetaData)) :
                   for m in range(len(ListeMetaData[k])) :
                    
                        if  [ListeMetaData[k][2],ListeMetaData[k][0]] not in ListFieldRedcap and ListeMetaData[k][3].lower() == Table_Liste[i].lower() :
                            ListFieldRedcap.append([ListeMetaData[k][2],ListeMetaData[k][0]])
                                  
                # Create a sql query to extract data from specific table in
                # Table_List

                res = cursor.execute("SELECT * FROM " + Table_Liste[i].lower() + " WHERE 1=0")
                columnList = [tuple[0] for tuple in res.description]
                print(columnList)

                selectStatement = 'SELECT ' 
                for row in columnList :
                   selectStatement = selectStatement + '[' + row + '], '
                selectStatement = selectStatement[:-2]
                selectStatement = selectStatement + ' FROM [' + Table_Liste[i] + '] WHERE [' + originalIdFieldName + ']= ?'
            
                # select data for each record in the list
                if Table_Liste[i].lower() == 'admission' :
                                      print (Table_Liste[i].lower())     
                                      print (selectStatement)
                                      cursor.execute(selectStatement, listeRecords[j])
                                  
                                      num_fields = len(cursor.description)
                                      field_names = [i[0] for i in cursor.description] # all fields in the records retrived from Access
                                  
                                      #index = 1
                                      for row in cursor.fetchall():    
                                             caseId = row[0]
                                             record_text = {}
                                             record_text["caseid"] = str(caseId)
                                         
                                             for l in range(len(ListFieldRedcap)):#  for each fields in the Redcap liste => need to find if this field exist in
                                                                                  #  Access list then we concatenate the json-record content
                                                 once = 0
                                                 for t in range(len(ListFieldRedcap[l])):
                                                   try :
                                                       #order =
                                                       #field_names.index(FieldLabelList[l])
                                                       #if order == index :
                                                       #record_text = record_text +
                                                       #field_names[index]+ ':' +
                                                       #str(row[index])+ ','
                                                       order = field_names.index(ListFieldRedcap[l][0])
                                                       if once == 0 :
                                                         
                                                                 if str(row[order]) == 'False'  :
                                                                     value = '0'
                                                                 elif str(row[order]) == 'True' :
                                                                     value = '1'
                                                                 else:
                                                                     value = str(row[order])
                                                                 
                                                                 #record_text =
                                                                 #record_text +
                                                                 #chr(39)+
                                                                 #ListFieldRedcap[l][1]+
                                                                 #chr(39)+': '
                                                                 #+chr(39)+
                                                                 #str(value)
                                                                 #+chr(39)+ ','
                                                                 if str(value) == "None" : value = ""
                                                                 record_text[ListFieldRedcap[l][1]] = str(value) 
                                                                 once +=1
                                                   except ValueError:
                                                                 pass
                                     
                                             #record_text=record_text[:-1]
                                             print (json.dumps(record_text, ensure_ascii=False))
                                        
                                             payload = {'token': Project_token, 'format': 'json', 'content': 'record','type':'flat'}
                                             to_import_json = dumps([record_text], separators=(',',':'))
                                             payload['data'] = to_import_json
                                             response = post(redcap_api_url, data=payload)
                                             print (response.json())

                else:
                                      print (selectStatement)
                                      cursor.execute(selectStatement, caseId)
                                      print (Table_Liste[i].lower()) 
                                      num_fields = len(cursor.description)
                                      field_names = [i[0] for i in cursor.description] # all fields in the records retrieved from Access
                                  
                                      index = 2
                                      for row in cursor.fetchall():
                                         
                                             if caseId =='' :
                                                 caseId = row[0]
                                             record_text = {}
                                             record_text["caseid"] = str(caseId)
                                             once = 0
                                             if (Table_Liste[i].lower() == 'admissionchart'
                                                or Table_Liste[i].lower() == 'formreviewed'
                                                or Table_Liste[i].lower() == 'otherdiagnosis'
                                                or Table_Liste[i].lower() == 'screenlog'
                                                or Table_Liste[i].lower() == 'epiq'
                                                or Table_Liste[i].lower() == 'antenatalinterventions'
                                                or Table_Liste[i].lower() == 'antenatalintervention'):
                                                                         if once == 0 :
                                                                             record_text["redcap_repeat_instrument"] = str(Table_Liste[i].lower()) 
                                                                             once = 1
                                                                         record_text["redcap_repeat_instance"] = str(index)
                                                                         index = index + 1

                                             for l in range(len(ListFieldRedcap)):#  for each fields in the Redcap liste => need to find if this field exist in
                                                                                  #  Access list then we concatenate the json-record content
                                                 once = 0
                                                 for t in range(len(ListFieldRedcap[l])):
                                                   try :
                                                       #order =
                                                       #field_names.index(FieldLabelList[l])
                                                       #if order == index :
                                                       #record_text = record_text +
                                                       #field_names[index]+ ':' +
                                                       #str(row[index])+ ','
                                                       order = field_names.index(ListFieldRedcap[l][0])
                                                       if once == 0 :
                                                         
                                                                 if str(row[order]) == 'False'  :
                                                                     value = '0'
                                                                 elif str(row[order]) == 'True' :
                                                                     value = '1'
                                                                 else:
                                                                     value = str(row[order])
                                                                 if str(value) == "None" : value = ""
                                                                 record_text[ListFieldRedcap[l][1]] = str(value) 
                                                                 once +=1
                                                   except ValueError:
                                                            
                                                                pass
                                     
                                             #record_text=record_text[:-1]
                                             print (json.dumps(record_text, ensure_ascii=False))
                                             #record ={"caseid": "01100001",
                                             #"redcap_repeat_instance": "2",
                                             #"admcha_item_id": "5",
                                             #"admcha_chart_date": "2010-01-02
                                             #00:00:00"}
                                         
                                             payload = {'token': Project_token, 'format': 'json', 'content': 'record','type':'flat'}
                                             to_import_json = dumps([record_text], separators=(',',':'))
                                             payload['data'] = to_import_json
                                             response = post(redcap_api_url, data=payload)
                                             print (response.json())

                                                  
     return

#-----------------------------------------------------------------------------------------------------------------------
# UI Code
#-----------------------------------------------------------------------------------------------------------------------

# Initialize the tcl/tk interpreter and create the root window.
window = Tk()

# Ajust size of window.
window.geometry("1024x768")

# Add a title label to the root window.
label = Label(window, text="CNN/CNFUN to REDCap - Data Update") 
label.pack()      

# Add all buttons to the root window.
button = Button(window, text="Display SQLite Content", command=displaySqliteContent,height = 1, width = 25) 
button.pack()
button = Button(window, text="Update REDCap Data", command=updateRedcapData,height = 1, width = 25) 
button.pack()

# Set window title.
window.title("CNN/CNFUN to REDCap - Data Update")

# Display window.
window.mainloop()
