from datetime import datetime, timezone
import time


def get_current_date():
    current_utc = datetime.utcnow()
    return current_utc.strftime("%Y-%m-%d")


def get_current_timestamp():
    return int(time.time())


def get_date_from_timestamp(timestamp):
    dt_utc = datetime.utcfromtimestamp(timestamp).replace(tzinfo=timezone.utc)
    return dt_utc.strftime("%Y-%m-%d")


def is_same_day(timestamp):
    date = get_date_from_timestamp(timestamp)
    current_data = get_current_date()
    return date == current_data
