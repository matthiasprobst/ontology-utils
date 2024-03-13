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


def get_query_string(cls, limit: int = None) -> str:
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
WHERE {{
    ?id a {_get_namespace(cls.__name__)} .
    ?id ?p ?o ."""
    if limit is not None:
        query_str += f"""
}} LIMIT {limit}"""
    else:
        query_str += "\n}"
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


def get_collection(node: str, graph):
    """see https://www.w3.org/TR/rdf-schema/#ch_collectionvocab """
    if not rdflib.BNode(node).startswith('_:'):
        return []

    query = """
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
SELECT ?x ?first ?rest
WHERE {
  ?x rdf:first ?first .
  ?x rdf:rest ?rest .
  FILTER isBlank(?x)
}"""
    out = graph.query(query)
    return out


def is_rest_in_list_of_things(node: str, graph):
    query = """SELECT ?subject
WHERE {
  ?subject <http://www.w3.org/1999/02/22-rdf-syntax-ns#rest> %s .
}""" % node
    out = graph.query(query)
    return len(out) == 1


def find_subsequent_fields(bindings, graph, add_type):
    out = {}
    for binding in bindings:
        p = binding['p'].__str__()
        _, predicate = split_URIRef(p)
        if predicate == 'type':
            if add_type:
                out['@type'] = binding['o'].__str__()
            continue
        objectn3 = binding['?o'].n3()
        object = binding['?o'].__str__()

        # if object is a node, two scenarios are possible (to my knowledge):
        # 1. the node describes a type. exists_as_type(objectn3, graph) is True.
        #          then in the data, we can find (_obj | rdf:type | XYZ)
        # 2. The node is in a list. get_collection(objectn3, graph) is True.
        if exists_as_type(objectn3, graph):
            sub_query = """SELECT ?p ?o WHERE { <%s> ?p ?o }""" % object
            sub_res = graph.query(sub_query)
            assert len(sub_res) > 0
            _data = find_subsequent_fields(sub_res.bindings, graph, add_type)
            if predicate in out:
                if isinstance(out[predicate], list):
                    out[predicate].append(_data)
                else:
                    out[predicate] = [out[predicate], _data]
            else:
                out[predicate] = _data
        else:
            if objectn3.startswith('_:'):
                # is a blank node, not a type. maybe starts with?
                collection = get_collection(objectn3, graph)
                for col in collection:
                    _node, _first, _rest = col
                    assert _first.startswith('http')
                    sub_query = """SELECT ?p ?o WHERE { <%s> ?p ?o }""" % _first
                    sub_res = graph.query(sub_query)
                    assert len(sub_res) > 0
                    _data = find_subsequent_fields(sub_res.bindings, graph, add_type)
                    out['id'] = _first

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


def expand_sparql_res(bindings,
                      graph,
                      add_type: bool,
                      add_context: bool):
    out = {}

    for binding in bindings:
        _id = str(binding['?id'])  # .n3()
        if _id not in out:
            out[_id] = {}
            if add_context:
                out[_id] = {'@context': {}}
        p = binding['p'].__str__()
        _, predicate = split_URIRef(p)

        if predicate == 'type':
            if add_type:
                out[_id]['@type'] = str(binding['o'])
            continue
        if add_context:
            out[_id]['@context'][predicate] = str(p)

        objectn3 = binding['?o'].n3()
        object = binding['?o'].__str__()

        if exists_as_type(objectn3, graph):
            sub_query = """SELECT ?p ?o WHERE { %s ?p ?o }""" % objectn3
            sub_res = graph.query(sub_query)
            assert len(sub_res) > 0
            _data = find_subsequent_fields(sub_res.bindings, graph, add_type)
            if predicate in out[_id]:
                if isinstance(out[_id][predicate], list):
                    out[_id][predicate].append(_data)
                else:
                    out[_id][predicate] = [out[_id][predicate], _data]
            else:
                out[_id][predicate] = _data
        else:
            print(predicate, objectn3)
            if objectn3.startswith('_:'):
                # is a blank node, not a type. maybe starts with?
                collection = get_collection(objectn3, graph)
                for col in collection:
                    _node, _first, _rest = col
                    assert _first.startswith('http')
                    sub_query = """SELECT ?p ?o WHERE { <%s> ?p ?o }""" % _first
                    sub_res = graph.query(sub_query)
                    assert len(sub_res) > 0
                    _data = find_subsequent_fields(sub_res.bindings, graph, add_type)
                    out[_id]['id'] = _first

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
    >>> ontolutils.dquery(type='prov:Agent', source='agent1.jsonld')
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

    kwargs: Dict = expand_sparql_res(res.bindings, g, True, True)
    for id in kwargs:
        kwargs[id]['id'] = id
    return [v for v in kwargs.values()]


def query(cls: Thing,
          source: Optional[Union[str, pathlib.Path]] = None,
          data: Optional[Union[str, Dict]] = None,
          context: Optional[Union[Dict, str]] = None,
          limit: Optional[int] = None) -> Union[Thing, List]:
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
    limit: Optional[int]
        The limit of the query. Default is None (no limit).
        If limit equals to 1, the result will be a single object, not a list.
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
    # print(prefixes + query_string)
    res = g.query(gquery)

    if len(res) == 0:
        return

    kwargs: Dict = expand_sparql_res(res.bindings, g, False, False)
    if limit is not None:
        out = []
        for i, (k, v) in enumerate(kwargs.items()):
            if limit == 1:
                return cls.model_validate({'id': k, **v})
            out.append(cls.model_validate({'id': k, **v}))
            if i == limit:
                return out
    return [cls.model_validate({'id': k, **v}) for k, v in kwargs.items()]
