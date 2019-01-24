
class CNBP_blueprint:

    """
    this blueprint represent the underlying field of the main database.
    NOTE that EACH MRN must be unique. There will NOT be more than one MRN. We update the information to keep the latest subjects seen.
    """

    table_name = 'id_table'

    keyfield = 'MRN'
    keyfield_type = 'INTEGER'

    fields = ['CNBPID',
              'CNNID',
              'CNFUNID',
              'DCCID',
              'Timepoint',
              'Date',
              'Completed',
              'Hash1',
              'Hash2',
              'Hash3',
              'SeriesUID']

    fields_types = ['TEXT',
                    'INTEGER',
                    'INTEGER',
                    'INTEGER',
                    'INTEGER',
                    'TEXT',
                    'INTEGER',
                    'TEXT',
                    'TEXT',
                    'TEXT',
                    'TEXT']

    # this must pass at ALL TIME
    assert(len(fields)==len(fields_types))

    # todo: cross checek these with schema.sql from dtconfigurator as well as .env
    dotenv_variables = [
        "created",
        "LORISurl",
        "LORISusername",
        "LORISpassword",
        "timepoint_prefix",
        "institutionID",
        "projectID_dictionary",
        "LocalDatabasePath",
        "LogPath",
        "ZipPath",
        "DevOrthancIP",
        "DevOrthancUser",
        "DevOrthancPassword",
        "ProdOrthancIP",
        "ProdOrthancUser",
        "ProdOrthancPassword",
    ]

    import copy

    schema = copy.deepcopy(fields)
    schema.insert(0, keyfield)

    schema_types = copy.deepcopy(fields_types)
    schema_types.insert(0, keyfield_type)

    # the regular expressino of each component of the parts that makes up the proper CNBPID in total.
    #PSCID_schema_institution = "^[A-z][A-z][A-z]"

    # Must beginning with a number.
    PSCID_schema_institution = "^[0-9]"

    #PSCID_schema_project = "[A-z][A-z][0-9][0-9]"

    # Must end with 7 numbers.
    PSCID_schema_subject = "[0-9][0-9][0-9][0-9][0-9][0-9][0-9]$"

    PSCID_schema = PSCID_schema_institution + PSCID_schema_subject



def concatenatedSchema():
    """
    Schemea does not include keyfield as that is specified during table creation. This provides a way to return the ENTIRE table schema including both.
    :return:
    """
    return CNBP_blueprint.schema, CNBP_blueprint.schema_types


if __name__ == '__main__':
    print(concatenatedSchema())
