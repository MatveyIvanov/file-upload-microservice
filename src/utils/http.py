from slugify import slugify


def safe_filename(filename: str) -> str:
    """
    Construct safe filename for cases like http header

    :param filename: name of the file
    :type filename: str
    :return: safe version of the filename
    :rtype: str
    """
    ext = filename.split(".")[-1]
    return f"{slugify(filename[:-(len(ext) + 1)])}.{ext}"
