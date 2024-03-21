import abc
import json
import logging
import rdflib
from datetime import datetime
from pydantic import HttpUrl, FileUrl, BaseModel, ConfigDict
from typing import Dict, Union, Optional

from .decorator import urirefs, namespaces, URIRefManager, NamespaceManager, _is_http_url
from .typing import BlankNodeType
from .utils import split_URIRef

logger = logging.getLogger('ontolutils')

EXTRA = 'allow'  # or 'forbid' or 'ignore'


class ThingModel(BaseModel, abc.ABC):
    """Abstract base model class to be used by model classes used within ontolutils"""

    model_config = ConfigDict(extra=EXTRA)

    @abc.abstractmethod
    def _repr_html_(self) -> str:
        """Returns the HTML representation of the class"""


@namespaces(owl='http://www.w3.org/2002/07/owl#',
            rdfs='http://www.w3.org/2000/01/rdf-schema#')
@urirefs(Thing='owl:Thing', label='rdfs:label')
class Thing(ThingModel):
    """owl:Thing
    """
    id: Union[str, HttpUrl, FileUrl, BlankNodeType, None] = None  # @id
    label: str = None  # rdfs:label

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
                        exclude_none: bool = True) -> Dict:
        """Return the JSON-LD dictionary of the object. This will include the context
        and the fields of the object.

        Parameters
        ----------
        context: Optional[Union[Dict, str]]
            The context to use for the JSON-LD serialization. If a string is given, it will
            be interpreted as an import statement and will be added to the context.
        exclude_none: bool=True
            Exclude fields with None values

        Returns
        -------
        Dict
            The JSON-LD dictionary
        """
        logger.debug('Initializing RDF graph to dump the Thing to JSON-LD')

        # lets auto-generate the context
        at_context: Dict = NamespaceManager.get(self.__class__, {})

        if context is None:
            context = {}

        if not isinstance(context, dict):
            raise TypeError(f"Context must be a dict, not {type(context)}")

        at_context.update(**context)

        logger.debug(f'The context is "{at_context}".')

        def serialize_fields(
                obj: Union[ThingModel, int, str, float, bool, datetime],
                exclude_none: bool = True
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
            exclude_none: bool=True
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
            if uri_ref_manager is None:
                return obj

            try:
                if exclude_none:
                    serialized_fields = {}
                    for k in obj.model_dump(exclude_none=True):
                        value = getattr(obj, k)
                        if value is not None and k not in ('id', '@id'):
                            iri = uri_ref_manager.get(k, k)
                            if _is_http_url(iri):
                                serialized_fields[iri] = value
                            if isinstance(value, str):  # this turn URLs into base strings
                                serialized_fields[iri] = str(value)
                            else:
                                serialized_fields[iri] = value
                else:
                    serialized_fields = {}
                    for k in obj.model_dump(exclude_none=True):
                        value = getattr(obj, k)
                        if value not in ('id', '@id'):
                            iri = uri_ref_manager[k]
                            if _is_http_url(iri):
                                serialized_fields[k] = value
                            else:
                                serialized_fields[iri] = value
            except AttributeError as e:
                raise AttributeError(f"Could not serialize {obj} ({obj.__class__}). Orig. err: {e}") from e

            if obj.model_config['extra'] == 'allow':
                for k, v in obj.model_extra.items():
                    iri = uri_ref_manager.get(k, k)
                    if _is_http_url(iri):
                        serialized_fields[k] = v
                    else:
                        serialized_fields[iri] = v

            # datetime
            for k, v in serialized_fields.copy().items():
                _field = serialized_fields.pop(k)
                key = k
                if isinstance(v, datetime):
                    serialized_fields[key] = serialize_fields(v)
                elif isinstance(v, Thing):
                    serialized_fields[key] = serialize_fields(v, exclude_none=exclude_none)
                elif isinstance(v, list):
                    serialized_fields[key] = [serialize_fields(i, exclude_none=exclude_none) for i in v]
                else:
                    serialized_fields[key] = str(v)

            _type = URIRefManager[obj.__class__].get(obj.__class__.__name__, obj.__class__.__name__)

            out = {"@type": _type, **serialized_fields}
            # if no ID is given, generate a local one:
            if obj.id is not None:
                out["@id"] = obj.id
            else:
                out["@id"] = rdflib.BNode()
            return out

        serialization = serialize_fields(self, exclude_none=exclude_none)

        jsonld = {
            "@context": at_context,
            **serialization
        }
        return jsonld

    def model_dump_jsonld(self,
                          context: Optional[Dict] = None,
                          exclude_none: bool = True,
                          rdflib_serialize: bool = False) -> str:
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

        Returns
        -------
        str
            The JSON-LD string
        """
        jsonld_dict = self.get_jsonld_dict(
            context=context,
            exclude_none=exclude_none
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
                           indent=4)

    def __repr__(self):
        _fields = {k: getattr(self, k) for k in self.model_fields if getattr(self, k) is not None}
        repr_fields = ", ".join([f"{k}={v}" for k, v in _fields.items()])
        if self.model_config['extra'] == 'allow':
            if len(self.model_extra) > 0:
                repr_extra = ", ".join([f"{k}={v}" for k, v in self.model_extra.items()])
                return f"{self.__class__.__name__}({repr_fields}, {repr_extra})"
        return f"{self.__class__.__name__}({repr_fields})"

    def __str__(self):
        return self.__repr__()

    def _repr_html_(self) -> str:
        """Returns the HTML representation of the class"""
        _fields = {k: getattr(self, k) for k in self.model_fields if getattr(self, k) is not None}
        repr_fields = ", ".join([f"{k}={v}" for k, v in _fields.items()])
        return f"{self.__class__.__name__}({repr_fields})"

    @classmethod
    def from_jsonld(cls, source=None, data=None, limit=None, context=None):
        """Initialize the class from a JSON-LD source

        Note the inconsistency in the schema.org protocol. Codemeta for instance uses http whereas
        https is the current standard. This repo only works with https. If you have a http schema,
        this method will replace http with https.
        """
        from . import query
        if data is not None and isinstance(data, str):
            if 'http://schema.org/' in data:
                print('Replacing http with https in the JSON-LD data. This is a workaround for the schema.org inconsistency.')
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

    @classmethod
    def get_context(cls):
        """Return the context of the class"""
        return NamespaceManager[cls]

    @property
    def namespaces(self):
        """Return the namespaces of the class"""
        return NamespaceManager[self.__class__]

    @property
    def urirefs(self):
        """Return the URIRefs of the class"""
        return URIRefManager[self.__class__]
