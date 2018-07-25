
CNBP_schema_table_name = 'id_table'

CNBP_schema_keyfield = 'MRN'
CNBP_schema_keyfield_type = 'INTEGER'

CNBP_schema_fields = ['CNBPID', 'CNNID', 'CNFUNID', 'PSCID', 'DCCID', 'Timepoint', 'Hash1', 'Hash2', 'Hash3']
CNBP_schema_fields_types = ['TEXT', 'INTEGER', 'INTEGER', 'TEXT', 'INTEGER', 'INTEGER', 'TEXT', 'TEXT', 'TEXT']

def concatenatedSchema():
    """
    Schemea does not include keyfield as that is specified during table creation. This provides a way to return the ENTIRE table schema including both.
    :return:
    """
    import copy

    CNBP_schema = copy.deepcopy(CNBP_schema_fields)
    CNBP_schema.insert(0, CNBP_schema_keyfield)

    CNBP_schema_types = copy.deepcopy(CNBP_schema_fields_types)
    CNBP_schema_types.insert(0, CNBP_schema_keyfield_type)

    return CNBP_schema, CNBP_schema_types


CNBP_schema, CNBP_schema_types = concatenatedSchema()


if __name__ == '__main__':
    print(concatenatedSchema())

