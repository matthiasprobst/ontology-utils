import abc
import json
import uuid
from datetime import datetime
from typing import Dict, Union

import rdflib
from pydantic import BaseModel
from pydantic import HttpUrl, FileUrl

from .decorator import urirefs, namespaces, URIRefManager, NamespaceManager
from .model import ThingModel
from .typing import BlankNodeType
from .utils import split_URIRef


class ThingModel(abc.ABC, BaseModel):
    """Abstract class to be used by model classes used within PIVMetalib"""

    class Config:
        validate_assignment = True
        # extra = Extra.forbid
        extra = 'allow'

    @abc.abstractmethod
    def _repr_html_(self) -> str:
        """Returns the HTML representation of the class"""


def serialize_fields(obj, exclude_none: bool = True) -> Dict:
    """Serializes the fields of a Thing object into a json-ld dictionary (without context!)"""

    if exclude_none:
        serialized_fields = {URIRefManager[obj.__class__][k]: getattr(obj, k) for k in obj.model_fields if
                             getattr(obj, k) is not None and k not in ('id', '@id')}
        # serialized_fields = {_parse_key(k): getattr(obj, k) for k in obj.model_fields if getattr(obj, k) is not None}
    else:
        serialized_fields = {URIRefManager[obj.__class__][k]: getattr(obj, k) for k in obj.model_fields if
                             k not in ('id', '@id')}
        # serialized_fields = {_parse_key(k): getattr(obj, k) for k in obj.model_fields}
    if obj.Config.extra == 'allow':
        for k, v in obj.model_extra.items():
            serialized_fields[URIRefManager[obj.__class__].get(k, k)] = v

    # datetime
    for k, v in serialized_fields.copy().items():
        _field = serialized_fields.pop(k)
        key = k
        if isinstance(v, datetime):
            serialized_fields[key] = v.isoformat()
        elif isinstance(v, Thing):
            serialized_fields[key] = serialize_fields(v, exclude_none=exclude_none)
        elif isinstance(v, list):
            serialized_fields[key] = [serialize_fields(i, exclude_none=exclude_none) for i in v]
        else:
            serialized_fields[key] = str(v)

    _type = URIRefManager[obj.__class__].get(obj.__class__.__name__, obj.__class__.__name__)

    return {"@type": _type, **serialized_fields,
            "@id": obj.id if obj.id is not None else f'local:{str(uuid.uuid4())}'}


def _repr(obj):
    if hasattr(obj, '_repr_html_'):
        return obj._repr_html_()
    if isinstance(obj, list):
        return f"[{', '.join([_repr(i) for i in obj])}]"
    if isinstance(obj, rdflib.URIRef):
        return str(obj)
    return repr(obj)


def _html_repr(obj):
    if hasattr(obj, '_repr_html_'):
        return obj._repr_html_()
    if isinstance(obj, list):
        return f"[{', '.join([_repr(i) for i in obj])}]"
    if isinstance(obj, rdflib.URIRef):
        return f"<a href='{obj}'>{obj}</a>"
    return repr(obj)


def dump_hdf(g, data: Dict, iris: Dict = None):
    """Write a dictionary to a hdf group. Nested dictionaries result in nested groups"""
    iris = iris or {}
    for k, v in data.items():
        if isinstance(v, dict):
            sub_g = g.create_group(k)
            if k in iris:
                sub_g.iri = iris[k]
            dump_hdf(sub_g, v, iris)
        else:
            g.attrs[k] = v


@namespaces(owl='http://www.w3.org/2002/07/owl#',
            rdfs='http://www.w3.org/2000/01/rdf-schema#',
            local='http://example.com/')
@urirefs(Thing='owl:Thing', label='rdfs:label')
class Thing(ThingModel):
    """owl:Thing
    """
    id: Union[str, HttpUrl, FileUrl, BlankNodeType, None] = None  # @id
    label: str = None  # rdfs:label

    def __lt__(self, other):
        if self.id is None or other.id is None:
            return False
        return self.id <= other.id

    def dump_jsonld(self,
                    context=None,
                    exclude_none: bool = True,
                    local_namespace: HttpUrl = 'https://local-domain.org/') -> str:
        """alias for model_dump_json()"""

        # if context is None:
        #     from . import CONTEXT
        #     context = CONTEXT

        g = rdflib.Graph()

        at_context: Dict = {"local": local_namespace}
        if isinstance(context, str):
            at_context['@import'] = context
        else:
            at_context.update(**context)

        jsonld = {
            "@context": at_context,
            "@graph": [
                serialize_fields(self, exclude_none=exclude_none)
            ]
        }

        g.parse(data=json.dumps(jsonld), format='json-ld')
        if context:
            return g.serialize(format='json-ld',
                               context=at_context,
                               indent=4)
        return g.serialize(format='json-ld', indent=4)

    def dump_hdf(self, g):
        """Write the object to an hdf group. Nested dictionaries result in nested groups"""

        def _get_explained_dict(obj):
            model_fields = {k: getattr(obj, k) for k in obj.model_fields if getattr(obj, k) is not None}
            model_fields.pop('id', None)
            _context_manager = URIRefManager[obj.__class__]
            _namespace_manager = NamespaceManager[obj.__class__]
            namespaced_fields = {}

            assert isinstance(obj, ThingModel)

            rdf_type = URIRefManager[obj.__class__][obj.__class__.__name__]
            if ':' in rdf_type:
                ns, field = rdf_type.split(':', 1)
                at_type = f'{_namespace_manager[ns]}{field}'
            else:
                at_type = rdf_type
            namespaced_fields[('http://www.w3.org/1999/02/22-rdf-syntax-ns#type', '@type')] = at_type
            if obj.id is not None:
                namespaced_fields[('http://www.w3.org/1999/02/22-rdf-syntax-ns#id', '@id')] = obj.id

            for k, v in model_fields.items():
                nskey = _context_manager.get(k, k)
                if ':' in nskey:
                    ns, field = nskey.split(':', 1)
                    ns_iri = _namespace_manager.get(ns, None)
                    explained_key = (f'{ns_iri}{k}', k)
                else:
                    explained_key = (None, k)

                # namespaced_key = _resolve_namespaced_field(_context_manager.get(k, k))
                # namespace_dict[k] = _context_manager.get(key, key)
                if isinstance(v, ThingModel):
                    namespaced_fields[explained_key] = _get_explained_dict(v)
                else:
                    if isinstance(v, list):
                        if all(isinstance(i, ThingModel) for i in v):
                            namespaced_fields[explained_key] = [_get_explained_dict(i) for i in v]
                        else:
                            namespaced_fields[explained_key] = v
                    else:
                        namespaced_fields[explained_key] = v
            return namespaced_fields

        def _dump_hdf(g, explained_data: Dict):
            for (iri, key), v in explained_data.items():
                if isinstance(v, dict):
                    sub_g = g.create_group(key)
                    if iri:
                        sub_g.iri.subject = iri
                    _dump_hdf(sub_g, v)
                elif isinstance(v, list):
                    sub_g = g.create_group(key)
                    if iri:
                        sub_g.iri.subject = iri
                    for i, item in enumerate(v):
                        assert isinstance(item, dict)
                        if isinstance(item, dict):
                            sub_sub_g = sub_g.create_group(str(i))
                            _dump_hdf(sub_sub_g, item)
                else:
                    g.attrs[key] = v
                    if iri:
                        g.attrs[key, iri] = v

        _dump_hdf(g, _get_explained_dict(self))

    def __repr__(self):
        _fields = {k: getattr(self, k) for k in self.model_fields if getattr(self, k) is not None}
        repr_fields = ", ".join([f"{k}={v}" for k, v in _fields.items()])
        if self.Config.extra == 'allow':
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
    def from_jsonld(cls, source):
        """Initialize the class from a JSON-LD source"""
        from . import query
        return query(cls, source)

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
