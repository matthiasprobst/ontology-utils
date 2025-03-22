import abc
import json
import logging
import pathlib
import warnings
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Union, Optional, Any, List, Type

import rdflib
from pydantic import HttpUrl, FileUrl, BaseModel, ConfigDict, Field
from pydantic import field_validator
from rdflib.plugins.shared.jsonld.context import Context

from .decorator import urirefs, namespaces, URIRefManager, NamespaceManager, _is_http_url
from .typing import BlankNodeType
from .utils import split_URIRef
from .. import get_config
from ..config import PYDANTIC_EXTRA

logger = logging.getLogger('ontolutils')


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
        for field, meta in self.model_fields.items():
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


def build_blank_n3() -> str:
    _blank_node = rdflib.BNode().n3()
    bnode_prefix_name = get_config("blank_node_prefix_name")
    if bnode_prefix_name is None:
        return _blank_node
    return _blank_node.replace('_:', bnode_prefix_name)


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
    id: Optional[Union[str, HttpUrl, FileUrl, BlankNodeType, None]] = Field(default_factory=build_blank_n3)  # @id
    label: str = None  # rdfs:label
    relation: Optional[Union[str, HttpUrl, FileUrl, BlankNodeType, ThingModel]] = None
    closeMatch: Optional[Union[str, HttpUrl, FileUrl, BlankNodeType, ThingModel]] = None
    exactMatch: Optional[Union[str, HttpUrl, FileUrl, BlankNodeType, ThingModel]] = None

    @field_validator('id')
    @classmethod
    def _id(cls, id: Optional[Union[str, HttpUrl, FileUrl, BlankNodeType]]) -> str:
        if id is None:
            return build_blank_n3()
        return str(id)

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
                        context: Optional[Union[Dict, str]] = None,
                        exclude_none: bool = True,
                        resolve_keys: bool = False,
                        assign_bnode: bool = True) -> Dict:
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
        assign_bnode: bool=True
            Assigns a blank node if no ID is set.

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
            if isinstance(obj, datetime):
                return obj.isoformat()

            uri_ref_manager = URIRefManager.get(obj.__class__, None)
            at_context.update(NamespaceManager.get(obj.__class__, {}))

            obj_ctx = Context(source={**context,
                                      **NamespaceManager.get(obj.__class__, {}),
                                      **URIRefManager.get(obj.__class__, {})})

            if uri_ref_manager is None:
                return str(obj)

            try:
                serialized_fields = {}
                for k in obj.model_dump(exclude_none=_exclude_none):
                    value = getattr(obj, k)
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
                else:
                    serialized_fields[key] = _serialize_fields(v, _exclude_none=_exclude_none)

            _type = URIRefManager[obj.__class__].get(obj.__class__.__name__, obj.__class__.__name__)

            out = {"@type": _type, **serialized_fields}
            # if no ID is given, generate a local one:
            if obj.id is not None:
                out["@id"] = obj.id
            else:
                if assign_bnode:
                    out["@id"] = rdflib.BNode().n3()
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
                  assign_bnode: bool = True,
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
            assign_bnode=assign_bnode
        )
        jsonld_str = json.dumps(jsonld_dict)

        logger.debug(f'Parsing the following jsonld dict to the RDF graph: {jsonld_str}')
        g = rdflib.Graph()
        g.parse(data=jsonld_str, format='json-ld')

        _context = jsonld_dict.get('@context', {})
        if context:
            _context.update(context)

        return g.serialize(format=format,
                           context=_context,
                           **kwargs)

    def model_dump_jsonld(self,
                          context: Optional[Dict] = None,
                          exclude_none: bool = True,
                          rdflib_serialize: bool = False,
                          resolve_keys: bool = True,
                          assign_bnode: bool = True,
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
        assign_bnode: bool=True
            Assigns a blank node if no ID is set.
        indent: int=4
            The indent of the JSON-LD string

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
            assign_bnode=assign_bnode
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

    def __repr__(self, limit: Optional[int] = None):
        _fields = {k: getattr(self, k) for k in self.model_fields if getattr(self, k) is not None}
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
