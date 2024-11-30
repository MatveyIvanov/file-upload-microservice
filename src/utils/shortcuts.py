from typing import TypeVar

from utils.exceptions import Custom404Exception

T = TypeVar("T")


def get_object_or_404(obj: T | None, *, msg: str | None = None) -> T:
    """
    Similar to Django shortcut.

    If object is None, exception is raised.
    Otherwise object is returned.

    :param obj: object to return
    :type obj: T | None
    :param msg: message for exception, defaults to None
    :type msg: str | None, optional
    :raises Custom404Exception: _description_
    :return: object
    :rtype: T
    """
    msg = msg if msg else "Not found."
    if obj is None:
        raise Custom404Exception(msg)
    return obj
