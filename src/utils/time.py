from datetime import datetime, timedelta

import pytz

from config import settings


def get_current_time() -> datetime:
    """
    Get current time in server's timezone

    :return: datetime object
    :rtype: datetime
    """
    return datetime.now(tz=pytz.timezone(settings.TIMEZONE))


def timestamp_to_datetime(timestamp: float) -> datetime:
    """
    Convert timestamp to datetime in server's timezone

    :param timestamp: timestamp number
    :type timestamp: float
    :return: datetime object
    :rtype: datetime
    """
    return datetime.fromtimestamp(timestamp, tz=pytz.timezone(settings.TIMEZONE))


def get_current_time_with_delta(**delta_kwargs) -> datetime:
    """
    Get current time with timedelta. Kwargs must match timedelta API

    :return: datetime object
    :rtype: datetime
    """
    return get_current_time() + timedelta(**delta_kwargs)
