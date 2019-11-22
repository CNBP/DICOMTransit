# Experimental attempt to replace with Flask-SQLALchemy to access Flask created database
from datagator.model_base import DICOMTransitConfig


def get_setting(setting_name: str):
    """
    Used to access the dtconfigure_old.sqlite database to retrieve the settings necessary for most other operations.
    :param setting_name: assumed the string already exist. Prior method need to check that.
    :return:
    """

    # Make a query to find the latest setting record from the database
    config_latest = DICOMTransitConfig.query.order_by("timestamp").first()
    return getattr(config_latest, setting_name)


if __name__ == "__main__":
    # propose_CNBPID("GregoryLodygensky012 Study")
    get_setting("DevOrthancIP")
