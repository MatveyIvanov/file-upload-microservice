import random
import string


def random_string(
    length: int = 20,
    allowed_characters: str = string.ascii_uppercase,
) -> str:
    """
    Generate random string

    :param length: length of the string, defaults to 20
    :type length: int, optional
    :param allowed_characters: string containing allowed characters,
        defaults to string.ascii_uppercase
    :type allowed_characters: str, optional
    :return: generated string
    :rtype: str
    """
    return "".join(random.choice(allowed_characters) for _ in range(length))
