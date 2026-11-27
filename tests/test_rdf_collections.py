"""Collections are local ordered sequences, not sets of graph-wide values."""
import pytest
from rdflib import BNode, Graph, Literal, Namespace, RDF
from rdflib.collection import Collection

from ontolutils.classes.query_util import process_object

EX = Namespace('https://example.org/')


@pytest.mark.parametrize('head', [BNode('head'), EX.head])
def test_collection_order_duplicates_literals_and_isolation(head, monkeypatch):
    graph = Graph()
    Collection(graph, head, [EX.b, Literal('word', lang='en'), EX.b, EX.a])
    Collection(graph, BNode(), [EX.unrelated])
    monkeypatch.setattr(graph, 'query', lambda *a, **k: pytest.fail('Unexpected SPARQL'))
    assert process_object(EX.owner, EX.items, head, graph, False) == [
        str(EX.b), 'word@en', str(EX.b), str(EX.a)]
    assert process_object(EX.owner, EX.items, RDF.nil, graph, False) == []


@pytest.mark.parametrize('fault', ['cycle', 'missing', 'multiple', 'literal_rest', 'nested_cycle'])
def test_malformed_collection_raises(fault):
    graph = Graph()
    head = BNode()
    graph.add((head, RDF.first, EX.a))
    if fault == 'cycle':
        graph.add((head, RDF.rest, head))
    elif fault == 'multiple':
        graph.add((head, RDF.first, EX.b))
        graph.add((head, RDF.rest, RDF.nil))
    elif fault == 'literal_rest':
        graph.add((head, RDF.rest, Literal('invalid')))
    elif fault == 'nested_cycle':
        graph.set((head, RDF.first, head))
        graph.add((head, RDF.rest, RDF.nil))
    with pytest.raises(ValueError, match='collection'):
        process_object(EX.owner, EX.items, head, graph, False)
