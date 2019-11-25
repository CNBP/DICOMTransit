from datagator.model_base import Entry


def get_entries(MRN: int):
    """
    Acquire the Entry based on the MRN provided.
    :param MRN:
    :return:
    """
    entries = Entry.query.filter_by("CNBPID").order_by("timestamp").first()
    return entries


if __name__ == "__main__":
    get_entries(8912324)
