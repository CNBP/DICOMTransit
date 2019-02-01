from json import dumps
from operator import itemgetter
from requests import post
from redcap.enums import Project
from redcap.constants import *
from redcap.transaction import RedcapTransaction

import sys
import logging

logging.basicConfig(stream=sys.stdout, level=logging.INFO)

def get_fields(redcap_form_name, transaction: RedcapTransaction):
    """
    Returns a list of fields contained within a specific REDCap form (table)
    :param redcap_form_name: Name of form in REDCap
    :param transaction: the transaction content to be updated.
    :return: A dictionary (key: Name of field in the database, value: Name of field in REDCap)
    """
    redcap_fields = []

    if len(transaction.redcap_metadata) > 0 and not redcap_form_name == '':

        if redcap_form_name.lower() not in transaction.redcap_fields:

            # For each REDCap field
            for i in range(len(transaction.redcap_metadata)):

                # transaction.redcap_metadata[i][0] is field_name
                # transaction.redcap_metadata[i][2] is field_label
                # transaction.redcap_metadata[i][3] is form_name

                if ([transaction.redcap_metadata[i][2], transaction.redcap_metadata[i][0]] not in
                        redcap_fields
                        and transaction.redcap_metadata[i][3].lower() == redcap_form_name.lower()):
                    redcap_fields.append([transaction.redcap_metadata[i][2],
                                          transaction.redcap_metadata[i][0]])

            transaction.redcap_fields[redcap_form_name.lower()] = redcap_fields

        else:

            redcap_fields = transaction.redcap_fields[redcap_form_name.lower()]

    return redcap_fields


def load_metadata(transaction: RedcapTransaction):
    """
    Get all information about REDCap form names and fields.
    :return: None
    """
    transaction.redcap_metadata = []

    # For each REDCap project
    for project in Project:

        # Get all metadata rows.
        payload = {'token': get_project_token(project.name), 'format': 'json', 'content': 'metadata'}
        response = post(redcap_api_url, data=payload)
        metadata = response.json()

        # Add each metadata row to a local list.
        for field in metadata:
            transaction.redcap_metadata.append(
                [field['field_name'], field['field_type'], field['field_label'], field['form_name']])

    return transaction


def send_data(transaction: RedcapTransaction):
    """
    Sends all records in the queue to REDCap.
    :return: successful or not and reason
    """

    # If there is at least one record in the queue waiting to be sent to REDCap
    if not len(transaction.redcap_queue) > 0:
        return False, "RedCap queue is empty."


    # Sort record queue by second column ascending (project).
    transaction.redcap_queue = sorted(transaction.redcap_queue, key=itemgetter(1))

    # For each REDCap project
    for project in Project:

        batch_of_records = []

        # For each record in the global queue
        for index_record in range(len(transaction.redcap_queue)):

            # If the current record belongs to the current project
            if transaction.redcap_queue[index_record][1] == project.value: # todo: verifiy it should be using project.value instead of project.name or the like?

                # We add this record to the batch of records to send.
                batch_of_records.append(transaction.redcap_queue[index_record][0])

                # If the maximum number of records per batch has been reached
            if (len(batch_of_records)) % environment.NUMBER_OF_RECORDS_PER_BATCH == 0:
                # Send the batch of records to REDCap.
                import_records(batch_of_records, get_project_token(project.name))

        # Send the batch of records to REDCap.
        import_records(batch_of_records, get_project_token(project.name))

    return True, "All RedCap project has been sent. "


def import_records(records, project_token):
    """
    Executes a REDCap Import Records API call.
    :param records: Batch of records ready to be sent to REDCap
    :param project_token: Projects Token
    :return: successful or not and reason
    """
    logger = logging.getLogger(__name__)
    # If there is at least one record ready to be sent to REDCap
    if not len(records) > 0:
        return False, "Record is empty"

    # If a token was provided
    if project_token == '' or project_token is None:
        return False, "Project_token %s is invalid!" % project_token

    # Prepare HTTP request.
    payload = {'token': project_token, 'format': 'json', 'content': 'record', 'type': 'flat',
               'overwriteBehavior': 'overwrite'}
    json_string = dumps(records, separators=(',', ':'))
    payload['data'] = json_string

    # Send HTTP request.
    response = post(redcap_api_url, data=payload)

    # If the request was not successful
    if not response.status_code == 200:
        logger.error('There was an error in an API call: ' + response.text)

    # Remove all records from batch.
    records[:] = []

    return True, "Success in sending. "



def get_project_token(project):
    """
    Get Projects Token
    :param project: Projects Configuration Number
    :return: Projects Token
    """
    if project == Project.admission.name:
        return redcap_token_cnn_admission
    elif project == Project.baby.name:
        return redcap_token_cnn_baby
    elif project == Project.mother.name:
        return redcap_token_cnn_mother
    elif project == Project.master.name:
        return redcap_token_cnn_master
    elif project == Project.patient.name:
        return redcap_token_cnfun_patient
    else:
        return ''




