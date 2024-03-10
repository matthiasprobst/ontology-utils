import json
import logging
import pathlib
from typing import Union, Dict, List, Optional

import rdflib

from .decorator import URIRefManager, NamespaceManager
from .thing import Thing
from .utils import split_URIRef

logger = logging.getLogger('ontolutils')


# def get_query_string(cls) -> str:
#     def _get_namespace(key):
#         ns = URIRefManager[cls].data.get(key, f'local:{key}')
#         if ':' in ns:
#             return ns
#         return f'{ns}:{key}'
#
#     # generate query automatically based on fields
#     fields = " ".join([f"?{k}" for k in cls.model_fields.keys() if k != 'id'])
#     # better in a one-liner:
#     query_str = "".join([f"PREFIX {k}: <{v}>\n" for k, v in NamespaceManager.namespaces.items()])
#
#     query_str += f"""
# SELECT ?id {fields}
# WHERE {{
#     ?id a <{_get_namespace(cls.__name__)}> ."""
#
#     for field in cls.model_fields.keys():
#         if field != 'id':
#             if cls.model_fields[field].is_required():
#                 query_str += f"\n    ?id {_get_namespace(field)} ?{field} ."
#             else:
#                 query_str += f"\n    OPTIONAL {{ ?id {_get_namespace(field)} ?{field} . }}"
#     query_str += "\n}"
#     return query_str


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


def _qurey_by_id(graph, id: Union[str, rdflib.URIRef]):
    _sub_query_string = """SELECT ?p ?o WHERE { <%s> ?p ?o }""" % id
    _sub_res = graph.query(_sub_query_string)
    out = {}
    for binding in _sub_res.bindings:
        ns, key = split_URIRef(binding['p'])
        out[key] = str(binding['o'])
    return out


def exists_as_type(object: str, graph):
    query = """SELECT ?object
WHERE {
  %s <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> ?object .
}""" % object
    out = graph.query(query)
    return len(out) == 1


def find_subsequent_fields(bindings, graph):
    out = {}
    for binding in bindings:
        p = binding['p'].__str__()
        _, predicate = split_URIRef(p)
        if predicate == 'type':
            continue
        objectn3 = binding['?o'].n3()
        object = binding['?o'].__str__()

        if exists_as_type(objectn3, graph):
            sub_query = """SELECT ?p ?o WHERE { <%s> ?p ?o }""" % object
            sub_res = graph.query(sub_query)
            assert len(sub_res) > 0
            _data = find_subsequent_fields(sub_res.bindings, graph)
            if predicate in out:
                if isinstance(out[predicate], list):
                    out[predicate].append(_data)
                else:
                    out[predicate] = [out[predicate], _data]
            else:
                out[predicate] = _data
        else:
            if predicate in out:
                if isinstance(out[predicate], list):
                    out[predicate].append(object)
                else:
                    out[predicate] = [out[predicate], object]
            else:
                out[predicate] = object
    return out


def expand_sparql_res(bindings, graph):
    out = {}
    for binding in bindings:
        _id = str(binding['?id'])  # .n3()
        if _id not in out:
            out[_id] = {}
        p = binding['p'].__str__()
        _, predicate = split_URIRef(p)

        if predicate == 'type':
            continue

        objectn3 = binding['?o'].n3()
        object = binding['?o'].__str__()

        if exists_as_type(objectn3, graph):
            sub_query = """SELECT ?p ?o WHERE { %s ?p ?o }""" % objectn3
            sub_res = graph.query(sub_query)
            assert len(sub_res) > 0
            _data = find_subsequent_fields(sub_res.bindings, graph)
            if predicate in out[_id]:
                if isinstance(out[_id][predicate], list):
                    out[_id][predicate].append(_data)
                else:
                    out[_id][predicate] = [out[_id][predicate], _data]
            else:
                out[_id][predicate] = _data
        else:
            if predicate in out[_id]:
                if isinstance(out[_id][predicate], list):
                    out[_id][predicate].append(object)
                else:
                    out[_id][predicate] = [out[_id][predicate], object]
            else:
                out[_id][predicate] = object

    return out


def dquery(type: str,
           source: Optional[Union[str, pathlib.Path]] = None,
           data: Optional[Union[str, Dict]] = None,
           context: Optional[Dict] = None) -> List[Dict]:
    """Return a list of resutls. The entries are dictionaries.

    Example
    -------
    >>> # Query all agents from the source file
    >>> import ontolutils
    >>> ontolutils.query(type='prov:Agent', source='agent1.jsonld')
    """
    g = rdflib.Graph()
    g.parse(source=source,
            data=data,
            format='json-ld',
            context=context)
    # for k, v in context.items():
    #     g.bind(k, v)

    prefixes = "".join([f"PREFIX {k}: <{p}>\n" for k, p in context.items() if not k.startswith('@')])

    query_str = f"""
    SELECT *
    WHERE {{{{
        ?id a {type}.
        ?id ?p ?o .
}}}}"""

    res = g.query(prefixes + query_str)

    if len(res) == 0:
        return None

    kwargs: Dict = expand_sparql_res(res.bindings, g)
    for id in kwargs:
        kwargs[id]['id'] = id
    return [v for v in kwargs.values()]


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

    prefixes = "".join([f"PREFIX {k}: <{p}>\n" for k, p in NamespaceManager[cls].items() if not k.startswith('@')])
    for k, p in NamespaceManager[cls].items():
        if k not in ns_keys:
            g.bind(k, p)
            # print(k)
        g.bind(k, p)

    if isinstance(data, dict):
        data = json.dumps(data)

    _context = cls.get_context()

    if context is None:
        context = {}

    if not isinstance(context, dict):
        raise TypeError(f"Context must be a dict, not {type(context)}")

    _context.update(context)

    g.parse(source=source,
            data=data,
            format='json-ld',
            context=_context)

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

    kwargs: Dict = expand_sparql_res(res.bindings, g)

    return [cls.model_validate({'id': k, **v}) for k, v in kwargs.items()]
