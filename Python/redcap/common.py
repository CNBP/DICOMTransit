# ----------------------------------------------------------------------------------------------------------------------
#  Imports
# ----------------------------------------------------------------------------------------------------------------------

import sys
import logging


# ----------------------------------------------------------------------------------------------------------------------
#  Common Data Preparation Functions
# ----------------------------------------------------------------------------------------------------------------------

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logger = logging.getLogger(__name__)


def process_field(index_field, current_table_redcap_fields, database_column_list, index_row, record_text, rows) -> None:
    """
    Process the field of the row within the table.
    :param index_field: Index of current REDCap field
    :param current_table_redcap_fields: Current table REDCap fields
    :param database_column_list: Database columns list
    :param index_row: Index of current row
    :param record_text: Current record text
    :param rows: All data contained in current table
    :return: None
    """

    try:
        # 0 is for redcap field_label
        position_in_database_table = \
            database_column_list.index(current_table_redcap_fields[index_field][0])

        if str(rows[index_row][position_in_database_table]) == 'False':
            value = '0'
        elif str(rows[index_row][position_in_database_table]) == 'True':
            value = '1'
        elif str(rows[index_row][position_in_database_table]) == 'None':
            value = ''
        else:
            value = str(rows[index_row][position_in_database_table])

        # 1 is for redcap field_name
        record_text[current_table_redcap_fields[index_field][1]] = str(value)

    except ValueError:
        logger.warning('The current REDCap field (' + current_table_redcap_fields[index_field][1] +
                       ') does not exist in the database column list.')
        pass
