import re
from pydantic.functional_validators import WrapValidator
from typing_extensions import Annotated


def __validate_blank_node(value, handler, info):
    if value.startswith('_:'):
        return value
    raise ValueError(f"Blank node must start with _: {value}")


def __validate_camera_resolution(value: str, handler, info):
    if not isinstance(value, str):
        raise ValueError(f"Invalid data type for resolution. Expecting str but got {type(value)}")
    pattern = re.compile(r'^\d{3,5}x\d{3,5}$')
    if not re.match(pattern, value):
        raise ValueError(f"Invalid pattern. Expecting {pattern}")
    return value


def __validate_fnumber(value: str, handler, info):
    if not isinstance(value, str):
        raise ValueError(f"Invalid data type for resolution. Expecting str but got {type(value)}")
    pattern = re.compile(r'^f\/\d+(\.\d+)?$')
    if not re.match(pattern, value):
        raise ValueError(f"Invalid pattern. Expecting {pattern}")
    return value


BlankNodeType = Annotated[str, WrapValidator(__validate_blank_node)]
ResolutionType = Annotated[str, WrapValidator(__validate_camera_resolution)]
FNumberType = Annotated[str, WrapValidator(__validate_fnumber)]
