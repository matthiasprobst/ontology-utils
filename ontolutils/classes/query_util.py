"""This module contains the query utility functions for the Thing class."""
import json
import logging
import pathlib
import rdflib
from typing import Union, Dict, List, Optional

from .decorator import URIRefManager, NamespaceManager
from .thing import Thing
from .utils import split_URIRef

logger = logging.getLogger('ontolutils')


def process_object(
        _id,
        predicate,
        obj: Union[rdflib.URIRef, rdflib.BNode, rdflib.Literal],
        graph,
        add_type):
    """Process the object of a triple."""
    if isinstance(obj, rdflib.Literal):
        logger.debug(f'Object "{obj}" for predicate "{predicate}" is a literal.')
        return str(obj)

    if isinstance(obj, rdflib.BNode):
        logger.debug(f'"{predicate}" has blank node obj! not optimal... difficult to find children...')
        # find children for predicate with blank node obj
        sub_data = {}
        # collection = []
        for (s, p, o) in graph:
            # logger.debug(s, p, o, obj)
            if str(s) == str(obj):
                if isinstance(o, rdflib.Literal):
                    _, key = split_URIRef(p)
                    sub_data[key] = str(o)
                    continue

                if p == rdflib.RDF.first:
                    # first means we have a collection
                    logger.debug(f'Need to find children of first: {o}')
                    # get list:
                    qs = """PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

SELECT ?item
WHERE {
  ?a rdf:rest*/rdf:first ?item .
}"""
                    list_res = graph.query(qs)

                    _ids = list(set([str(_id[0]) for _id in list_res]))
                    _data = [_query_by_id(graph, _id, add_type) for _id in _ids]
                    return _data

                if p == rdflib.RDF.type and add_type:
                    sub_data["@type"] = str(o)
                else:
                    logger.debug(f'dont know what to do with {p} and {o}')
        if predicate in sub_data:
            return sub_data[predicate]
        return sub_data

    if isinstance(obj, rdflib.URIRef):
        # could be a type definition or a web IRI
        if _is_type_definition(graph, obj):
            logger.debug('points to a type definition inside the data')
            if obj == _id:
                return str(obj)
            return _query_by_id(graph=graph, _id=obj, add_type=False)

    logger.debug(f'"{obj}" for predicate "{predicate}" is a simple data field.')
    return str(obj)


def get_query_string(cls, limit: int = None) -> str:
    """Return the query string for the class."""

    def _get_namespace(key):
        ns = URIRefManager[cls].get(key, f'local:{key}')
        if ':' in ns:
            return ns
        return f'{ns}:{key}'

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


def _query_by_id(graph, _id: Union[str, rdflib.URIRef], add_type: bool) -> Dict:
    """Query the graph by the id. Return the data as a dictionary."""
    _sub_query_string = """SELECT DISTINCT ?p ?o WHERE { <%s> ?p ?o }""" % _id
    _sub_res = graph.query(_sub_query_string)
    out = {'id': str(_id)}
    for binding in _sub_res.bindings:
        predicate = binding['p']
        obj = binding['o']

        if predicate == rdflib.RDF.type:
            if add_type:
                out['@type'] = str(obj)
            continue

        _, key = split_URIRef(predicate)
        if str(_id) == str(obj):
            # would lead to a circular reference. Example for it: "landingPage" and "_id" are the same.
            # in this case, we return the object as a string
            out[key] = str(obj)
        else:
            out[key] = process_object(_id, predicate, obj, graph, add_type)

    return out


def _is_type_definition(graph, iri: Union[str, rdflib.URIRef]):
    _sub_query_string = """PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
SELECT DISTINCT ?o WHERE { <%s> rdf:type ?o }""" % iri
    _sub_res = graph.query(_sub_query_string)
    return len(_sub_res) == 1


def exists_as_type(obj: str, graph) -> bool:
    """Check if the object exists as a type in the graph."""
    query = """SELECT ?x ?obj ?p ?o
WHERE {
  ?x <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> ?obj .
  ?x ?p ?o .
}"""
    out = graph.query(query)
    for _id, _type, _, _ in out:
        if obj.startswith('_:'):
            if str(_id) == str(obj[2:]):
                return True
        else:
            if str(_id) == str(obj):
                return True
    return False


def expand_sparql_res(bindings,
                      graph,
                      add_type: bool,
                      add_context: bool) -> Dict:
    """Expand the SPARQL results. Return a dictionary."""
    out = {}
    # n_ = len(bindings)
    for i, binding in enumerate(bindings):
        logger.debug(
            f'Expanding SPARQL results {i}/{len(bindings)}: {binding["?id"]}, {binding["p"]}, {binding["?o"]}.')
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

        obj = str(binding['?o'])

        logger.debug(f'Processing object "{obj}" for predicate "{predicate}".')
        data = process_object(_id, predicate, binding['?o'], graph, add_type)

        # well obj is just a data field, add it
        if predicate in out[_id]:
            if isinstance(out[_id][predicate], list):
                out[_id][predicate].append(data)
            else:
                out[_id][predicate] = [out[_id][predicate], data]
        else:
            out[_id][predicate] = data

    return out


def dquery(subject: str,
           source: Optional[Union[str, pathlib.Path]] = None,
           data: Optional[Union[str, Dict]] = None,
           context: Optional[Dict] = None) -> Union[List[Dict], None]:
    """Return a list of resutls. The entries are dictionaries.

    Example
    -------
    >>> # Query all agents from the source file
    >>> import ontolutils
    >>> ontolutils.dquery(subject='prov:Agent', source='agent1.jsonld')
    """
    g = rdflib.Graph()
    g.parse(source=source,
            data=data,
            format='json-ld',
            context=context)

    prefixes = "".join([f"PREFIX {k}: <{p}>\n" for k, p in context.items() if not k.startswith('@')])

    query_str = f"""
    SELECT *
    WHERE {{
        ?id a {subject}.
        ?id ?p ?o .
}}"""

    res = g.query(prefixes + query_str)

    if len(res) == 0:
        return None

    logger.debug(f'Querying subject="{subject}" with query: "{prefixes + query_str}" and got {len(res)} results')

    kwargs: Dict = expand_sparql_res(res.bindings, g, True, True)
    for _id in kwargs:
        kwargs[_id]['id'] = _id
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
        If limit equals to 1, the result will be a single obj, not a list.
    """
    query_string = get_query_string(cls)
    g = rdflib.Graph()

    ns_keys = [_ns[0] for _ns in g.namespaces()]

    prefixes = "".join([f"PREFIX {k}: <{p}>\n" for k, p in NamespaceManager[cls].items() if not k.startswith('@')])
    for k, p in NamespaceManager[cls].items():
        if k not in ns_keys:
            g.bind(k, p)
            # logger.debug(k)
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

    logger.debug(f'Querying class "{cls.__name__}" with query: {gquery}')
    # logger.debug(prefixes + query_string)
    res = g.query(gquery)

    logger.debug(f'Querying resulted in {len(res)} results')

    if len(res) == 0:
        return

    logger.debug(f'Expanding SPARQL results...')
    kwargs: Dict = expand_sparql_res(res.bindings, g, False, False)

    # in case that the model field names are different than the IRI names, we need to find the
    # corresponding names. The urirefs translate the class model fields to a <prefix>:<name> format.
    # As we have the latter, the inverse dictionary let's us find the model field names.
    from . import get_urirefs
    inverse_urirefs = {v.split(':', 1)[-1]: k for k, v in get_urirefs(cls).items()}

    if limit is not None:
        out = []
        for i, (k, v) in enumerate(kwargs.items()):
            model_field_dict = {inverse_urirefs[key]: value for key, value in v.items()}
            if limit == 1:
                return cls.model_validate({'id': k, **model_field_dict})
            out.append(cls.model_validate({'id': k, **model_field_dict}))
            if i == limit:
                return out
    return [cls.model_validate({'id': k, **{inverse_urirefs[key]: value for key, value in v.items()}}) for k, v in
            kwargs.items()]
