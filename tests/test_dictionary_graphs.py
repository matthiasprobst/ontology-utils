"""Dictionary JSON-LD must preserve references and explicit RDF list structure."""
import json

import pytest
from rdflib import BNode, Graph, Literal, Namespace, RDF
from rdflib.collection import Collection
from rdflib.compare import isomorphic

from ontolutils import dquery

EX = Namespace('https://example.org/')


@pytest.mark.parametrize('head', [BNode('list'), EX.list])
def test_shared_annotated_collection_and_external_references(head):
    graph = Graph()
    graph.add((EX.root, RDF.type, EX.Root))
    graph.add((EX.root, EX.firstList, head))
    graph.add((EX.root, EX.secondList, head))
    graph.add((EX.root, EX.emptyList, RDF.nil))
    graph.add((EX.root, EX.external, EX.externalResource))
    Collection(graph, head, [EX.b, Literal('word', lang='de'), EX.b, EX.a])
    graph.add((head, EX.annotation, Literal('shared head')))
    payload = graph.serialize(format='json-ld')
    result = dquery('<https://example.org/Root>', data=payload)[0]
    assert result['external'] == {'@id': str(EX.externalResource)}
    assert result['firstList']['@id'] == result['secondList']['@id']
    assert isomorphic(graph, Graph().parse(data=json.dumps(result), format='json-ld'))


def test_untyped_described_resource_and_cycle():
    graph = Graph()
    graph.add((EX.root, RDF.type, EX.Root))
    graph.add((EX.root, EX.child, EX.child1))
    graph.add((EX.child1, EX.description, Literal('untyped child')))
    graph.add((EX.child1, EX.parent, EX.root))
    result = dquery('<https://example.org/Root>', data=graph.serialize(format='json-ld'))[0]
    assert result['child']['description'] == 'untyped child'
    assert isomorphic(graph, Graph().parse(data=json.dumps(result), format='json-ld'))


def test_deep_chain_uses_included_without_recursion():
    graph = Graph()
    graph.add((EX.root, RDF.type, EX.Root))
    previous = EX.root
    for index in range(1500):
        node = EX[f'node{index}']
        graph.add((previous, EX.next, node))
        previous = node
    result = dquery('<https://example.org/Root>', data=graph.serialize(format='json-ld'))[0]
    assert '@included' in result
    assert isomorphic(graph, Graph().parse(data=json.dumps(result), format='json-ld'))


def test_shared_subgraphs_are_described_once():
    graph = Graph()
    graph.add((EX.root, RDF.type, EX.Root))
    previous = EX.root
    for index in range(15):
        node = EX[f'shared{index}']
        graph.add((previous, EX.left, node))
        graph.add((previous, EX.right, node))
        previous = node
    result = dquery('<https://example.org/Root>', data=graph.serialize(format='json-ld'))[0]
    encoded = json.dumps(result)
    assert len(encoded) < 10000  # A linear-size description, not 2**15 copies.
    assert isomorphic(graph, Graph().parse(data=encoded, format='json-ld'))


def test_dictionary_input_and_non_qname_predicate():
    data = {'@id': str(EX.root), '@type': str(EX.Root),
            'https://example.org/123': {'@value': 'value'}}
    result = dquery('<https://example.org/Root>', data=data)[0]
    assert isomorphic(Graph().parse(data=json.dumps(data), format='json-ld'),
                      Graph().parse(data=json.dumps(result), format='json-ld'))
