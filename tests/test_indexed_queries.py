"""Resource lookup must use RDF terms and preserve repeated values."""
from rdflib import Graph, Literal, Namespace, RDF

from ontolutils.classes.query_util import _is_type_definition, _query_by_id


def test_resource_lookup_uses_graph_index(monkeypatch):
    ex = Namespace('https://example.org/')
    graph = Graph()
    graph.add((ex.subject, RDF.type, ex.Type))
    graph.add((ex.subject, ex.label, Literal('one', lang='en')))
    graph.add((ex.subject, ex.label, Literal('two', lang='en')))

    def unexpected_query(*args, **kwargs):
        raise AssertionError('Resource lookup must not compile a SPARQL query')

    monkeypatch.setattr(graph, 'query', unexpected_query)
    assert _is_type_definition(graph, ex.subject)
    result = _query_by_id(graph, ex.subject, True)
    assert result['@id'] == str(ex.subject)
    assert result['@type'] == str(ex.Type)
    assert set(result['label']) == {'one@en', 'two@en'}
    assert not _is_type_definition(graph, ex.absent)
    graph.add((ex.subject, RDF.type, ex.OtherType))
    assert _is_type_definition(graph, ex.subject)
