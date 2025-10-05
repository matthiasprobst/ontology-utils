import abc
import json
import logging
import pathlib
import warnings
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Union, Optional, Any, List, Type
from urllib.parse import urlparse

import rdflib
from pydantic import AnyUrl, HttpUrl, FileUrl, BaseModel, ConfigDict, Field, field_validator, model_validator
from pydantic import field_serializer
from rdflib.plugins.shared.jsonld.context import Context

from .decorator import urirefs, namespaces, URIRefManager, NamespaceManager, _is_http_url
from .typing import BlankNodeType
from .utils import split_URIRef
from .. import get_config
from ..config import PYDANTIC_EXTRA

logger = logging.getLogger('ontolutils')
URL_SCHEMES = {"http", "https", "urn", "doi"}


@dataclass
class Property:
    name: str
    property_type: Any
    default: Optional[Any] = None
    namespace: Optional[HttpUrl] = None
    namespace_prefix: Optional[str] = None

    def __post_init__(self):
        if self.namespace is None and self.namespace_prefix is not None:
            raise ValueError("If namespace_prefix is given, then namespace must be given as well.")
        if self.namespace_prefix is None and self.namespace is not None:
            raise ValueError("If namespace is given, then namespace_prefix must be given as well.")


class ThingModel(BaseModel, abc.ABC, validate_assignment=True):
    """Abstract base model class to be used by model classes used within ontolutils"""

    model_config = ConfigDict(extra=PYDANTIC_EXTRA, populate_by_name=True)

    def __getattr__(self, item):
        for field, meta in self.__class__.model_fields.items():
            if meta.alias == item:
                return getattr(self, field)
        return super().__getattr__(item)

    @abc.abstractmethod
    def _repr_html_(self) -> str:
        """Returns the HTML representation of the class"""


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
    iri = str(iri)
    try:
        s = str(iri)  # works for Pydantic URL types and plain strings
    except Exception:
        return False
    scheme = urlparse(s).scheme.lower()
    return scheme in URL_SCHEMES


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
        # Avoid importing rdflib unless needed
        try:
            import rdflib  # type: ignore
            RDFLIB_AVAILABLE = True
        except Exception:
            RDFLIB_AVAILABLE = False

        if isinstance(v, cls):
            return v
        if RDFLIB_AVAILABLE:
            import rdflib  # type: ignore
            if isinstance(v, rdflib.Literal):
                return {"value": str(v), "lang": v.language}

        if isinstance(v, dict):
            return v

        if isinstance(v, str):
            value, lang = _split_value_lang(v)
            return {"value": value, "lang": lang}

        if isinstance(v, list):
            return [cls.model_validate(_v) for _v in v]

        raise TypeError("LangString must be a str, dict, rdflib.Literal or LangString instance")

    def __str__(self):
        return f"{self.value}@{self.lang}" if self.lang else self.value

    def to_dict(self):
        return {"value": self.value, "lang": self.lang}

    @field_serializer("value", "lang")
    def _identity(self, v):
        return v

    def __eq__(self, other):
        """Equality comparison with another LangString or a plain string."""
        if isinstance(other, LangString):
            return self.value == other.value and self.lang == other.lang
        if isinstance(other, str):
            return self.value == self.value
        raise TypeError(f"Cannot compare LangString with {type(other)}")


def serialize_lang_str_field(lang_str: LangString):
    if lang_str.lang is None:
        return lang_str.value
    result = {"@value": lang_str.value, "@language": lang_str.lang}
    return result


@namespaces(owl='http://www.w3.org/2002/07/owl#',
            rdfs='http://www.w3.org/2000/01/rdf-schema#',
            dcterms='http://purl.org/dc/terms/',
            skos='http://www.w3.org/2004/02/skos/core#',
            )
@urirefs(Thing='owl:Thing',
         label='rdfs:label',
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
    id: Optional[Union[str, HttpUrl, FileUrl, BlankNodeType, None]] = Field(default_factory=build_blank_id)  # @id
    label: Optional[Union[LangString, List[LangString]]] = None  # rdfs:label
    relation: Optional[Union[str, HttpUrl, FileUrl, BlankNodeType, ThingModel]] = None
    closeMatch: Optional[Union[str, HttpUrl, FileUrl, BlankNodeType, ThingModel]] = None
    exactMatch: Optional[Union[str, HttpUrl, FileUrl, BlankNodeType, ThingModel]] = None

    class Config:
        arbitrary_types_allowed = True

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

    @field_validator('id', mode="before")
    @classmethod
    def _id(cls, id: Optional[Union[str, HttpUrl, FileUrl, BlankNodeType]]) -> str:
        if id is None:
            return build_blank_n3()
        if isinstance(id, rdflib.URIRef):
            return id.n3()
        if isinstance(id, rdflib.BNode):
            return id.n3()
        if not isinstance(id, str):
            raise TypeError(
                f'The ID must be a string, HttpUrl, FileUrl or BlankNodeType but got {type(id)}.'
            )
        if id.startswith('http'):
            return str(HttpUrl(id))
        if id.startswith('file'):
            return str(FileUrl(id))
        if id.startswith('_:'):
            return id  # this is a blank node
        raise ValueError(
            f'The ID must be a valid IRI or blank node but got "{id}". '
            'It must start with "_:", "http", "file".'
        )

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
            if isinstance(obj, (int, str, float, bool)):
                return obj
            if isinstance(obj, LangString):
                return serialize_lang_str_field(obj)
            if isinstance(obj, datetime):
                return obj.isoformat()

            uri_ref_manager = URIRefManager.get(obj.__class__, None)
            at_context.update(NamespaceManager.get(obj.__class__, {}))

            if isinstance(obj, ThingModel):
                if obj.model_extra:
                    for extra in obj.model_extra.values():
                        if isinstance(extra, URIValue):
                            at_context[extra.prefix] = extra.namespace

            obj_ctx = Context(source={**context,
                                      **NamespaceManager.get(obj.__class__, {}),
                                      **URIRefManager.get(obj.__class__, {})})

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
        return query(cls, source=source, data=data, limit=limit, context=context)

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
        ns, key = split_URIRef(iri_short)
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


def _replace_context_url_with_prefix(value: str, context: Dict) -> str:
    for context_key, context_url in context.items():
        if value.startswith(context_url):
            return value.replace(context_url, context_key + ':')
    return value


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
