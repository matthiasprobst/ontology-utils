import re
from typing import TypeVar, Union, List, Optional

from pydantic import AnyUrl, FileUrl, HttpUrl
from pydantic.functional_validators import WrapValidator
from rdflib import URIRef, BNode
from typing_extensions import Annotated, TypeAlias

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
        if isinstance(item, BNode):
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


def validate_id(value, handler, info):
    if isinstance(value, str):
        if value.startswith('_:'):
            return value
        if re.match(r'^https?://', value):
            return str(HttpUrl(value))
        # urn:
        if value.startswith("urn:"):
            return str(value)
        # file:
        if value.startswith("file"):
            return str(FileUrl(value))

    if isinstance(value, BNode):
        return value.n3()
    if isinstance(value, AnyUrl):
        return str(value)
    if isinstance(value, URIRef):
        return str(value)
    if isinstance(value, FileUrl):
        return str(value)
    raise ValueError(f"Id must be a HTTP-URL string or a pydantic AnyUrl or a URIRef, not {type(value)}")


def validate_none_blank_id(value, handler, info):
    if isinstance(value, str):
        if value.startswith('_:'):
            raise ValueError("Blank nodes are not allowed for this IdType")

        if isinstance(value, BNode):
            raise ValueError("Blank nodes are not allowed for this IdType")

    return validate_id(value, handler, info)


IdType = Annotated[
    object,
    WrapValidator(validate_id)
]

# Alias for IdType for better readability when blank nodes are not allowed
NoneBlankNodeType = Annotated[object, WrapValidator(validate_none_blank_id)]


def __validate_blank_node(value: str, handler, info):
    if not isinstance(value, str):
        raise ValueError(f"Blank node must be a string, not {type(value)}")
    if value.startswith('_:'):
        return value
    raise ValueError(f"Blank node must start with _: {value}")


BlankNodeType = Annotated[str, WrapValidator(__validate_blank_node)]

T = TypeVar("T")
TypeOrListOf: TypeAlias = Union[T, ResourceType, List[Union[T, ResourceType]]]
OptionalTypeOrListOf: TypeAlias = Optional[Union[T, ResourceType, List[Union[T, ResourceType]]]]

UnionResourceType: TypeAlias = Union[T, ResourceType]