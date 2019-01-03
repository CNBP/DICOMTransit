from json import dumps

from requests import post
import redcap.development as environment
from redcap import globalvars
from redcap.enums import Project
from redcap.constants import redcap_api_url, redcap_token_cnn_admission, redcap_token_cnn_baby, redcap_token_cnn_mother, \
    redcap_token_cnn_master, redcap_token_cnfun_patient

import os
import logging


def get_redcap_fields(redcap_form_name):
    """
    Returns a list of fields contained within a specific REDCap form (table)
    :param redcap_form_name: Name of form in REDCap
    :return: A dictionary (key: Name of field in the database, value: Name of field in REDCap)
    """
    redcap_fields = []

    if len(globalvars.redcap_metadata) > 0 and not redcap_form_name == '':

        if redcap_form_name.lower() not in globalvars.redcap_fields:

            # For each REDCap field
            for i in range(len(globalvars.redcap_metadata)):

                # globalvars.redcap_metadata[i][0] is field_name
                # globalvars.redcap_metadata[i][2] is field_label
                # globalvars.redcap_metadata[i][3] is form_name

                if ([globalvars.redcap_metadata[i][2], globalvars.redcap_metadata[i][0]] not in
                        redcap_fields
                        and globalvars.redcap_metadata[i][3].lower() == redcap_form_name.lower()):
                    redcap_fields.append([globalvars.redcap_metadata[i][2],
                                          globalvars.redcap_metadata[i][0]])

            globalvars.redcap_fields[redcap_form_name.lower()] = redcap_fields

        else:

            redcap_fields = globalvars.redcap_fields[redcap_form_name.lower()]

    return redcap_fields


def load_redcap_metadata():
    """
    Get all information about REDCap form names and fields.
    :return: None
    """
    globalvars.redcap_metadata = []

    # For each REDCap project
    for index_project in range(1,len(Project) + 1):

        # Get all metadata rows.
        payload = {'token': get_project_token(index_project), 'format': 'json', 'content': 'metadata'}
        response = post(redcap_api_url, data=payload)
        metadata = response.json()

        # Add each metadata row to a local list.
        for field in metadata:
            globalvars.redcap_metadata.append(
                [field['field_name'], field['field_type'], field['field_label'], field['form_name']])

    return


def send_data_to_redcap():
    """
    Sends all records in the queue to REDCap.
    :return: None
    """

    # If there is at least one record in the queue waiting to be sent to REDCap
    if len(globalvars.redcap_queue) > 0:

        # Sort record queue by second column ascending (project).
        globalvars.redcap_queue = sorted(globalvars.redcap_queue, key=itemgetter(1))

        # For each REDCap project
        for i in range(1, len(Project) + 1):

            batch_of_records = []

            # For each record in the global queue
            for j in range(0, len(globalvars.redcap_queue)):

                # If the current record belongs to the current project
                if globalvars.redcap_queue[j][1] == i:
                    # We add this record to the batch of records to send.
                    batch_of_records.append(globalvars.redcap_queue[j][0])

                    # If the maximum number of records per batch has been reached
                if (len(batch_of_records)) % environment.NUMBER_OF_RECORDS_PER_BATCH == 0:
                    # Send the batch of records to REDCap.
                    execute_record_import_api_call(batch_of_records, get_project_token(i))

            # Send the batch of records to REDCap.
            execute_record_import_api_call(batch_of_records, get_project_token(i))

    return


def execute_record_import_api_call(records, project_token):
    """
    Executes a REDCap Import Records API call.
    :param records: Batch of records ready to be sent to REDCap
    :param project_token: Project Token
    :return:
    """
    logger = logging.getLogger(__name__)
    # If there is at least one record ready to be sent to REDCap
    if len(records) > 0:

        # If a token was provided
        if not project_token == '':

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

    return



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


def clear_redcap_queue():
    """
    Erase all records in the queue.
    :return: None
    """
    globalvars.redcap_queue = []

    return


def add_record_to_redcap_queue(record_text, project):
    """
    Adds a record to the list of records to send to REDCap.
    :param record_text: Record data
    :param project: Project Configuration Number where this record belongs
    :return: None
    """
    globalvars.redcap_queue.append([record_text, project])

    return