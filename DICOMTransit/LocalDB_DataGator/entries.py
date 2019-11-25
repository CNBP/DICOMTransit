from datagator.model_base import Entry
import json


def get_entries(CNBPID: str):
    """
    Acquire the Entry based on the MRN provided.
    :param MRN:
    :return:
    """
    entries = Entry.query.filter_by(CNBPID=CNBPID).order_by("timestamp").first()
    return entries


def get_fields_dict(entry: Entry):
    """
    Obtain all fields and filter them to include on the relevant fields.
    :param entry:
    :return:
    """

    keys_fields = entry.__dict__.keys()
    list_all_fields = list(keys_fields)
    list_fields = filter(is_native_field, list_all_fields)
    return list_fields


def is_native_field(field: str):
    """
    Check if the field is a native field that does not contain data.
    All native fields starts with "_"
    This is used in a filter function
    :param field:
    :return:
    """
    return field[0] == "_"


def jsonify_entry(entry: Entry):
    list_fields = get_fields_dict(entry)
    Meta: dict = {
        "Instrument": "LocalMRIQuestionnaire",
        "Visit": "V1",
        "Candidate": 362950,
        "DDE": False,
    }
    LocalMRIQuestionnaire: dict = {}
    for field in list_fields:
        LocalMRIQuestionnaire[field] = getattr(entry, field)
    return json.dumps([Meta, LocalMRIQuestionnaire])


if __name__ == "__main__":
    a = get_entries("VXF12345")
