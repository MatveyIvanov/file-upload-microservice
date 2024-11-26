import random
import string


def random_string(length: int = 20, allowed_characters: str = string.ascii_uppercase):
    return "".join(random.choice(allowed_characters) for _ in range(length))
