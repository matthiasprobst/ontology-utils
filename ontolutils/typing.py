import re

from pydantic import AnyUrl
from pydantic.functional_validators import WrapValidator
from typing_extensions import Annotated
from rdflib import URIRef
from .classes.thingmodel import ThingModel


def validate_resource_type(value, handler, info):
    def check_item(item):
        if isinstance(item, str) and re.match(r'^https?://', item):
            return str(item)
        if isinstance(item, AnyUrl):
            return str(item)
        if isinstance(item, ThingModel):
            return item
        if isinstance(item, URIRef):
            return str(item)
        field_name = getattr(info, "field_name", None)
        if field_name is not None:
            msg = f"ResourceType in field '{field_name}' must be a HTTP-URL string, a pydantic AnyUrl or a Thing object. Got: {type(item)}"
        else:
            msg = "ResourceType must be a HTTP-URL string, a pydantic AnyUrl or a Thing object."
        raise ValueError(msg)

    if isinstance(value, list):
        return [check_item(v) for v in value]
    return check_item(value)


ResourceType = Annotated[
    object,
    WrapValidator(validate_resource_type)
]


def __validate_blank_node(value: str, handler, info):
    if not isinstance(value, str):
        raise ValueError(f"Blank node must be a string, not {type(value)}")
    if value.startswith('_:'):
        return value
    raise ValueError(f"Blank node must start with _: {value}")


BlankNodeType = Annotated[str, WrapValidator(__validate_blank_node)]
