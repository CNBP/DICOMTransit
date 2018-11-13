
class CNBP_blueprint:

    table_name = 'id_table'

    keyfield = 'MRN'
    keyfield_type = 'INTEGER'

    fields = ['CNBPID',
              'CNNID',
              'CNFUNID',
              'DCCID',
              'Timepoint',
              'Hash1',
              'Hash2',
              'Hash3']

    fields_types = ['TEXT',
                    'INTEGER',
                    'INTEGER',
                    'INTEGER',
                    'INTEGER',
                    'TEXT',
                    'TEXT',
                    'TEXT']

    dotenv_variables = [
        "LORISurl",
        "LORISusername",
        "LORISpassword",
        "timepoint_prefix",
        "institutionID",
        "projectID_dictionary",
        "LocalDatabase",
        "LocalDatabasePath",
        "OrthancURL",
        "ProxyIP",
        "ProxyUsername",
        "ProxyPassword",
        "LORISHostIP",
        "LORISHostUsername",
        "LORISHostPassword",
        "DeletionScript",
        "zip_storage_location",
    ]

    import copy

    schema = copy.deepcopy(fields)
    schema.insert(0, keyfield)

    schema_types = copy.deepcopy(fields_types)
    schema_types.insert(0, keyfield_type)

    # the regular expressino of each component of the parts that makes up the proper CNBPID in total.
    PSCID_schema_institution = "^[A-z][A-z][A-z]"
    #PSCID_schema_project = "[A-z][A-z][0-9][0-9]"
    PSCID_schema_subject = "[0-9][0-9][0-9][0-9][0-9][0-9][0-9]"

    PSCID_schema = PSCID_schema_institution + PSCID_schema_subject


def concatenatedSchema():
    """
    Schemea does not include keyfield as that is specified during table creation. This provides a way to return the ENTIRE table schema including both.
    :return:
    """
    return CNBP_blueprint.schema, CNBP_blueprint.schema_types


if __name__ == '__main__':
    print(concatenatedSchema())
