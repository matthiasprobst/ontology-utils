"""Graph references retain identity when projected to finite model input."""
import pytest
from rdflib import BNode, Graph, Literal, Namespace, RDF

from ontolutils.classes.query_util import _query_by_id

EX = Namespace('https://example.org/')


@pytest.mark.parametrize('nodes', [(EX.a, EX.b), (BNode('a'), BNode('b'))])
def test_cycle_terminates_with_reference(nodes):
    a, b = nodes
    graph = Graph()
    for node in nodes:
        graph.add((node, RDF.type, EX.Node))
    graph.add((a, EX.next, b))
    graph.add((b, EX.next, a))
    result = _query_by_id(graph, a, True)
    identifier = lambda node: node.n3() if isinstance(node, BNode) else str(node)
    assert result['@id'] == identifier(a)
    assert result['next']['@id'] == identifier(b)
    assert result['next']['next'] == identifier(a)


def test_shared_blank_node_and_non_http_reference():
    graph = Graph()
    shared = BNode('shared')
    graph.add((EX.a, EX.left, shared))
    graph.add((EX.a, EX.right, shared))
    graph.add((shared, EX.label, Literal('shared')))
    graph.add((shared, EX.link, Namespace('urn:example:').target))
    result = _query_by_id(graph, EX.a, False)
    assert result['left'] == result['right']
    assert result['left']['@id'] == '_:shared'
    assert result['left']['link'] == 'urn:example:target'


def test_collection_cycle_through_resource_raises():
    graph = Graph()
    head = BNode('list')
    graph.add((head, RDF.first, EX.member))
    graph.add((head, RDF.rest, RDF.nil))
    graph.add((EX.member, RDF.type, EX.Node))
    graph.add((EX.member, EX.items, head))
    graph.add((EX.a, EX.items, head))
    with pytest.raises(ValueError, match='Cyclic nested RDF collection'):
        _query_by_id(graph, EX.a, False)
