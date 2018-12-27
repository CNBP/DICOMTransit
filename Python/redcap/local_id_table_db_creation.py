""""
Script used to generated a SAMPLE database.
"""

import sqlite3
import hashlib
import uuid

sqlite_file = 'Local_id_table.sqlite'    # name of the sqlite database file
table_name = 'Local_id_table'  # name of the table to be created

new_field = 'ID' # name of the column
field_type = 'INTEGER'  # column data type

new_field2 = 'study_id' # name of the column
field_type2 = 'TEXT'  # column data type

new_field3 = 'MNR' # name of the column
field_type3 = 'TEXT'  # column data type

new_field4 = 'National_id ' # name of the column
field_type4 = 'TEXT'  # column data type

new_field5 = 'National_id_temp ' # name of the column
field_type5 = 'TEXT'  # column data type

new_field6 = 'Study_name ' # name of the column
field_type6 = 'TEXT'  # column data type

new_field7 = 'hashing' # name of the column
field_type7 = 'TEXT'  # column data type

new_field8 = 'CnnPatientUI' # name of the column
field_type8 = 'TEXT'  # column data type

def hash_NATIONAL_ID(National_id):
    # uuid is used to generate a random number
    salt = uuid.uuid4().hex
    return hashlib.sha256(salt.encode() + National_id.encode()).hexdigest() + ':' + salt

# Connecting to the database file
conn = sqlite3.connect(sqlite_file)
c = conn.cursor()
c.execute('DROP TABLE IF EXISTS {tn}'.format(tn=table_name))
# Creating a second table with 1 column and set it as PRIMARY KEY
# note that PRIMARY KEY column must consist of unique values!
c.execute(' CREATE TABLE  {tn} ({nf} {ft} PRIMARY KEY  ,{nf2} {ft2} NOT NULL  ,{nf3} {ft3} NOT NULL,{nf4} {ft4} ,{nf5} {ft5},{nf6} {ft6} ,{nf7} {ft7} ,{nf8} {ft8} )  '\
        .format(tn=table_name, nf=new_field, ft=field_type,nf2=new_field2, ft2=field_type2,nf3=new_field3, ft3=field_type3,nf4=new_field4, ft4=field_type4,nf5=new_field5, ft5=field_type5,nf6=new_field6, ft6=field_type6,nf7=new_field7, ft7=field_type7,nf8=new_field8, ft8=field_type8 ))
try:
    hashed= hash_NATIONAL_ID('ELTR1524859')
    c.execute("INSERT INTO {tn} ({nf2},{nf3},{nf4},{nf5},{nf6},{nf7},{nf8}) VALUES ('CNBP01001', '2358228','ELTR1524859','','','','')"\
        .format(tn=table_name, nf2=new_field2, nf3=new_field3,nf4=new_field4,nf5=new_field5,nf6=new_field6,nf7=new_field7,nf8=new_field8))
    c.execute("INSERT INTO {tn} ({nf2},{nf3},{nf4},{nf5},{nf6},{nf7},{nf8}) VALUES ('CNBP01001', '2361664','ELTR1524859','','','','')"\
        .format(tn=table_name, nf2=new_field2, nf3=new_field3,nf4=new_field4,nf5=new_field5,nf6=new_field6,nf7=new_field7,nf8=new_field8))
    c.execute("INSERT INTO {tn} ({nf2},{nf3},{nf4},{nf5},{nf6},{nf7},{nf8}) VALUES ('CNBP01001', '2361665','ELTR1524859','','','','')"\
        .format(tn=table_name, nf2=new_field2, nf3=new_field3,nf4=new_field4,nf5=new_field5,nf6=new_field6,nf7=new_field7,nf8=new_field8))
    c.execute("INSERT INTO {tn} ({nf2},{nf3},{nf4},{nf5},{nf6},{nf7},{nf8}) VALUES ('CNBP01001', '2362666','ELTR1524859','','','','')"\
        .format(tn=table_name, nf2=new_field2, nf3=new_field3,nf4=new_field4,nf5=new_field5,nf6=new_field6,nf7=new_field7,nf8=new_field8))
#    c.execute("INSERT INTO {tn} ({nf2},{nf3},{nf4},{nf5},{nf6},{nf7},{nf8}) VALUES (%s, %s, %s,%s, %s, %s, %s))" .format(tn=table_name, nf2=new_field2, nf3=new_field3,nf4=new_field4,nf5=new_field5,nf6=new_field6,nf7=new_field7,nf8=new_field8)),("CNBP01001", "14587584","ELTR1524859","","","","")
        
       
except sqlite3.IntegrityError:
    print('ERROR: ID already exists in PRIMARY KEY column {}'.format(id_column))
    

#    c.execute("INSERT INTO {tn} ({nf2},{nf3},{nf4},{nf5},{nf6},{nf7},{nf8}) VALUES (%s, %s, %s,%s, %s, %s, %s))",("CNBP01001", "14587584","ELTR1524859","","","","")\
#        .format(tn=table_name, nf2=new_field2, nf3=new_field3,nf4=new_field4,nf5=new_field5,nf6=new_field6,nf7=new_field7,nf8=new_field8))
# Committing changes and closing the connection to the database file
conn.commit()
conn.close()
