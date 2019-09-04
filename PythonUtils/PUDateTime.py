from datetime import datetime, timedelta, time as timeobject


def sleep_until(destination_time: timeobject):
    """
    Sleep until particular time of the date.
    :param destination_time:
    :return:
    """
    sleep_duration = calculate_countdown(
        datetime.now(), destination_time
    ).total_seconds()
    import time

    time.sleep(sleep_duration)


def calculate_countdown(
    source_datetime: datetime, destination_time: timeobject
) -> timedelta:
    """
    Compute the time delta between the current time and to the same destination/hour/time of today.
    Used primarily in scheduled function to compute time delta until next run.
    :param source_datetime:
    :param destination_time:
    :return:
    """
    # Get the date from the source datetime
    destination_date: datetime.date = source_datetime.date()

    # Compute the destination date time by cominging the destination DATE (e.g. today) with the desired destination time.
    destination_datetime: datetime = datetime.combine(
        destination_date, destination_time
    )

    # Add one day if the current destination date time is in the past: used to prevent NEGATIVE countdowns.
    if destination_datetime < source_datetime:
        destination_datetime = datetime.combine(
            destination_date + timedelta(days=1), destination_time
        )

    # Compute the delta.
    remaining_time: timedelta = destination_datetime - source_datetime

    return remaining_time


def datetime_increment(
    datetime_input: datetime, number_of_unit_hours_increment: int, unit_hours: int = 1
):
    """
    Dedicated function to compute the time offset.
    :param current_date:
    :param format:
    :return:
    """
    datetime_offsetted = datetime_input + number_of_unit_hours_increment * timedelta(
        hours=unit_hours
    )

    return datetime_offsetted


def iso2str(input_datetime: datetime) -> str:
    """
    Convert Iso Datetime to ISO string that are compliant with file pathing requirement across OS.
    :return:
    """
    iso_datetime_string = input_datetime.isoformat()
    iso_datetime_string_cleaned = iso_datetime_string.replace(":", "")
    return iso_datetime_string_cleaned


def str2iso(input_string: str) -> datetime:
    """
    Convert a specific type of ISO string that are compliant with file pathing requirement to ISO datetime.
    :return:
    """
    iso_datetime = datetime.strptime(input_string, "%Y-%m-%d %H:%M:%S")
    return iso_datetime


def tstr2iso(input_string: str) -> datetime:
    """
    Convert a specific type of ISO string that are compliant with file pathing requirement to ISO datetime.
    :return:
    """
    no_colon_input_string = input_string.replace(":", "")
    iso_datetime = tstr2iso_nocolon(no_colon_input_string)
    return iso_datetime


def tstr2iso_nocolon(input_string: str) -> datetime:
    """
    Convert a specific type of ISO string that are compliant with file pathing requirement to ISO datetime.
    :return:
    """
    iso_datetime = datetime.strptime(input_string, "%Y-%m-%dT%H%M%S")
    return iso_datetime


def iso2tstr(input_datetime: datetime) -> str:
    """
    Convert ISO string that are compliant with file pathing requirement to ISO datetime with T.
    :return:
    """
    iso_datetime_string_cleaned = iso2str(input_datetime)
    iso_datetime_string_t_replaced = iso_datetime_string_cleaned.replace("T", " ")
    return iso_datetime_string_t_replaced


if __name__ == "__main__":
    from datetime import time as timeobject

    sleep_duration = calculate_countdown(
        datetime.now(), timeobject(hour=19)
    ).total_seconds()
    print(f"{sleep_duration} seconds until waking up.")
