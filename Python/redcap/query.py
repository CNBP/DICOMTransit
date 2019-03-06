# ----------------------------------------------------------------------------------------------------------------------
#  Imports
# ----------------------------------------------------------------------------------------------------------------------

from json import dumps
from operator import itemgetter
from requests import post
from redcap.enums import Project
from redcap.constants import *
from redcap.transaction import RedcapTransaction

import sys
import logging


# ----------------------------------------------------------------------------------------------------------------------
#  Query
# ----------------------------------------------------------------------------------------------------------------------

logging.basicConfig(stream=sys.stdout, level=logging.INFO)


def get_fields(redcap_form_name, transaction: RedcapTransaction):
    """
    Returns a list of fields contained within a specific REDCap form (table)
    :param redcap_form_name: Name of form in REDCap
    :param transaction: RedcapTransaction
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
    for p in Project:

        # Get all metadata rows.
        payload = {'token': get_project_token(p.name), 'format': 'json', 'content': 'metadata'}
        response = post(redcap_api_url, data=payload)
        metadata = response.json()

        # Add each metadata row to a local list.
        for field in metadata:
            transaction.redcap_metadata.append(
                [field['field_name'], field['field_type'], field['field_label'], field['form_name']])

    return transaction


def wipe_all_redcap_data():
    """
    Deletes all REDCap records.
    :return: None
    """
    # For each REDCap project
    for p in Project:

        # Delete all records.
        delete_records(get_record_ids(p.name),get_project_token(p.name))


def send_data(transaction: RedcapTransaction):
    """
    Sends all records in the queue to REDCap.
    :return: Successful or not and reason
    """

    # If there is at least one record in the queue waiting to be sent to REDCap
    if not len(transaction.redcap_queue) > 0:
        return False, "REDCap queue is empty."

    # Sort record queue by second column ascending (project).
    transaction.redcap_queue = sorted(transaction.redcap_queue, key=itemgetter(1))

    # For each REDCap project
    for p in Project:

        batch_of_records = []

        # For each record in the global queue
        for index_record in range(len(transaction.redcap_queue)):

            # If the current record belongs to the current project
            if transaction.redcap_queue[index_record][1] == p.value:

                # We add this record to the batch of records to send.
                batch_of_records.append(transaction.redcap_queue[index_record][0])

                # If the maximum number of records per batch has been reached
            if (len(batch_of_records)) % environment.NUMBER_OF_RECORDS_PER_BATCH == 0:
                # Send the batch of records to REDCap.
                import_records(batch_of_records, get_project_token(p.name))

        # Send the batch of records to REDCap.
        import_records(batch_of_records, get_project_token(p.name))

    return True, "All REDCap data in queue has been sent. "


def import_records(records, project_token):
    """
    Executes a REDCap Import Records API call.
    :param records: Batch of records ready to be sent to REDCap
    :param project_token: Project Token
    :return: Successful or not and reason
    """

    logger = logging.getLogger(__name__)

    # If there is not at least one record ready to be sent to REDCap
    if not len(records) > 0:
        return False, "Record queue is empty"

    # If a token was not provided
    if project_token == '' or project_token is None:
        return False, "Project token %s is invalid!" % project_token

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

    return True, "Success in sending."


def get_record_ids(project):
    """
    Executes a REDCap Export Records API call.
    :param project: Project Name
    :return: List of record ids in specified REDCap project
    """

    record_ids = []

    logger = logging.getLogger(__name__)

    # If a project name was not provided
    if project == '' or project is None:
        return False, "Project name %s is invalid!" % project

    # Get project token.
    project_token = get_project_token(project)

    # Get all record ids.
    payload = {'token':project_token, 'format': 'json', 'content': 'record', 'fields': [get_project_record_id_field_name(project)]}
    response = post(redcap_api_url, data=payload)
    metadata = response.json()

    # If the request was not successful
    if not response.status_code == 200:
        logger.error('There was an error in an API call: ' + response.text)
        return False

    # Add each record id to a list.
    for field in metadata:
        record_ids.append(field[get_project_record_id_field_name(project)])

    return record_ids


def delete_records(record_ids, project_token):
    """
    Executes a REDCap Delete Records API call.
    :param record_ids: List of record ids to delete from REDCap
    :param project_token: Project Token
    :return: Successful or not and reason
    """

    logger = logging.getLogger(__name__)

    # If there is not at least one record id ready to be deleted from REDCap
    if not len(record_ids) > 0:
        return False, "Record list is empty"

    # If a token was not provided
    if project_token == '' or project_token is None:
        return False, "Project token %s is invalid!" % project_token

    # Prepare HTTP request.
    payload = {'token': project_token, 'action': 'delete', 'content': 'record'}
    for record_id_index in range(len(record_ids)):
        payload['records[' + str(record_id_index) + ']'] = record_ids[record_id_index]

    # Send HTTP request.
    response = post(redcap_api_url, data=payload)

    # If the request was not successful
    if not response.status_code == 200:
        logger.error('There was an error in an API call: ' + response.text)

    return True, "Success in deleting."


def get_project_token(project):
    """
    Get Project Token
    :param project: Project Name
    :return: Project Token
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


def get_project_record_id_field_name(project):
    """
    Get Project Record Id Field Name
    :param project: Project Name
    :return: Record Id Field Name
    """
    if project == Project.admission.name:
        return redcap_record_id_field_name_cnn_admission
    elif project == Project.baby.name:
        return redcap_record_id_field_name_cnn_baby
    elif project == Project.mother.name:
        return redcap_record_id_field_name_cnn_mother
    elif project == Project.master.name:
        return redcap_record_id_field_name_cnn_master
    elif project == Project.patient.name:
        return redcap_record_id_field_name_cnfun_patient
    else:
        return ''
