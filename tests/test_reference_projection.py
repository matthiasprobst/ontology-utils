"""Reference-only fields must not become embedded models because RDF has more data."""
from typing import List

import pytest
from pydantic import HttpUrl
from rdflib import BNode, Graph, Literal, Namespace, RDF, URIRef

from ontolutils import Thing, namespaces, urirefs
from ontolutils.typing import AnyIri


EX = Namespace('https://example.org/')


@namespaces(ex=str(EX))
@urirefs(References='ex:References', target='ex:target', targets='ex:targets')
class References(Thing):
    target: AnyIri
    targets: List[AnyIri]


def reference_graph(target):
    graph = Graph()
    graph.add((EX.references, RDF.type, EX.References))
    graph.add((EX.references, EX.target, target))
    graph.add((EX.references, EX.targets, target))
    graph.add((target, RDF.type, EX.Described))
    graph.add((target, EX.note, Literal('Source graph has additional metadata')))
    return graph


@pytest.mark.parametrize('target', [EX.described, BNode('described')])
def test_described_resources_remain_references_in_iri_only_fields(target):
    graph = reference_graph(target)
    original_size = len(graph)
    restored = References.from_graph(graph, limit=1)
    expected = target.n3() if isinstance(target, BNode) else str(target)
    assert restored.target == expected
    assert restored.targets == [expected]
    exported = Graph().parse(data=restored.serialize('ttl'), format='ttl')
    actual_target = next(exported.objects(EX.references, EX.target))
    assert isinstance(actual_target, type(target))
    assert (actual_target, RDF.type, EX.Described) not in exported
    assert len(graph) == original_size


def test_reference_field_does_not_expand_an_ambiguous_collection():
    graph = reference_graph(EX.described)
    graph.remove((EX.references, EX.targets, EX.described))
    graph.add((EX.references, EX.targets, EX.other))
    graph.add((EX.described, RDF.first, Literal(1)))
    graph.add((EX.described, RDF.first, Literal(2)))
    graph.add((EX.described, RDF.rest, RDF.nil))
    assert References.from_graph(graph, limit=1).target == str(EX.described)


def test_declared_collection_of_iris_still_loads_rdf_list_members():
    from rdflib.collection import Collection

    graph = reference_graph(EX.described)
    graph.remove((EX.references, EX.targets, EX.described))
    head = BNode()
    Collection(graph, head, [EX.described, EX.other, EX.described])
    graph.add((EX.references, EX.targets, head))
    assert References.from_graph(graph, limit=1).targets == [str(EX.described), str(EX.other), str(EX.described)]


def test_url_field_can_reference_a_described_resource():
    @namespaces(ex=str(EX))
    @urirefs(WebReference='ex:WebReference', target='ex:target')
    class WebReference(Thing):
        target: HttpUrl

    graph = reference_graph(EX.described)
    graph.add((EX.web, RDF.type, EX.WebReference))
    graph.add((EX.web, EX.target, EX.described))
    assert str(WebReference.from_graph(graph, limit=1).target) == str(EX.described)


def test_reference_only_fields_work_in_nested_models():
    @namespaces(ex=str(EX))
    @urirefs(Container='ex:Container', references='ex:references')
    class Container(Thing):
        references: References

    graph = reference_graph(EX.described)
    graph.add((EX.container, RDF.type, EX.Container))
    graph.add((EX.container, EX.references, EX.references))
    result = Container.from_graph(graph, limit=1)
    assert isinstance(result.references, References)
    assert result.references.target == str(EX.described)
    assert result.references.targets == [str(EX.described)]
