import json
import logging
import pathlib
import warnings
from dataclasses import dataclass
from datetime import datetime
from functools import lru_cache
from typing import Dict, Union, Optional, Any, List, Type
from urllib.parse import urlparse

import numpy as np
import rdflib
import yaml
from pydantic import AnyUrl, HttpUrl, BaseModel, Field, model_validator, ValidationError
from pydantic import field_serializer
from pydantic_core import Url
from rdflib import XSD
from rdflib.plugins.shared.jsonld.context import Context
from rdflib.query import Result

from .decorator import urirefs, namespaces, URIRefManager, NamespaceManager, _is_http_url
from .thingmodel import ThingModel
from .utils import split_uri
from .. import get_config
from ..typing import IdType, AnyThingOrList

logger = logging.getLogger('ontolutils')
URL_SCHEMES = {"http", "https", "urn", "doi"}


@lru_cache(maxsize=1)
def _get_pyshacl():
    try:
        import pyshacl as sh
        return sh
    except ImportError as e:
        raise ImportError(
            "pyshacl is required but not installed"
        ) from e


@dataclass
class ValidationResult:
    conforms: bool
    results_graph: rdflib.Graph
    results_text: str

    def __bool__(self):
        return self.conforms


@dataclass
class Property:
    name: str
    property_type: Any
    default: Optional[Any] = None
    namespace: Optional[Union[HttpUrl, str]] = None
    namespace_prefix: Optional[str] = None

    def __post_init__(self):
        if self.namespace is None and self.namespace_prefix is not None:
            raise ValueError("If namespace_prefix is given, then namespace must be given as well.")
        if self.namespace_prefix is None and self.namespace is not None:
            raise ValueError("If namespace is given, then namespace_prefix must be given as well.")
        if self.namespace:
            self.namespace = str(HttpUrl(self.namespace))


def resolve_iri(key_or_iri: str, context: Context) -> Optional[str]:
    """Resolve a key or IRI to a full IRI using the context."""
    if key_or_iri.startswith('http'):
        return str(key_or_iri)
    if ':' in key_or_iri:
        iri = context.resolve(key_or_iri)
        if iri.startswith('http'):
            return iri
    try:
        return context.terms.get(key_or_iri).id
    except AttributeError:
        if key_or_iri == 'label':
            return 'http://www.w3.org/2000/01/rdf-schema#label'
    return


def _get_n3():
    return rdflib.BNode().n3()


def build_blank_n3() -> str:
    return rdflib.BNode().n3()


def build_blank_id() -> str:
    id_generator = get_config("blank_id_generator")
    if id_generator is None:
        id_generator = _get_n3

    _blank_node = id_generator()
    return _blank_node


def is_url(iri: str) -> bool:
    try:
        s = str(iri)
        scheme = urlparse(s).scheme.lower()
        if scheme in URL_SCHEMES:
            try:
                AnyUrl(iri)
                return True
            except Exception:
                return False
        return False
    except Exception:
        return False


# class LangString(BaseModel):
#     value: Union[str, int, float]
#     lang: Optional[str] = None
#     datatype: Optional[Union[HttpUrl, str]] = None
#
#     # Validate the datatype itself
#     @field_validator('datatype', mode='before')
#     @classmethod
#     def validate_datatype(cls, datatype):
#         if datatype is None:
#             return datatype
#         # accept either HttpUrl objects or strings that parse as HttpUrl
#         if not is_url(datatype):
#             raise ValueError(f"The datatype must be a valid IRI but got {datatype}.")
#         return datatype
#
#     # Enforce: lang XOR datatype (not both set)
#     @model_validator(mode='after')
#     def check_lang_xor_datatype(self):
#         if self.lang and self.datatype:
#             raise ValueError("A LangString cannot have both a datatype and a language.")
#         return self
#
#     def __str__(self) -> str:
#         return str(self.value)

# A light, permissive BCP-47-ish check: en | en-US | zh-Hant | de-CH-1996, etc.
def _looks_like_lang(tag: str) -> bool:
    import re
    return bool(re.fullmatch(r"[A-Za-z]{1,8}(?:-[A-Za-z0-9]{1,8})*", tag))


def _split_value_lang(s: str) -> tuple[str, Optional[str]]:
    """
    Split 'value@lang' only if the suffix looks like a language tag and there is no trailing space.
    Otherwise, return (s, None).
    """
    if "@" not in s:
        return s, None
    # Take the last '@' so values with earlier '@' (e.g., emails) aren't split incorrectly
    head, tail = s.rsplit("@", 1)
    if not head:  # avoid '@en' case
        return s, None
    if " " in tail:  # lang tags shouldn't contain spaces
        return s, None
    if _looks_like_lang(tail):
        return head, tail
    return s, None


class LangString(BaseModel):
    """Language-String"""
    value: str
    lang: Optional[str] = None

    # Accept str, dict, rdflib.Literal, or LangString
    @model_validator(mode="before")
    @classmethod
    def coerce_input(cls, v: Any):

        if isinstance(v, cls):
            return v

        if isinstance(v, rdflib.Literal):
            return {"value": str(v), "lang": v.language}

        if isinstance(v, dict):
            return v

        if isinstance(v, str):
            value, lang = _split_value_lang(v)
            return {"value": value, "lang": lang}

        if isinstance(v, list):
            return [cls.model_validate(_v) for _v in v]

        return v

    def __hash__(self):
        return hash((self.value, self.lang))

    def __str__(self, show_lang: bool = None):
        if show_lang is None:
            show_lang = get_config("show_lang_in_str")
        if self.lang and show_lang:
            return f"{self.value}@{self.lang}"
        return f"{self.value}" if self.lang else str(self.value)

    def to_dict(self):
        return {"value": self.value, "lang": self.lang}

    @field_serializer("value", "lang")
    def _identity(self, v):
        return v

    def __eq__(self, other):
        """Equality comparison with another LangString or a plain string.

        Examples of equality:
        >>> LangString(value="Hello", lang="en") == LangString(value="Hello", lang="en")
        True
        >>> LangString(value="Hello", lang="en") == "Hello@en"
        True
        >>> LangString(value="Hello", lang="en") == "Hello"
        True
        >>> LangString(value="Hello") == "Hello"
        True
        >>> LangString(value="Hello") == LangString(value="Hello")
        True
        >>> LangString(value="Hello", lang="en") == "Hello@fr"
        False
        """
        if isinstance(other, LangString):
            return self.value == other.value and self.lang == other.lang
        if isinstance(other, str):
            return str(self) == other or self.value == other
        raise TypeError(f"Cannot compare LangString with {type(other)}")

    def startswith(self, *args, **kwargs) -> bool:
        return self.value.startswith(*args, **kwargs)

    def endswith(self, *args, **kwargs) -> bool:
        return self.value.endswith(*args, **kwargs)

    def __len__(self):
        return len(self.value)

    def __getitem__(self, item):
        return self.value.__getitem__(item)

    def split(self, *args, **kwargs):
        return self.value.split(*args, **kwargs)

    def strip(self, *args, **kwargs):
        return self.value.strip(*args, **kwargs)


def langstring_representer(dumper, data):
    return dumper.represent_scalar('tag:yaml.org,2002:str', str(data))


yaml.add_representer(LangString, langstring_representer)


def serialize_lang_str_field(lang_str: LangString):
    if lang_str.lang is None:
        return lang_str.value
    result = {"@value": lang_str.value, "@language": lang_str.lang}
    return result


def datetime_to_literal(dt: datetime):
    """Turn a datetime into a literal."""
    return {
        "@value": dt.isoformat(),
        "@type": str(XSD.dateTime if dt.hour or dt.minute or dt.second else XSD.date)
    }


def _parse_string_value(value, ctx):
    if is_url(value):
        return {"@id": str(value)}
    elif ":" in value:
        _ns, _value = value.split(":", 1)
        if _ns in ctx:
            return {"@id": f"{ctx[_ns]}{_value}"}
    return value


@namespaces(owl='http://www.w3.org/2002/07/owl#',
            rdfs='http://www.w3.org/2000/01/rdf-schema#',
            dcterms='http://purl.org/dc/terms/',
            schema='https://schema.org/',
            skos='http://www.w3.org/2004/02/skos/core#',
            )
@urirefs(Thing='owl:Thing',
         label='rdfs:label',
         altLabel='skos:altLabel',
         description='dcterms:description',
         broader='skos:broader',
         about='schema:about',
         comment='rdfs:comment',
         isDefinedBy='rdfs:isDefinedBy',
         relation='dcterms:relation',
         closeMatch='skos:closeMatch',
         exactMatch='skos:exactMatch')
class Thing(ThingModel):
    """Most basic concept class owl:Thing (see also https://www.w3.org/TR/owl-guide/)

    This class is basis to model other concepts.

    Example for `prov:Person`:

    >>> @namespaces(prov='https://www.w3.org/ns/prov#',
    >>>             foaf='http://xmlns.com/foaf/0.1/')
    >>> @urirefs(Person='prov:Person', first_name='foaf:firstName')
    >>> class Person(Thing):
    >>>     first_name: str = None
    >>>     last_name: str = None

    >>> p = Person(first_name='John', last_name='Doe', age=30)
    >>> # Note, that age is not defined in the class! This is allowed, but may not be
    >>> # serialized into an IRI although the ontology defines it

    >>> print(p.model_dump_jsonld())
    >>> {
    >>>     "@context": {
    >>>         "prov": "https://www.w3.org/ns/prov#",
    >>>         "foaf": "http://xmlns.com/foaf/0.1/",
    >>>         "first_name": "foaf:firstName"
    >>>     },
    >>>     "@id": "N23036f1a4eb149edb7db41b2f5f4268c",
    >>>     "@type": "prov:Person",
    >>>     "foaf:firstName": "John",
    >>>     "last_name": "Doe",
    >>>     "age": "30"  # Age appears as a field without context!
    >>> }

    Note, that values are validated, as `Thing` is a subclass of `pydantic.BaseModel`:

    >>> Person(first_name=1)

    Will lead to a validation error:

    >>> # Traceback (most recent call last):
    >>> # ...
    >>> # pydantic_core._pydantic_core.ValidationError: 1 validation error for Person
    >>> # first_name
    >>> #   Input should be a valid string [type=string_type, input_value=1, input_type=int]
    >>> #     For further information visit https://errors.pydantic.dev/2.4/v/string_type

    """
    id: Optional[IdType] = Field(default_factory=build_blank_id)  # @id
    label: Optional[Union[LangString, List[LangString]]] = Field(default=None)  # rdfs:label
    altLabel: Optional[Union[LangString, List[LangString]]] = Field(default=None, alias="alt_label")  # skos:altLabel
    broader: Optional[AnyThingOrList] = Field(default=None)  # skos:broader
    comment: Optional[Union[LangString, List[LangString]]] = None  # rdfs:comment
    about: Optional[AnyThingOrList] = Field(default=None)  # schema:about
    relation: Optional[AnyThingOrList] = Field(default=None)
    closeMatch: Optional[AnyThingOrList] = Field(default=None, alias='close_match')
    exactMatch: Optional[AnyThingOrList] = Field(default=None, alias='exact_match')
    description: Optional[Union[LangString, List[LangString]]] = None  # dcterms:description
    isDefinedBy: Optional[AnyThingOrList] = Field(default=None, alias="is_defined_by")  # rdfs:isDefinedBy

    # class Config:
    #     arbitrary_types_allowed = True

    @property
    def namespace(self) -> str:
        compact_uri = self.urirefs[self.__class__.__name__]
        prefix, name = compact_uri.split(':')
        return self.namespaces[prefix]

    @property
    def uri(self) -> str:
        compact_uri = self.urirefs[self.__class__.__name__]
        prefix, name = compact_uri.split(':')
        namespace = self.namespaces[prefix]
        return f"{namespace}{name}"

    def map(self, other: Type[ThingModel]) -> ThingModel:
        """Return the class as another class. This is useful to convert a ThingModel
        to another ThingModel class."""
        if not issubclass(other, ThingModel):
            raise TypeError(f"Cannot convert {self.__class__} to {other}. "
                            f"{other} must be a subclass of ThingModel.")
        combined_urirefs = {**self.urirefs, **URIRefManager[other]}
        combined_urirefs.pop(self.__class__.__name__)
        URIRefManager.data[other] = combined_urirefs

        combined_namespaces = {**self.namespaces, **NamespaceManager[other]}
        NamespaceManager.data[other] = combined_namespaces
        return other(**self.model_dump(exclude_none=True))

    @classmethod
    def build(cls, namespace: HttpUrl,
              namespace_prefix: str,
              class_name: str,
              properties: List[Union[Property, Dict]]) -> type:
        """Build a Thing object"""
        return build(
            namespace,
            namespace_prefix,
            class_name,
            properties,
            cls
        )

    # @classmethod
    # def __getattr__(self, item):
    #     urirefs =
    def __lt__(self, other: ThingModel) -> bool:
        """Less than comparison. Useful to sort Thing objects.
        Comparison can only be done with other Thing objects and if an ID is given.
        If one of the objects has no ID, then False is returned."""
        if not isinstance(other, ThingModel):
            raise TypeError(f"Cannot compare {self.__class__} with {type(other)}")
        if self.id is None or other.id is None:
            return False
        return self.id <= other.id

    def get_jsonld_dict(self,
                        base_uri: Optional[Union[str, AnyUrl]] = None,
                        context: Optional[Union[Dict, str]] = None,
                        exclude_none: bool = True,
                        resolve_keys: bool = False,
                        ) -> Dict:
        """Return the JSON-LD dictionary of the object. This will include the context
        and the fields of the object.

        Parameters
        ----------
        context: Optional[Union[Dict, str]]
            The context to use for the JSON-LD serialization. If a string is given, it will
            be interpreted as an import statement and will be added to the context.
        exclude_none: bool=True
            Exclude fields with None values
        resolve_keys: bool=False
            If True, then attributes of a Thing class will be resolved to the full IRI and
            explained in the context.
        base_uri: Optional[Union[str, AnyUrl]]=None
            The base URI to use for blank nodes (only used if no ID is set).
            This is useful, because blank nodes are not globally unique and
            can lead to problems when merging data from different sources.

            Example:

                In the following example, first_name refers to foaf:firstName:

                >>> @namespaces(foaf='http://xmlns.com/foaf/0.1/')
                >>> @urirefs(Person='foaf:Person', first_name='foaf:firstName')
                >>> class Person(Thing):
                >>>     first_name: str = None

                >>> p = Person(first_name='John')
                >>> p.model_dump_jsonld(resolve_keys=True)

                This will result "first_name": "foaf:firstName" showing up in the context:

                >>> {
                >>>     "@context": {
                >>>         "foaf": "http://xmlns.com/foaf/0.1/",
                >>>         "first_name": "foaf:firstName"
                >>>     },
                >>>     "@type": "foaf:Person",
                >>>     "foaf:firstName": "John"
                >>> }

                While resolve_keys=False will result in:

                >>> {
                >>>     "@context": {
                >>>         "foaf": "http://xmlns.com/foaf/0.1/"
                >>>     },
                >>>     "@type": "foaf:Person",
                >>>     "foaf:firstName": "John"
                >>> }


        Returns
        -------
        Dict
            The JSON-LD dictionary
        """
        from .urivalue import URIValue
        logger.debug('Initializing RDF graph to dump the Thing to JSON-LD')

        # lets auto-generate the context
        at_context: Dict = NamespaceManager.get(self.__class__, {}).copy()

        if context is None:
            context = {}

        if not isinstance(context, dict):
            raise TypeError(f"Context must be a dict, not {type(context)}")

        at_context.update(**context)

        # ctx = Context(source={**at_context, **URIRefManager.get(self.__class__)})

        logger.debug(f'The context is "{at_context}".')

        def _serialize_fields(
                obj: Union[ThingModel, int, str, float, bool, datetime],
                _exclude_none: bool
        ) -> Union[Dict, int, str, float, bool]:
            """Serializes the fields of a Thing object into a json-ld
            dictionary (without context!). Note, that IDs can automatically be
            generated (with a local prefix)

            Parameter
            ---------
            obj: Union[ThingModel, int, str, float, bool, datetime]
                The object to serialize (a subclass of ThingModel). All other types will
                be returned as is. One exception is datetime, which will be serialized
                to an ISO string.
            _exclude_none: bool=True
                If True, fields with None values will be excluded from the
                serialization

            Returns
            -------
            Union[Dict, int, str, float, bool]
                The serialized fields or the object as is
            """

            obj_ctx = Context(source={**context,
                                      **NamespaceManager.get(obj.__class__, {}),
                                      **URIRefManager.get(obj.__class__, {})})

            if isinstance(obj, str) and _is_http_url(obj):
                return {"@id": str(obj)}
            if isinstance(obj, str):
                return _parse_string_value(obj, at_context)
            if isinstance(obj, Url):
                return {"@id": str(obj)}
            if isinstance(obj, list):
                return [_serialize_fields(o, _exclude_none) for o in obj]
            if isinstance(obj, (int, float, bool)):
                return obj
            if isinstance(obj, LangString):
                return serialize_lang_str_field(obj)
            if isinstance(obj, datetime):
                return datetime_to_literal(obj)

            uri_ref_manager = URIRefManager.get(obj.__class__, None)
            at_context.update(NamespaceManager.get(obj.__class__, {}))

            if isinstance(obj, ThingModel):
                if obj.model_extra:
                    for extra in obj.model_extra.values():
                        if isinstance(extra, URIValue):
                            at_context[extra.prefix] = extra.namespace

            if uri_ref_manager is None:
                return str(obj)

            try:
                serialized_fields = {}
                if isinstance(obj, ThingModel):
                    if obj.model_extra:
                        for extra_field_name, extra_field_value in obj.model_extra.items():
                            if isinstance(extra_field_value, URIValue):
                                serialized_fields[extra_field_name] = f"{extra_field_value.prefix}:{extra_field_name}"
                for k in obj.model_dump(exclude_none=_exclude_none):
                    value = getattr(obj, k)
                    if isinstance(value, np.ndarray):
                        value = value.tolist()
                    if isinstance(value, str):
                        value = _replace_context_url_with_prefix(value, at_context)
                    if value is not None and k not in ('id', '@id'):
                        iri = uri_ref_manager.get(k, k)
                        if _is_http_url(iri):
                            serialized_fields[iri] = value
                        if resolve_keys:
                            serialized_fields[iri] = value
                        else:
                            term = obj_ctx.find_term(obj_ctx.expand(iri))
                            if term:
                                if obj_ctx.shrink_iri(term.id).split(':')[1] != k:
                                    at_context[k] = term.id
                                    serialized_fields[k] = value
                                else:
                                    serialized_fields[iri] = value
            except AttributeError as e:
                raise AttributeError(f"Could not serialize {obj} ({obj.__class__}). Orig. err: {e}") from e

            # datetime
            for k, v in serialized_fields.copy().items():
                _field = serialized_fields.pop(k)
                key = k
                if isinstance(v, Thing):
                    serialized_fields[key] = _serialize_fields(v, _exclude_none=_exclude_none)
                elif isinstance(v, list):
                    serialized_fields[key] = [
                        _serialize_fields(i, _exclude_none=_exclude_none) for i in v]
                elif isinstance(v, (int, float)):
                    serialized_fields[key] = v
                elif isinstance(v, LangString):
                    serialized_fields[key] = serialize_lang_str_field(v)
                elif _is_http_url(v):
                    serialized_fields[key] = {"@id": str(v)}
                elif isinstance(v, URIValue):
                    serialized_fields[f"{v.prefix}:{key}"] = v.value
                elif isinstance(v, datetime):
                    serialized_fields[key] = datetime_to_literal(v)
                elif isinstance(v, str):
                    serialized_fields[key] = _parse_string_value(v, at_context)
                else:
                    serialized_fields[key] = _serialize_fields(v, _exclude_none=_exclude_none)

            _type = URIRefManager[obj.__class__].get(obj.__class__.__name__, obj.__class__.__name__)

            out = {"@type": _type, **serialized_fields}
            # if no ID is given, generate a local one:
            if obj.id is not None:
                out["@id"] = _replace_context_url_with_prefix(_parse_blank_node(obj.id, base_uri), context)
            else:
                out["@id"] = _replace_context_url_with_prefix(_parse_blank_node(rdflib.BNode().n3(), base_uri), context)
            return out

        serialization = _serialize_fields(self, _exclude_none=exclude_none)

        jsonld = {
            "@context": at_context,
            **serialization
        }

        properties = self.__class__.model_json_schema().get("properties", {})
        if not properties:
            properties = self.__class__.model_json_schema().get("items", {}).get(self.__class__.__name__, {}).get(
                "properties", {})

        for field_name, field_value in properties.items():
            _use_as_id = field_value.get("use_as_id", None)
            if _use_as_id is not None:
                warnings.warn("The use_as_id field is deprecated. Use the @id field instead.", DeprecationWarning)
                _id = getattr(self, field_name)
                if _id is not None:
                    if str(_id).startswith(("_:", "http")):
                        jsonld["@id"] = getattr(self, field_name)
                    else:
                        raise ValueError(f'The ID must be a valid IRI or blank node but got "{_id}".')
        return jsonld

    def serialize(self,
                  format: str,
                  context: Optional[Dict] = None,
                  exclude_none: bool = True,
                  resolve_keys: bool = True,
                  base_uri: Optional[Union[str, AnyUrl]] = None,
                  **kwargs) -> str:
        """
        Serialize the object to a given format. This method calls rdflib.Graph().parse(),
        so the available formats are the same as for the rdflib library:
            ``"xml"``, ``"n3"``,
           ``"turtle"``, ``"nt"``, ``"pretty-xml"``, ``"trix"``, ``"trig"``,
           ``"nquads"``, ``"json-ld"`` and ``"hext"`` are built in.
        The kwargs are passed to rdflib.Graph().parse()
        """

        jsonld_dict = self.get_jsonld_dict(
            context=context,
            exclude_none=exclude_none,
            resolve_keys=resolve_keys,
            base_uri=base_uri
        )
        jsonld_str = json.dumps(jsonld_dict)

        logger.debug(f'Parsing the following jsonld dict to the RDF graph: {jsonld_str}')
        g = rdflib.Graph()

        if context:
            for k, v in context.items():
                g.bind(k, rdflib.Namespace(v))

        g.parse(data=jsonld_str, format='json-ld')

        _context = jsonld_dict.get('@context', {})
        if context:
            _context.update(context)

        return g.serialize(format=format,
                           context=_context,
                           **kwargs)

    def model_dump_jsonld(
            self,
            context: Optional[Dict] = None,
            exclude_none: bool = True,
            rdflib_serialize: bool = False,
            resolve_keys: bool = True,
            base_uri: Optional[Union[str, AnyUrl]] = None,
            indent: int = 4) -> str:
        """Similar to model_dump_json() but will return a JSON string with
        context resulting in a JSON-LD serialization. Using `rdflib_serialize=True`
        will use the rdflib to serialize. This will make the output a bit cleaner
        but is not needed in most cases and just takes a bit more time (and requires
        an internet connection.

        Note, that if `rdflib_serialize=True`, then a blank node will be generated if no ID is set.

        Parameters
        ----------
        context: Optional[Union[Dict, str]]
            The context to use for the JSON-LD serialization. If a string is given, it will
            be interpreted as an import statement and will be added to the context.
        exclude_none: bool=True
            Exclude fields with None values
        rdflib_serialize: bool=False
            If True, the output will be serialized using rdflib. This results in a cleaner
            output but is not needed in most cases and just takes a bit more time (and requires
            an internet connection). Will also generate a blank node if no ID is set.
        resolve_keys: bool=False
            If True, then attributes of a Thing class will be resolved to the full IRI and
            explained in the context.
        indent: int=4
            The indent of the JSON-LD string
        base_uri: Optional[HttpUrl]=None
            The base URI to use for blank nodes (only used if no ID is set).
            This is useful, because blank nodes are not globally unique and
            can lead to problems when merging data from different sources.

            .. seealso:: `Thing.get_jsonld_dict`

        Returns
        -------
        str
            The JSON-LD string
        """
        jsonld_dict = self.get_jsonld_dict(
            context=context,
            exclude_none=exclude_none,
            resolve_keys=resolve_keys,
            base_uri=base_uri
        )
        jsonld_str = json.dumps(jsonld_dict, indent=4)
        if not rdflib_serialize:
            return jsonld_str

        logger.debug(f'Parsing the following jsonld dict to the RDF graph: {jsonld_str}')
        g = rdflib.Graph()
        g.parse(data=jsonld_str, format='json-ld')

        _context = jsonld_dict.get('@context', {})
        if context:
            _context.update(context)

        return g.serialize(format='json-ld',
                           context=_context,
                           indent=indent)

    def model_dump_ttl(self,
                       context: Optional[Dict] = None,
                       exclude_none: bool = True,
                       resolve_keys: bool = True,
                       base_uri: Optional[Union[str, AnyUrl]] = None
                       ):
        """Dump the model as a Turtle string."""
        return self.serialize(
            format="turtle",
            context=context,
            exclude_none=exclude_none,
            resolve_keys=resolve_keys,
            base_uri=base_uri
        )

    def __repr__(self, limit: Optional[int] = None):
        _fields = {k: getattr(self, k) for k in self.__class__.model_fields.keys() if getattr(self, k) is not None}
        if self.model_extra:
            repr_extra = ", ".join([f"{k}={v}" for k, v in {**_fields, **self.model_extra}.items()])
        else:
            repr_extra = ", ".join([f"{k}={v}" for k, v in {**_fields}.items()])
        if limit is None or len(repr_extra) < limit:
            return f"{self.__class__.__name__}({repr_extra})"
        return f"{self.__class__.__name__}({repr_extra[0:limit]}...)"

    def __str__(self, limit: Optional[int] = None):
        return self.__repr__(limit=limit)

    def _repr_html_(self) -> str:
        """Returns the HTML representation of the class"""
        # _fields = {k: getattr(self, k) for k in self.model_fields if getattr(self, k) is not None}
        # repr_fields = ", ".join([f"{k}={v}" for k, v in _fields.items()])
        return self.__repr__()

    @classmethod
    def from_file(cls,
                  source: Optional[Union[str, pathlib.Path]] = None,
                  format: Optional[str] = None,
                  limit: Optional[int] = None,
                  context: Optional[Dict] = None
                  ):
        """Initialize the class from a file"""
        from . import query
        return query(cls, source=source, limit=limit, format=format, context=context)

    @classmethod
    def from_ttl(cls,
                 source: Optional[Union[str, pathlib.Path]] = None,
                 data: Optional[Union[str, Dict]] = None,
                 limit: Optional[int] = None,
                 context: Optional[Dict] = None
                 ):
        """Initialize the class from a Turtle source"""
        g = rdflib.Graph().parse(source=source, data=data)
        jld = g.serialize(format='json-ld')
        return cls.from_jsonld(data=jld, limit=limit, context=context)

    @classmethod
    def from_jsonld(cls,
                    source: Optional[Union[str, pathlib.Path]] = None,
                    data: Optional[Union[str, Dict]] = None,
                    limit: Optional[int] = None,
                    context: Optional[Dict] = None):
        """Initialize the class from a JSON-LD source

        Note the inconsistency in the schema.org protocol. Codemeta for instance uses http whereas
        https is the current standard. This repo only works with https. If you have a http schema,
        this method will replace http with https.

        Parameters
        ----------
        source: Optional[Union[str, pathlib.Path]]=None
            The source of the JSON-LD data (filename). Must be given if data is None.
        data: Optional[Union[str, Dict]]=None
            The JSON-LD data as a str or dictionary. Must be given if source is None.
        limit: Optional[int]=None
            The limit of the number of objects to return. If None, all objects will be returned.
            If limit is 1, then the first object will be returned, else a list of objects.
        context: Optional[Dict]=None
            The context to use for the JSON-LD serialization. If a string is given, it will
            be interpreted as an import statement and will be added to the context.

        """
        from . import query
        if data is not None:
            if isinstance(data, dict):
                data = json.dumps(data)
            if 'http://schema.org/' in data:
                warnings.warn('Replacing http with https in the JSON-LD data. '
                              'This is a workaround for the schema.org inconsistency.',
                              UserWarning)
                data = data.replace('http://schema.org/', 'https://schema.org/')
        return query(cls, source=source, data=data, format="json-ld", limit=limit, context=context)

    @classmethod
    def iri(cls, key: str = None, compact: bool = False):
        """Return the IRI of the class or the key

        Parameter
        ---------
        key: str
            The key (field) of the class
        compact: bool
            If True, returns the short form of the IRI, e.g. 'owl:Thing'
            If False, returns the full IRI, e.g. 'http://www.w3.org/2002/07/owl#Thing'

        Returns
        -------
        str
            The IRI of the class or the key, e.g. 'http://www.w3.org/2002/07/owl#Thing' or
            'owl:Thing' if compact is True
        """
        if key is None:
            iri_short = URIRefManager[cls][cls.__name__]
        else:
            iri_short = URIRefManager[cls][key]
        if compact:
            return iri_short
        ns, key = split_uri(iri_short)
        if ns.endswith(":"):
            ns = ns[:-1]
        ns_iri = NamespaceManager[cls].get(ns, None)
        return f'{ns_iri}{key}'

    @property
    def namespaces(self) -> Dict:
        """Return the namespaces of the class"""
        return get_namespaces(self.__class__)

    @property
    def urirefs(self) -> Dict:
        """Return the urirefs of the class"""
        return get_urirefs(self.__class__)

    @classmethod
    def get_context(cls) -> Dict:
        """Return the context of the class"""
        return get_namespaces(cls)

    @classmethod
    def from_sparql(cls,
                    sparql_result: Result,
                    raise_on_error=True):
        """Initialize the class from a SPARQL result"""
        # sparql_result_dict = _sparql_result_to_dict(sparql_result)
        # first cluster by subject. a subject can be identified by type property
        subjects: Dict[str, Dict[str, Any]] = {}
        for row in sparql_result:
            row_dict = _sparql_result_to_dict(row)
            _id = row_dict.pop("id")
            if _id in subjects:
                for k, v in row_dict.items():
                    if k in subjects[_id]:
                        # already exists, make it a list
                        if v not in subjects[_id][k]:
                            if not isinstance(subjects[_id][k], list):
                                subjects[_id][k] = [subjects[_id][k]]
                            subjects[_id][k].append(v)
                    else:
                        subjects[_id][k] = v
            else:
                subjects[_id] = row_dict
        instances = []
        for k, v in subjects.items():
            try:
                i = cls.model_validate({"id": k, **v})
            except ValidationError as e:
                if raise_on_error:
                    raise e
                logger.error(f"Could not validate {v} to {cls.__name__}: {e}")
                continue
            instances.append(i)
        # instances = [cls.model_validate(v) for k, v in subjects.items()]
        return instances

    @classmethod
    def add_property(cls,
                     *,
                     name: str,
                     property_type: Any,
                     namespace: Optional[Union[HttpUrl, str]],
                     namespace_prefix: Optional[str],
                     default: Optional[Any] = None,
                     ):
        """Add a property to the class"""
        prop = Property(
            name=name,
            property_type=property_type,
            default=default,
            namespace=namespace,
            namespace_prefix=namespace_prefix
        )
        if not isinstance(prop, Property):
            raise TypeError(f"Cannot add property of type {type(prop)}. "
                            f"Expected a Property.")
        uri_ref_manager = URIRefManager.get(cls, {})
        uri_ref_manager[prop.name] = f"{prop.namespace_prefix}:{prop.name}"
        URIRefManager.data[cls] = uri_ref_manager

        namespace_manager = NamespaceManager.get(cls, {})
        namespace_manager[prop.namespace_prefix] = prop.namespace
        NamespaceManager.data[cls] = namespace_manager

    @classmethod
    def get_iri(cls, item):
        ns = get_namespaces(cls)
        uris = get_urirefs(cls)
        if item in uris:
            compact_uri = uris[item]
            prefix, name = compact_uri.split(':')
            namespace = ns[prefix]
            return f"{namespace}{name}"
        raise KeyError(f"Item {item} not found in urirefs of class {cls.__name__}.")

    @classmethod
    def create_query(cls,
                     select_vars: Optional[List[str]] = None,
                     subject: Union[str, rdflib.URIRef] = None,
                     limit: Optional[int] = None,
                     distinct: bool = False) -> str:
        """Generate a SPARQL query to find instances of this Thing subclass.

        - `select_vars`: list of variable names (including leading `?`) to select; defaults to `['?s']`.
        - `limit`: optional integer limit.
        - `distinct`: use `DISTINCT` in SELECT when True.
        """
        if subject is not None:
            if isinstance(subject, str):
                subj = f"<{subject}>"
            else:
                raise TypeError(f"Subject must be a str or rdflib.URIRef, not {type(subject)}")
        else:
            subj = "?id"

        if select_vars is None:
            _all_uris = get_urirefs(cls).copy()
            # _all_uris.pop(cls.__name__)
            _mros = cls.__mro__
            for mro in _mros:
                # remove all class names until Thing
                _all_uris.pop(mro.__name__)
                if mro == Thing:
                    break
            select_vars = [f"?{k}" for k in _all_uris.keys()]

        if isinstance(select_vars, str):
            select_vars = [select_vars]

        if subject is None:
            select_vars = [subj, *select_vars] if select_vars and subj not in select_vars else select_vars
            vars_to_select = list(select_vars) if select_vars else [subj]
        else:
            vars_to_select = list(select_vars) if select_vars else []

        # if include_label and "?label" not in vars_to_select:
        #     vars_to_select.append("?label")
        distinct_str = "DISTINCT " if distinct else ""
        select_clause = f"SELECT {distinct_str}{' '.join(vars_to_select)}"

        class_iri = cls.iri(compact=False)
        rdf_type = str(rdflib.RDF.type)
        # rdfs_label = "http://www.w3.org/2000/01/rdf-schema#label"

        where_lines = [f"{subj} <{rdf_type}> <{class_iri}> ."]
        # if include_label:
        #     where_lines.append(f"OPTIONAL {{ {subj} <{rdfs_label}> ?label . }}")

        # Add OPTIONAL patterns for any selected var that maps to a class property IRI.
        for var in vars_to_select:
            if not isinstance(var, str) or not var.startswith('?'):
                continue
            if var in (subj,):
                continue
            key = var[1:]
            iri = None
            try:
                iri = cls.iri(key, compact=False)
            except Exception:
                iri = None
            if iri:
                where_lines.append(f"OPTIONAL {{ {subj} <{iri}> {var} . }}")

        where_clause = "\n  ".join(where_lines)
        query = f"{select_clause}\nWHERE {{\n  {where_clause}\n}}"
        if limit is not None:
            query += f"\nLIMIT {int(limit)}"
        return query

    def validate(self,
                 shacl_source: Union[str, pathlib.Path] = None,
                 shacl_data: Union[str, rdflib.Graph] = None,
                 raise_on_error=True,
                 inference: str = 'rdfs',
                 abort_on_first: bool = False,
                 meta_shacl: bool = False,
                 advanced: bool = True,
                 ) -> ValidationResult:
        if shacl_source is not None and shacl_data is not None:
            raise ValueError("Cannot provide both shacl_source and shacl_data.")
        sh = _get_pyshacl()
        this_graph = rdflib.Graph()
        this_graph.parse(data=self.serialize("ttl"), format="ttl")  # TODO there should be a .to_graph() method

        if shacl_data is not None:
            if isinstance(shacl_data, rdflib.Graph):
                shacl_graph = shacl_data
            else:
                shacl_graph = rdflib.Graph()
                shacl_graph.parse(data=shacl_data, format="ttl")
        else:
            shacl_graph = rdflib.Graph()
            shacl_graph.parse(source=shacl_source)

        results = sh.validate(
            data_graph=this_graph,
            shacl_graph=shacl_graph,
            inference=inference,
            abort_on_first=abort_on_first,
            meta_shacl=meta_shacl,
            advanced=advanced,
        )
        conforms, results_graph, results_text = results
        if not conforms and raise_on_error:
            raise ValueError(f"SHACL validation failed:\n{results_text}")
        return ValidationResult(conforms, results_graph, results_text)


def _replace_context_url_with_prefix(value: str, context: Dict) -> str:
    for context_key, context_url in context.items():
        if value.startswith(context_url):
            return value.replace(context_url, context_key + ':')
    return value


def serialize(thing: Union[Thing, List[Thing]],
              format: str,
              context: Optional[Dict] = None,
              exclude_none: bool = True,
              resolve_keys: bool = True,
              base_uri: Optional[Union[str, AnyUrl]] = None,
              **kwargs):
    if not isinstance(thing, list):
        if isinstance(thing, Thing):
            return thing.serialize(
                format=format,
                context=context,
                exclude_none=exclude_none,
                resolve_keys=resolve_keys,
                base_uri=base_uri,
                **kwargs
            )
        else:
            raise TypeError(f"Cannot serialize object of type {type(thing)}. "
                            f"Expected a Thing or a list of Things.")
    serializations = []
    for t in thing:
        if not isinstance(t, Thing):
            raise TypeError(f"Cannot serialize object of type {type(t)}. "
                            f"Expected a Thing.")
        serializations.append(
            t.serialize(
                format=format,
                context=context,
                exclude_none=exclude_none,
                resolve_keys=resolve_keys,
                base_uri=base_uri,
                **kwargs
            )
        )
    graph = rdflib.Graph()
    for s in serializations:
        graph.parse(data=s, format=format)
    return graph.serialize(format=format, **kwargs)


def _parse_blank_node(_id, base_uri: Optional[Union[str, AnyUrl]]):
    if base_uri:
        base_uri = AnyUrl(base_uri)
    if base_uri is None:
        return _id
    if isinstance(_id, rdflib.BNode):
        return f"{base_uri}{_id}"
    if isinstance(_id, str) and _id.startswith('_:'):
        return f"{base_uri}{_id[2:]}"
    if isinstance(_id, str) and _id.startswith('http'):
        return _id
    if isinstance(_id, str) and _id.startswith('file://'):
        return _id
    if isinstance(_id, str) and _id.startswith('urn:'):
        return _id
    if isinstance(_id, str) and _id.startswith('bnode:'):
        return f"{base_uri}{_id[6:]}"
    if isinstance(_id, str) and _id.startswith('N'):
        # This is a blank node generated by rdflib
        return f"{base_uri}{_id}"
    warnings.warn(f"Could not parse blank node ID '{_id}'. ")
    return _id


def get_urirefs(cls: Thing) -> Dict:
    """Return the URIRefs of the class"""
    return URIRefManager[cls]


def get_namespaces(cls: Thing) -> Dict:
    """Return the namespaces of the class"""
    return NamespaceManager[cls]


def build(
        namespace: HttpUrl,
        namespace_prefix: str,
        class_name: str,
        properties: List[Union[Property, Dict]],
        baseclass=Thing) -> Type[Thing]:
    """Build a ThingModel class

    Parameters
    ----------
    namespace: str
        The namespace of the class
    namespace_prefix: str
        The namespace prefix of the class
    class_name: str
        The name of the class
    properties: Dict[str, Union[str, int, float, bool, datetime, BlankNodeType, None]]
        The properties of the class
    baseclass: Type[Thing]
        The base class to inherit from, default is Thing


    Returns
    -------
    Thing
        A Thing
    """
    _properties = []
    for prop in properties:
        if isinstance(prop, dict):
            _properties.append(Property(**prop))
        else:
            _properties.append(prop)

    annotations = {prop.name: prop.property_type for prop in _properties}
    default_values = {prop.name: prop.default for prop in _properties}

    new_cls = type(
        class_name,
        (baseclass,),
        {
            "__annotations__": annotations,  # Define field type
            **default_values,
        }
    )
    from ontolutils.classes.decorator import _decorate_urirefs, _add_namesapces
    _urirefs = {class_name: f"{namespace_prefix}:{class_name}"}
    _namespaces = {namespace_prefix: namespace}
    for prop in _properties:
        _ns = prop.namespace
        _nsp = prop.namespace_prefix
        if _ns is None:
            _ns = namespace
            _nsp = namespace_prefix
        _urirefs[prop.name] = f"{_nsp}:{prop.name}"
        if _nsp not in _namespaces:
            _namespaces[_nsp] = _ns

    _decorate_urirefs(new_cls, **_urirefs)
    _add_namesapces(new_cls, _namespaces)
    return new_cls


def is_semantically_equal(thing1, thing2) -> bool:
    # Prüfe, ob beide Instanzen von Thing sind
    if isinstance(thing1, Thing) and isinstance(thing2, Thing):
        return thing1.uri == thing2.uri
    return thing1 == thing2


def _sparql_result_to_dict(bindings, exclude_none=True):
    """Convert a SPARQL query result row to a dictionary."""
    if exclude_none:
        return {k: bindings[v] for k, v in bindings.labels.items() if bindings[v] is not None}
    return {k: bindings[v] for k, v in bindings.labels.items() if bindings[v]}
