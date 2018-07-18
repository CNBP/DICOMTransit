CNBP_schema = ['CNBPID', 'CNNID', 'CNFUNID', 'PSCID', 'DCCID', 'Timpoint', 'Hash1', 'Hash2', 'Hash3']
CNBP_schema_types = ['TEXT', 'INTEGER', 'INTEGER', 'TEXT', 'INTEGER', 'INTEGER', 'TEXT', 'TEXT', 'TEXT']
CNBP_schema_keyfield = 'MRN'
CNBP_schema_keyfield_type = 'INTEGER'
CNBP_schema_table_name = 'id_table'

def concatenatedSchema():
    CNBP_schema.insert(0, CNBP_schema_keyfield)
    CNBP_schema_types.insert(0, CNBP_schema_keyfield_type)
    return CNBP_schema, CNBP_schema_types

if __name__ == '__main__':
    print(concatenatedSchema())
