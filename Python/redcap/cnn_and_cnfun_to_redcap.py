# ----------------------------------------------------------------------------------------------------------------------
#  Imports
# ----------------------------------------------------------------------------------------------------------------------

from tkinter import *
from LocalDB.API import load_hospital_record_numbers
from redcap.prepare_patient import prepare_patient_tables
from redcap.prepare_reference import prepare_reference_tables
from redcap.initialization import initialize_import_configuration
from redcap.transaction import RedcapTransaction # the class that contain all the configurations and buffer fo the records
from redcap.query import load_metadata, send_data
from redcap.constants import environment
import logging


# ----------------------------------------------------------------------------------------------------------------------
#  CNN and CNFUN to REDCap
# ----------------------------------------------------------------------------------------------------------------------

logging.basicConfig(stream=sys.stdout, level=logging.INFO)

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

    # Initilize the RedcapTransaction class object to be past and returned each step of the way.
    transaction_stage0 = RedcapTransaction()


    # Load data import configuration matrix.
    label = Label(window, text='Loading Data Import Configuration...')
    label.pack()
    transaction_stage1_initialized = initialize_import_configuration(transaction_stage0)
    label = Label(window, text='Done.')
    label.pack()

    # Get all information about REDCap table names and fields.
    label = Label(window, text='Loading REDCap Metadata...')
    label.pack()
    transaction_stage2_meta_added = load_metadata(transaction_stage1_initialized)
    label = Label(window, text='Done.')
    label.pack()

    # Get all hospital record numbers.
    label = Label(window, text='Loading Hospital Record Numbers...')
    label.pack()
    # Change this flag in env or here to force local of DB loading.
    transaction_stage2_meta_added.hospital_record_numbers = load_hospital_record_numbers(environment.USE_LOCAL_HOSPITAL_RECORD_NUMBERS_LIST)
    label = Label(window, text='Done.')
    label.pack()

    # Update Reference Tables.
    label = Label(window, text='Preparing Reference Data Transfer...')
    label.pack()
    transaction_stage3_references_added = prepare_reference_tables(transaction_stage2_meta_added)
    label = Label(window, text='Done.')
    label.pack()

    # Update Patient Tables.
    label = Label(window, text='Preparing Patient Data Transfer...')
    label.pack()
    transaction_stage4_patients_added = prepare_patient_tables(transaction_stage3_references_added)
    label = Label(window, text='Done.')
    label.pack()

    # Send data to REDCap.
    label = Label(window, text='Sending ALL data to REDCap...')
    label.pack()
    send_data(transaction_stage4_patients_added)
    label = Label(window, text='Done.')
    label.pack()

    # Insert blank line.
    label = Label(window, text='')
    label.pack()

    # Indicate that the script is completed.
    label = Label(window, text='Command completed.')
    label.pack()

    window.config(cursor="")

    return


if __name__ == "__main__":


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

    update_redcap_data()