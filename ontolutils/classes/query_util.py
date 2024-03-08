import json
import logging
import pathlib
from typing import Union, Dict, List, Optional

import rdflib

from .decorator import URIRefManager, NamespaceManager
from .thing import Thing
from .utils import split_URIRef

logger = logging.getLogger('ontolutils')


def get_query_string(cls) -> str:
    def _get_namespace(key):
        ns = URIRefManager[cls].data.get(key, f'local:{key}')
        if ':' in ns:
            return ns
        return f'{ns}:{key}'

    # generate query automatically based on fields
    fields = " ".join([f"?{k}" for k in cls.model_fields.keys() if k != 'id'])
    # better in a one-liner:
    query_str = "".join([f"PREFIX {k}: <{v}>\n" for k, v in NamespaceManager.namespaces.items()])

    query_str += f"""
SELECT ?id {fields}
WHERE {{
    ?id a {_get_namespace(cls.__name__)} ."""

    for field in cls.model_fields.keys():
        if field != 'id':
            if cls.model_fields[field].is_required():
                query_str += f"\n    ?id {_get_namespace(field)} ?{field} ."
            else:
                query_str += f"\n    OPTIONAL {{ ?id {_get_namespace(field)} ?{field} . }}"
    query_str += "\n}"
    return query_str


def get_query_string(cls) -> str:
    def _get_namespace(key):
        ns = URIRefManager[cls].get(key, f'local:{key}')
        if ':' in ns:
            return ns
        return f'{ns}:{key}'

    # generate query automatically based on fields
    # fields = " ".join([f"?{k}" for k in cls.model_fields.keys() if k != 'id'])
    # better in a one-liner:
    # query_str = "".join([f"PREFIX {k}: <{v}>\n" for k, v in NamespaceManager.namespaces.items()])

    query_str = f"""
SELECT *
WHERE {{{{
    ?id a {_get_namespace(cls.__name__)} .
    ?id ?p ?o ."""

    # for field in cls.model_fields.keys():
    #     if field != 'id':
    #         if cls.model_fields[field].is_required():
    #             query_str += f"\n    ?id {_get_namespace(field)} ?{field} ."
    #         else:
    #             query_str += f"\n    OPTIONAL {{ ?id {_get_namespace(field)} ?{field} . }}"
    query_str += "\n}}"
    return query_str


class QueryResult:

    def __init__(self, cls, source: Union[str, Dict, pathlib.Path], n3dict):
        self.cls = cls
        self.source = source  # Dict or json-ld file!
        for k, v in n3dict.items():
            assert k.startswith('?')
            if v.startswith('<') and k != '?id':
                # it is a URIRef
                mfield = cls.model_fields[k[1:]]
                if isinstance(mfield, Thing):
                    # it is a Thing
                    setattr(self, k[1:], mfield.cls(id=v[1:-1]))
                else:
                    flag = False
                    for arg in mfield.annotation.__args__:
                        if issubclass(arg, Thing):
                            # it is a Thing
                            setattr(self, k[1:], arg(id=v[1:-1]))
                            flag = True
                            break
                    if not flag:
                        setattr(self, k[1:], v[1:-1])
            else:
                setattr(self, k[1:], v[1:-1])

    def __repr__(self):
        return f"{self.__class__.__name__}(cls={self.cls.__name__})"

    def parse(self):
        return self.cls.model_validate(self.model_dump())


def _qurey_by_id(graph, id: Union[str, rdflib.URIRef]):
    _sub_query_string = """SELECT ?p ?o WHERE { <%s> ?p ?o }""" % id
    _sub_res = graph.query(_sub_query_string)
    out = {}
    for binding in _sub_res.bindings:
        ns, key = split_URIRef(binding['p'])
        out[key] = str(binding['o'])
    return out


def query(cls: Thing,
          source: Optional[Union[str, pathlib.Path]] = None,
          data: Optional[Union[str, Dict]] = None,
          context: Optional[Union[Dict, str]] = None) -> List:
    """Return a generator of results from the query.

    Parameters
    ----------
    cls : Thing
        The class to query
    source: Optional[Union[str, pathlib.Path]]
        The source of the json-ld file. see json.dump() for details
    data : Optional[Union[str, Dict]]
        The data of the json-ld file
    context : Optional[Union[Dict, str]]
        The context of the json-ld file
    """

    query_string = get_query_string(cls)
    g = rdflib.Graph()

    ns_keys = [_ns[0] for _ns in g.namespaces()]

    prefixes = "".join([f"PREFIX {k}: <{p}>\n" for k, p in NamespaceManager[cls].items()])
    for k, p in NamespaceManager[cls].items():
        if k not in ns_keys:
            g.bind(k, p)
            # print(k)
        g.bind(k, p)

    if isinstance(data, dict):
        data = json.dumps(data)
    g.parse(source=source, data=data, format='json-ld', context=context)

    gquery = prefixes + query_string
    logger.debug(f"Querying {cls.__name__} with query: {gquery}")
    res = g.query(gquery)

    # print(prefixes+ query_string)

    if len(res) == 0:
        return

    # get model field dict as IRI
    # e.g. {'http://www.w3.org/2000/01/rdf-schema#description': 'description'}
    model_field_iri = {}
    for model_field, iri in URIRefManager[cls].items():
        ns, key = iri.split(':', 1)
        ns_iri = NamespaceManager[cls].get(ns, None)
        if ns_iri is None:
            full_iri = key
        else:
            full_iri = f'{NamespaceManager[cls].get(ns)}{key}'
        model_field_iri[full_iri] = model_field

    n3dict = {}
    for binding in res.bindings:
        _id = binding['?id'].n3()
        if _id not in n3dict:
            n3dict[_id] = {}
        p = binding['p'].__str__()
        _, predicate = split_URIRef(p)
        objectn3 = binding['?o'].n3()
        object = binding['?o'].__str__()
        if objectn3.startswith('<'):
            # it is a URIRef
            if predicate != 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type':  # and _o may be an ID
                assert object.startswith('http') or object.startswith('_:')
                object = _qurey_by_id(g, object)

        if predicate in n3dict[_id]:
            if isinstance(n3dict[_id][predicate], list):
                n3dict[_id][predicate].append(object)
            else:
                n3dict[_id][predicate] = [n3dict[_id][predicate], object]
        else:
            n3dict[_id][predicate] = object

    results = []
    for _id, _params in n3dict.items():
        results.append(cls.model_validate({'id': _id[1:-1], **_params}))
    return results
