from utils.exceptions import Custom404Exception


def get_object_or_404(obj: object | None, *, msg: str | None = None):
    msg = msg if msg else "Not found."
    if obj is None:
        raise Custom404Exception(msg)
    return obj
