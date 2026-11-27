"""Resource limits must never truncate the RDF properties of a selected model."""
from typing import List, Optional

import pytest
from rdflib import BNode, Graph, Literal, Namespace, RDF, URIRef
from rdflib.compare import isomorphic

from ontolutils import Thing, namespaces, query, urirefs


EX = Namespace('https://example.org/loading/')


@namespaces(ex=str(EX))
@urirefs(Measurement='ex:Measurement', values='ex:value')
class Measurement(Thing):
    values: List[int]


@pytest.fixture
def graph():
    result = Graph()
    for subject, values in [(EX.first, [1, 2, 3]), (EX.second, [4, 5])]:
        result.add((subject, RDF.type, EX.Measurement))
        for value in values:
            result.add((subject, EX.value, Literal(value)))
    return result


@pytest.fixture(params=['graph', 'jsonld', 'turtle', 'file', 'query'])
def load(request, graph, tmp_path):
    if request.param == 'graph':
        return lambda limit: Measurement.from_graph(graph, limit=limit)
    if request.param == 'jsonld':
        return lambda limit: Measurement.from_jsonld(data=graph.serialize(format='json-ld'), limit=limit)
    turtle = graph.serialize(format='turtle')
    if request.param == 'turtle':
        return lambda limit: Measurement.from_ttl(data=turtle, limit=limit)
    if request.param == 'file':
        path = tmp_path / 'measurements.ttl'
        path.write_text(turtle, encoding='utf-8')
        return lambda limit: Measurement.from_file(path, format='turtle', limit=limit)
    return lambda limit: query(Measurement, data=turtle, format='turtle', limit=limit)


def test_resource_limits_preserve_complete_models(load, graph):
    for limit in [None, 2, 3]:
        models = load(limit)
        assert len(models) == 2
        assert {item.id: set(item.values) for item in models} == {
            str(EX.first): {1, 2, 3}, str(EX.second): {4, 5}}
    model = load(1)
    assert isinstance(model, Measurement)
    assert set(model.values) == {value.toPython() for value in graph.objects(URIRef(model.id), EX.value)}
    assert load(0) == []


@pytest.mark.parametrize('limit,error', [(-1, ValueError), (True, TypeError),
                                        (False, TypeError), (1.5, TypeError), ('1', TypeError)])
def test_invalid_limits_are_rejected(load, limit, error):
    with pytest.raises(error, match='limit'):
        load(limit)


def test_no_matches_for_every_limit():
    empty = Graph()
    for limit in [None, 0, 1, 2]:
        assert Measurement.from_graph(empty, limit=limit) == []
        assert Measurement.from_ttl(data='', limit=limit) == []


def test_graph_selection_and_namespace_bindings_are_preserved(graph):
    blank = BNode('measurement')
    graph.add((blank, RDF.type, EX.Measurement))
    graph.add((blank, EX.value, Literal(9)))
    before = Graph()
    before += graph
    namespaces_before = list(graph.namespaces())
    assert set(Measurement.from_graph(graph, subject=EX.second, limit=1).values) == {4, 5}
    assert Measurement.from_graph(graph, subject=blank, limit=1).id == '_:measurement'
    assert Measurement.from_graph(graph, subject='_:measurement', limit=1).values == [9]
    assert Measurement.from_graph(graph, subject=EX.absent, limit=1) == []
    assert isomorphic(graph, before)
    assert list(graph.namespaces()) == namespaces_before


@pytest.mark.parametrize('limit,error', [(-1, ValueError), (True, TypeError),
                                        (1.5, TypeError), ('1', TypeError)])
def test_query_generation_validates_row_limit(limit, error):
    with pytest.raises(error, match='limit'):
        Measurement.create_query(limit=limit)


def test_limits_are_checked_before_parsing_or_network_access():
    with pytest.raises(ValueError, match='limit'):
        Measurement.from_ttl(source='https://invalid.example/data.ttl', limit=-1)
    assert Measurement.from_jsonld(source='https://invalid.example/data.jsonld', limit=0) == []


def test_single_valued_rdf_predicates_fill_list_fields_in_nested_models():
    @namespaces(ex=str(EX))
    @urirefs(Container='ex:Container', measurements='ex:measurement')
    class Container(Thing):
        measurements: Optional[List[Measurement]] = None

    graph = Graph()
    graph.add((EX.container, RDF.type, EX.Container))
    graph.add((EX.container, EX.measurement, EX.single))
    graph.add((EX.single, RDF.type, EX.Measurement))
    graph.add((EX.single, EX.value, Literal(7)))
    restored = Container.from_graph(graph, limit=1)
    assert restored.measurements[0].values == [7]
    # RDF singleton accommodation must not relax ordinary Python input validation.
    with pytest.raises(ValueError):
        Measurement(values=7)
