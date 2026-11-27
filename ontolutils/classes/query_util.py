"""This module contains the query utility functions for the Thing class."""
import json
import logging
import pathlib
import re
from collections import deque
from collections.abc import Mapping
from itertools import islice
from typing import Union, Dict, List, Optional, Type

import rdflib

from .decorator import URIRefManager, _get_predicate_fields
from .thing import Thing, _literal_to_jsonld, _is_reference_field, _has_list_annotation
from .utils import split_uri, _validate_limit

logger = logging.getLogger('ontolutils')


def _add_rdf_type(resource, rdf_type):
    """Retain all distinct RDF types without changing the single-type shape."""
    value = rdf_type.n3() if isinstance(rdf_type, rdflib.BNode) else str(rdf_type)
    previous = resource.get('@type')
    if previous is None:
        resource['@type'] = value
    elif isinstance(previous, list):
        if value not in previous:
            previous.append(value)
    elif previous != value:
        resource['@type'] = [previous, value]


def _collection_values(head, graph, add_type, ancestors=frozenset(), resources=frozenset(), preserve_predicates=False, literal_mode="legacy"):
    """Read one finite RDF collection, preserving order and multiplicity.

    Reject ambiguous or cyclic list structure instead of choosing an arbitrary
    rdf:first/rdf:rest value. This is a model-loading constraint, not a claim
    that such graphs are invalid RDF.
    """
    if head in ancestors:
        raise ValueError('Cyclic nested RDF collection')
    ancestors = ancestors | {head}
    values = []
    seen = set()
    node = head
    while node != rdflib.RDF.nil:
        if node in seen:
            raise ValueError('Cyclic RDF collection')
        seen.add(node)
        first = list(graph.objects(node, rdflib.RDF.first))
        rest = list(graph.objects(node, rdflib.RDF.rest))
        if len(first) != 1 or len(rest) != 1:
            raise ValueError('RDF collection requires exactly one rdf:first and rdf:rest per cell')
        if not isinstance(rest[0], (rdflib.URIRef, rdflib.BNode)):
            raise ValueError('RDF collection rdf:rest must identify a resource')
        values.append(process_object(head, rdflib.RDF.first, first[0], graph, add_type,
                                     _collection_ancestors=ancestors, _resource_ancestors=resources,
                                     _preserve_predicates=preserve_predicates, _literal_mode=literal_mode))
        node = rest[0]
    return values


def process_object(
        _id,
        predicate,
        obj: Union[rdflib.URIRef, rdflib.BNode, rdflib.Literal],
        graph,
        add_type,
        _collection_ancestors=frozenset(),
        _resource_ancestors=frozenset(), _preserve_predicates=False, _literal_mode="legacy"):
    """Process the object of a triple."""
    if _literal_mode == 'jsonld' and isinstance(obj, (rdflib.URIRef, rdflib.BNode)):
        identifier = obj.n3() if isinstance(obj, rdflib.BNode) else str(obj)
        if obj in _resource_ancestors or next(graph.predicate_objects(obj), None) is None:
            return {'@id': identifier}
        # Preserve RDF list cells as ordinary nodes, including named/shared
        # heads and annotations. Replacing them with @list can lose identity.
        return _query_by_id(graph, obj, add_type,
                            _resource_ancestors=_resource_ancestors,
                            _collection_ancestors=_collection_ancestors,
                            _preserve_predicates=_preserve_predicates, _literal_mode='jsonld')
    if obj == rdflib.RDF.nil:
        return []
    if isinstance(obj, (rdflib.URIRef, rdflib.BNode)) and (
            (obj, rdflib.RDF.first, None) in graph or
            (obj, rdflib.RDF.rest, None) in graph):
        return _collection_values(obj, graph, add_type, _collection_ancestors, _resource_ancestors, _preserve_predicates, _literal_mode)
    if isinstance(obj, rdflib.Literal):
        logger.debug(f'Object "{obj}" for predicate "{predicate}" is a literal.')
        if _literal_mode == 'model':
            return obj
        if _literal_mode == 'jsonld':
            if obj.language or obj.datatype is not None:
                return _literal_to_jsonld(obj)
            return str(obj)
        if obj.language:
            return f"{obj}@{obj.language}"
        return str(obj)

    if isinstance(obj, (rdflib.BNode, rdflib.URIRef)):
        identifier = obj.n3() if isinstance(obj, rdflib.BNode) else str(obj)
        if obj in _resource_ancestors:
            return obj if _literal_mode == 'model' else identifier
        if _literal_mode == 'model' and next(graph.predicate_objects(obj), None) is None:
            return obj
        if isinstance(obj, rdflib.BNode) or _is_type_definition(graph, obj):
            return _query_by_id(graph, obj, add_type,
                                _resource_ancestors=_resource_ancestors,
                                _collection_ancestors=_collection_ancestors,
                                _preserve_predicates=_preserve_predicates, _literal_mode=_literal_mode)
        return obj if _literal_mode == 'model' else identifier
    return str(obj)


def get_query_string(cls) -> str:
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
    ?id ?p ?o .
}}"""
    return query_str


def _query_by_id(graph, _id: Union[str, rdflib.URIRef], add_type: bool,
                 _resource_ancestors=frozenset(), _collection_ancestors=frozenset(),
                 _preserve_predicates=False, _literal_mode="legacy") -> Dict:
    """Expand indexed resource properties; cycle edges remain identifier references."""
    subject = _id if isinstance(_id, (rdflib.URIRef, rdflib.BNode)) else rdflib.URIRef(_id)
    identifier = subject.n3() if isinstance(subject, rdflib.BNode) else str(subject)
    ancestors = _resource_ancestors | {subject}
    out = {'@id': identifier}
    for predicate, obj in graph.predicate_objects(subject):
        if predicate == rdflib.RDF.type:
            if add_type:
                _add_rdf_type(out, obj)
            continue
        key = str(predicate) if _preserve_predicates else split_uri(predicate)[1]
        value = process_object(subject, predicate, obj, graph, add_type,
                               _resource_ancestors=ancestors,
                               _collection_ancestors=_collection_ancestors,
                               _preserve_predicates=_preserve_predicates, _literal_mode=_literal_mode)
        if key in out:
            if isinstance(out[key], list):
                out[key].append(value)
            else:
                out[key] = [out[key], value]
        else:
            out[key] = value
    return out


def _is_type_definition(graph, iri: Union[str, rdflib.URIRef]):
    """Check whether a resource has a type using the subject/predicate index."""
    return next(graph.objects(rdflib.URIRef(iri), rdflib.RDF.type), None) is not None


def expand_sparql_res(bindings,
                      graph,
                      add_type: bool,
                      add_context: bool,
                      predicate_fields=None) -> Dict:
    """Expand the SPARQL results. Return a dictionary."""
    out = {}
    # n_ = len(bindings)
    for i, binding in enumerate(bindings):
        logger.debug(
            f'Expanding SPARQL results {i + 1}/{len(bindings)}: {binding["?id"]}, {binding["p"]}, {binding["?o"]}.')

        if isinstance(binding['?id'], rdflib.URIRef):
            _id = str(binding['?id'])
        else:
            _id = binding['?id'].n3()
        if _id not in out:
            out[_id] = {}
            if add_context:
                out[_id] = {'@context': {}}
        p = str(binding['p'])
        if predicate_fields is None:
            _, predicate = split_uri(p)
        else:
            if p not in predicate_fields and binding['p'] != rdflib.RDF.type:
                continue
            predicate = predicate_fields.get(p, p)

        if binding['p'] == rdflib.RDF.type:
            if add_type:
                _add_rdf_type(out[_id], binding['o'])
            continue
        if add_context:
            out[_id]['@context'][predicate] = str(p)

        obj = str(binding['?o'])

        logger.debug(f'Processing object "{obj}" for predicate "{predicate}".')
        data = process_object(_id, predicate, binding['?o'], graph, add_type,
                              _preserve_predicates=predicate_fields is not None,
                              _literal_mode=("jsonld" if add_context else "model") if predicate_fields is not None else "legacy")

        # well obj is just a data field, add it
        if predicate in out[_id]:
            if isinstance(out[_id][predicate], list):
                out[_id][predicate].append(data)
            else:
                out[_id][predicate] = [out[_id][predicate], data]
        else:
            out[_id][predicate] = data

    return out


def _dictionary_resource(graph, subject, predicate_fields):
    """Describe each reachable resource once with bounded JSON nesting.

    Deeper descriptions use JSON-LD @included, retaining edges and identifiers
    without relying on Python recursion or duplicating shared subgraphs.
    """
    def identifier(node):
        return node.n3() if isinstance(node, rdflib.BNode) else str(node)

    root = {'@id': identifier(subject)}
    pending = deque([(subject, root, 0)])
    discovered = {subject}
    included = []
    while pending:
        node, description, depth = pending.popleft()
        for predicate, obj in graph.predicate_objects(node):
            if predicate == rdflib.RDF.type:
                _add_rdf_type(description, obj)
                continue
            key = predicate_fields[str(predicate)]
            if isinstance(obj, rdflib.Literal):
                value = (_literal_to_jsonld(obj) if obj.language or obj.datatype is not None
                         else str(obj))
            else:
                value = {'@id': identifier(obj)}
                if obj not in discovered and next(graph.predicate_objects(obj), None) is not None:
                    discovered.add(obj)
                    if depth < 32:
                        pending.append((obj, value, depth + 1))
                    else:
                        extra = {'@id': identifier(obj)}
                        included.append(extra)
                        pending.append((obj, extra, depth))
            if key not in description:
                description[key] = value
            elif isinstance(description[key], list):
                description[key].append(value)
            else:
                description[key] = [description[key], value]
    if included:
        root['@included'] = included
    root['@context'] = {key: iri for iri, key in predicate_fields.items()}
    return root


def dquery(subject: str,
           source: Optional[Union[str, pathlib.Path]] = None,
           data: Optional[Union[str, Dict]] = None,
           context: Optional[Dict] = None) -> List[Dict]:
    """Return JSON-LD resources as dictionaries for a compact class IRI.

    ``subject`` names an RDF class, such as ``"prov:Person"``; it is not
    an individual resource ID. Supply JSON-LD through source or data, and
    a context dictionary defining the prefixes in subject. The return
    value is a list of dictionaries, or ``[]`` if no matches are found.
    """
    g = rdflib.Graph()
    if isinstance(data, dict):
        data = json.dumps(data)
    g.parse(source=source,
            data=data,
            format='json-ld',
            context=context)
    if context is None:
        context = {}
    prefixes = "".join([f"PREFIX {k}: <{p}>\n" for k, p in context.items() if not k.startswith('@')])

    assert isinstance(subject, str), f"Subject must be a string, not {type(subject)}"

    query_str = f"""
    SELECT DISTINCT ?id
    WHERE {{
        ?id a {subject}.
}}"""

    res = g.query(prefixes + query_str)

    if len(res) == 0:
        return []

    logger.debug(f'Querying subject="{subject}" with query: "{prefixes + query_str}" and got {len(res)} results')

    # Keep readable local keys when unambiguous. A collision requires full IRI
    # keys so values from different vocabularies cannot be merged or relabelled.
    by_local = {}
    for predicate in set(g.predicates()):
        if predicate == rdflib.RDF.type:
            continue
        try:
            local = split_uri(predicate)[1]
        except ValueError:
            local = str(predicate)
        by_local.setdefault(local, set()).add(str(predicate))
    dictionary_fields = {iri: (local if len(iris) == 1 else iri)
                         for local, iris in by_local.items() for iri in iris}
    return [_dictionary_resource(g, row['id'], dictionary_fields) for row in res.bindings]


def query(cls: Type[Thing],
          source: Optional[Union[str, pathlib.Path]] = None,
          data: Optional[Union[str, Dict]] = None,
          format: Optional[str] = None,
          context: Optional[Union[Dict, str]] = None,
          limit: Optional[int] = None) -> Union[Thing, List]:
    """Load matching instances of a model class from RDF.

    ``cls`` is a ``Thing`` subclass, not a graph or SPARQL query string.
    Supply a file/URL through ``source`` or inline RDF through ``data``;
    ``format`` selects the RDFLib parser. ``context`` is a legacy namespace
    dictionary retained for compatibility; model mappings remain authoritative.
    JSON-LD uses the input document's own context through RDFLib.

    Returns a list, except that ``limit=1`` returns a single matching model.
    No matches and ``limit=0`` return ``[]``. Limits must be nonnegative integers;
    booleans are not accepted. This function does not return
    a generator. Use ``rdflib.Graph.query`` for arbitrary SPARQL.
    """
    _validate_limit(limit)
    if context is not None and not isinstance(context, dict):
        raise TypeError(f"Context must be a dict, not {type(context)}")
    if limit == 0:
        return []
    if isinstance(data, dict):
        data = json.dumps(data)
    graph = rdflib.Graph().parse(source=source, data=data, format=format)
    return _query_graph(cls, graph, limit=limit)


def _query_graph(cls, graph, limit=None, subject=None):
    """Project complete resources using RDFLib indexes, without a row limit."""
    _validate_limit(limit)
    if limit == 0:
        return []
    rdf_type = None if cls is Thing else rdflib.URIRef(cls.iri())
    if subject is not None:
        if not isinstance(subject, (str, rdflib.URIRef, rdflib.BNode)):
            raise TypeError('subject must be a resource IRI or blank node')
        if not isinstance(subject, (rdflib.URIRef, rdflib.BNode)):
            subject = rdflib.BNode(subject[2:]) if subject.startswith('_:') else rdflib.URIRef(subject)
        subjects = [subject] if any(graph.triples((subject, rdflib.RDF.type, rdf_type))) else []
    else:
        subjects = graph.subjects(rdflib.RDF.type, rdf_type, unique=True)
    predicate_fields = _get_predicate_fields(cls)
    reference_predicates = {
        predicate for predicate, name in predicate_fields.items()
        if _is_reference_field(cls.model_fields.get(name))
        and not _has_list_annotation(cls.model_fields[name].annotation)}
    models = []
    for resource in islice(subjects, limit):
        identifier = resource.n3() if isinstance(resource, rdflib.BNode) else str(resource)
        fields = {'id': identifier}
        for predicate, obj in graph.predicate_objects(resource):
            field = str(predicate)
            if field not in predicate_fields:
                continue
            if field in reference_predicates and isinstance(obj, (rdflib.URIRef, rdflib.BNode)):
                value = obj
            else:
                value = process_object(resource, predicate, obj, graph, False,
                                       _resource_ancestors=frozenset({resource}),
                                       _preserve_predicates=True, _literal_mode='model')
            if field in fields:
                if not isinstance(fields[field], list):
                    fields[field] = [fields[field]]
                fields[field].append(value)
            else:
                fields[field] = value
        models.append(cls.model_validate(_at_id_to_id(fields)))
    return models[0] if limit == 1 and models else models


_SCHEME_RE = re.compile(r'^[A-Za-z][A-Za-z0-9+.-]*:')


def _expand_compact_iris(obj, context, *, transform_keys=False):
    """
    Recursively expand 'prefix:suffix' strings using a JSON-LD-like context.

    - obj: any nested structure (dict/list/tuple/set/str/…).
    - context: mapping like {'pivmeta': 'https://…#', ...}.
      If a context value is a dict (e.g. {'@id': '…'}), '@id' is used.
    - transform_keys: if True, also expand dictionary KEYS that are 'prefix:suffix'.

    Returns a new structure with expansions applied.
    """
    # Normalize context to {prefix: base_iri_string}
    prefixes = {}
    for k, v in context.items():
        if k.startswith('@'):
            continue
        if isinstance(v, str):
            prefixes[k] = v
        elif isinstance(v, Mapping):
            iri = v.get('@id')
            if isinstance(iri, str):
                prefixes[k] = iri

    def expand_str(s: str) -> str:
        # Only consider exact 'prefix:suffix' forms where prefix is in context.
        if ':' in s and not s.startswith(('http://', 'https://', 'urn:', 'mailto:')):
            pref, rest = s.split(':', 1)
            base = prefixes.get(pref)
            if base:
                # Ensure we don't accidentally drop/add separators incorrectly
                needs_sep = not (base.endswith(('/', '#')) or rest.startswith(('/', '#')))
                sep = '#' if needs_sep else ''
                return f"{base}{sep}{rest}"
        return s

    def expand_any(x):
        if isinstance(x, str):
            return expand_str(x)
        if isinstance(x, Mapping):
            return {expand_str(k) if transform_keys and isinstance(k, str) else k: expand_any(v)
                    for k, v in x.items()}
        if isinstance(x, tuple):
            return tuple(expand_any(i) for i in x)
        if isinstance(x, set):
            return {expand_any(i) for i in x}
        if isinstance(x, list):
            return [expand_any(i) for i in x]
        return x

    return expand_any(obj)


def _at_id_to_id(data: Dict) -> Dict:
    """Convert recursively '@id' keys to 'id' keys in a dictionary."""
    if isinstance(data, dict):
        new_data = {}
        for k, v in data.items():
            if k == '@id':
                new_data['id'] = v
            else:
                new_data[k] = _at_id_to_id(v)
        return new_data
    if isinstance(data, list):
        return [_at_id_to_id(item) for item in data]
    return data
