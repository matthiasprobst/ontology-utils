from __future__ import annotations

import re
import warnings
from typing import TYPE_CHECKING, Union, List, Optional, Any
from typing import TypeVar

from pydantic import AnyUrl, FileUrl, HttpUrl
from pydantic.functional_validators import WrapValidator
from rdflib import URIRef, BNode
from typing_extensions import Annotated, TypeAlias

# Only import Thing for static type checkers — avoids runtime circular import
if TYPE_CHECKING:
    from .classes import Thing  # pragma: no cover


def validate_iri_type(value, handler, info):
    def check_item(item):
        if isinstance(item, str) and re.match(r'^https?://', item):
            return str(item)
        if isinstance(item, str) and item.startswith("_:"):
            return str(item)
        if isinstance(item, AnyUrl):
            return str(item)
        if isinstance(item, URIRef):
            return str(item)
        if isinstance(item, BNode):
            return str(item)
        field_name = getattr(info, "field_name", None)
        if field_name is not None:
            msg = f"IriOrType in field '{field_name}' must be a HTTP-URL string or a pydantic AnyUrl object. Got: {type(item)}"
        else:
            msg = "IriOrType must be a HTTP-URL string or a pydantic AnyUrl."
        raise ValueError(msg)

    if isinstance(value, list):
        return [check_item(v) for v in value]
    return check_item(value)


AnyIri = Annotated[
    object,
    WrapValidator(validate_iri_type)
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

IriList: TypeAlias = Union[AnyIri, List[AnyIri]]  # an IRI or a list of IRIs

# High-level aliases (generic where appropriate)
AnyThing: TypeAlias = Union[AnyIri, "Thing"]  # a Thing instance or an IRI
AnyThingOf: TypeAlias = Union[T, AnyThing]  # a Thing instance, an IRI, or the specified type T
AnyThingOrList: TypeAlias = Union[AnyThing, List[AnyThing]]  # a Thing instance, an IRI, or a list of those

AnyIriOf: TypeAlias = Union[T, AnyIri]  # an IRI or the specified type T
# Generic alias: an IRI, a T, or a list containing T or IRIs.
AnyIriOrListOf: TypeAlias = Union[AnyIri, T, List[Union[T, AnyIri]]]

# A runtime factory that helps avoid leaving an unbound TypeVar `T` in runtime
# constructs. Use `make_type_or_list(SomeClass)` to get a typing object that
# accepts SomeClass, IRIs, or lists of those (works well with pydantic.


def _build_union_for_types(types: tuple):
    """Return typing.Union[...] for the supplied types tuple."""
    # Use direct subscription to typing.Union with a tuple of types
    return Union[types]


def make_type_or_list(*types: object):
    """Create a typing object equivalent to:
       Union[<types...>, AnyIri, List[Union[<types...>, AnyIri]]]

    Pass one or more concrete types (classes or typing constructs).
    This returns a runtime typing object (Union[...] / List[...]) which avoids
    leaving an unresolved TypeVar in the annotation when generating schemas or
    serializing values.
    """
    if not types:
        raise ValueError("make_type_or_list requires at least one type")

    # inner union: Union[<types...>, AnyIri]
    inner_union = _build_union_for_types((*types, AnyIri))
    # list of inner union
    list_of_inner = List[inner_union]
    # outer union: Union[<types...>, AnyIri, List[inner_union]]
    return _build_union_for_types((*types, AnyIri, list_of_inner))


def make_optional_type_or_list(*types: object):
    """Create Optional[...] variant of make_type_or_list for the supplied types."""
    return Optional[make_type_or_list(*types)]


class ResourceType:
    """
    Deprecated runtime validator for resources.

    - `ResourceType[...]` (subscript) returns an Annotated validator that accepts
      instances of the allowed type(s) or IRIs (via `validate_iri_type`).
    - Unsubscripted `ResourceType` still provides a pydantic validator for
      compatibility but emits the deprecation warning when validators run.

    Notes:\n    - Prefer using `make_type_or_list(SomeClass)` for runtime-safe annotations
      (these produce concrete Union[...] objects which avoid unresolved
      TypeVars when serializing or building schemas).
    - For static typing you can use `AnyIriOrListOf[SomeType]` or
      `AnyThingOf[SomeType]`.
    """
    _WARN_MSG = "`ResourceType` is deprecated; prefer `make_type_or_list(...)` or `AnyThing`/`AnyThingOf`"

    @classmethod
    def _warn(cls):
        warnings.warn(cls._WARN_MSG, DeprecationWarning, stacklevel=3)

    @classmethod
    def _validate_unsubscripted(cls, value, handler, info=None):
        # Keep compatibility: accept Thing instances and IRIs
        from ontolutils.classes.thing import Thing  # local import to avoid cycles
        cls._warn()
        if isinstance(value, Thing):
            return value
        return validate_iri_type(value, handler, info)

    @classmethod
    def __get_validators__(cls):
        # Called by pydantic when an annotation directly references ResourceType
        yield cls._validate_unsubscripted

    @classmethod
    def __class_getitem__(cls, allowed_type):
        # Called when used as ResourceType[SomeClass] or ResourceType[(A, B)]
        def validate_with_allowed(value, handler, info):
            cls._warn()

            def check_item(item):
                try:
                    is_allowed = isinstance(item, allowed_type)
                except Exception:
                    is_allowed = False
                if is_allowed:
                    return item
                return validate_iri_type(item, handler, info)

            if isinstance(value, list):
                return [check_item(v) for v in value]
            return check_item(value)

        return Annotated[object, WrapValidator(validate_with_allowed)]
