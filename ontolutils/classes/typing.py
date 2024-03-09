from pydantic.functional_validators import WrapValidator
from typing_extensions import Annotated


def __validate_blank_node(value, handler, info):
    if value.startswith('_:'):
        return value
    raise ValueError(f"Blank node must start with _: {value}")


BlankNodeType = Annotated[str, WrapValidator(__validate_blank_node)]
