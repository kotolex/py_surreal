import json
from typing import Optional, Dict


def combine(result: Optional[str], kwargs: Dict) -> str:
    """
    Combine optional raw string representation with optional keyword-arguments. Used in relate/create/update statements
    for set methods

    :param result: raw string representation for query
    :param kwargs: optional parameters
    :return: string combined
    """
    first = result if result else ''
    second = ", ".join(f"{k} = {json.dumps(v)}" for k, v in kwargs.items()) if kwargs else ''
    args = ', '.join(element for element in (first, second) if element)
    return args
