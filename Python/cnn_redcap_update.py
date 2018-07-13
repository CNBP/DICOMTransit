from tkinter import *
import sqlite3
import pyodbc
from array import *
import time
import sys

from tkinter.messagebox import *
fenetre = Tk()
liste = []

 # this creates x as a new label to the GUI
label = Label(fenetre, text="CNN/CNFUN to REDCap - Data update")
label.pack()


def printList():
    i=0
    db = sqlite3.connect ('cnbp_mnr.sqlite')
    cursor = db.cursor()
    cursor.execute('select cnbp, mnr from cnbpmnr')

    all_rows = cursor.fetchall()
    for row in all_rows:
    # row[0] returns the first column in the query (name), row[1] returns email column.
        #  print('{0} , {1}'.format(row[0], row[1]))
        label = Label(fenetre, text= '{0} , {1}'.format(row[0], row[1]))
        liste.append(row[1])
        i=i+1
        label.pack()
        cursor.close
        db.close
def updateList():
           label = Label(fenetre, text='Process began ..')
           # this creates x as a new label to the GUI
           label.pack()
           # Connect to the distant cnn database
           conn = pyodbc.connect(r'Driver={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=Q:\CNN\CNN2010_DB\CNNQueryDb.mdb;' r'PWD=sqlcnn;')
           cursor = conn.cursor()
##   trouver le moyen d'executer la macro
           
           # label = Label(fenetre, text= liste[0])
           # label.pack()
           cursor.execute("select DateOfAdmission from Admission where HospitalRecordNumber=?", 2358228 )
           ##Draw a liste of 
           for row in cursor.fetchall():
                    print (row)
                    toolbar_width = 40

# setup toolbar
toolbar_width = 40
sys.stdout.write("[%s]" % (" " * toolbar_width))
sys.stdout.flush()
sys.stdout.write("\b" * (toolbar_width+1)) # return to start of line, after '['

for i in range(toolbar_width):
    time.sleep(0.1) # do real work here
    # update the bar
    sys.stdout.write("-")
    sys.stdout.flush()

sys.stdout.write("\n")


##Buttons
button = Button(fenetre, text="Study participant's list", command=printList,height = 1, width = 25) 
button.pack()
button = Button(fenetre, text="Update REDCap Data", command=updateList,height = 1, width = 25) 
button.pack()
button = Button(fenetre, text="Import participant's list (csv)", command=updateList,height = 1, width = 25) 
button.pack()
button = Button(fenetre, text="Add New participant", command=updateList,height = 1, width = 25) 
button.pack()


# Make window 300x150 and place at position (50,50)
fenetre.geometry("500x400+350+350")
fenetre.title("CNN/CNFUN REDCap Data update")




fenetre.mainloop()
