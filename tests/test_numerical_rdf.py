"""Numerical RDF export describes one resource and an unordered value set."""
import json
import math

import numpy as np
import pytest
from pydantic import ValidationError
from rdflib import Graph, Literal, Namespace, RDF, URIRef, XSD
from rdflib.compare import isomorphic

from ontolutils import Thing, serialize
from ontology_fixtures.m4i import NumericalVariable


M4I = Namespace('http://w3id.org/nfdi4ing/metadata4ing#')
SUBJECT = URIRef('https://example.org/variable')


@pytest.mark.parametrize('values', [[3, 1, 3], np.array([3, 1, 3]),
                                   np.array([3, 1, 3], dtype=np.float32), [], np.array([]), 3, None])
def test_formats_preserve_the_same_resource_and_value_set(values):
    variable = NumericalVariable(id=str(SUBJECT), hasNumericalValue=values, hasUnit='m')
    expected = Graph().parse(data=variable.model_dump_jsonld(), format='json-ld')
    for format in ['ttl', 'json-ld', 'xml', 'n3', 'nt']:
        actual = Graph().parse(data=variable.serialize(format), format=format)
        assert isomorphic(actual, expected)
        assert set(actual.subjects(RDF.type, M4I.NumericalVariable)) == {SUBJECT}
    assert isomorphic(Graph().parse(data=json.dumps(variable.get_jsonld_dict()), format='json-ld'), expected)
    assert isomorphic(Graph().parse(data=serialize([variable], 'ttl'), format='ttl'), expected)


def test_rdf_values_do_not_claim_sequence_or_duplicate_preservation():
    variable = NumericalVariable(id=str(SUBJECT), hasNumericalValue=[3, 1, 3])
    graph = Graph().parse(data=variable.serialize('ttl'), format='ttl')
    assert set(graph.objects(SUBJECT, M4I.hasNumericalValue)) == {Literal(3), Literal(1)}
    assert len(list(graph.objects(SUBJECT, M4I.hasNumericalValue))) == 2
    restored = NumericalVariable.from_graph(graph, limit=1)
    assert set(restored.hasNumericalValue) == {1, 3}


def test_nested_variable_and_top_level_variable_describe_the_same_resource():
    variable = NumericalVariable(id=str(SUBJECT), hasNumericalValue=np.array([1, 2]))
    container = Thing(id='https://example.org/container', about=variable)
    graph = Graph().parse(data=container.serialize('ttl'), format='ttl')
    assert set(graph.subjects(RDF.type, M4I.NumericalVariable)) == {SUBJECT}
    assert set(graph.objects(SUBJECT, M4I.hasNumericalValue)) == {Literal(1), Literal(2)}


@pytest.mark.parametrize('values', [np.array(['1', '2']), np.array([True]),
                                   np.array([1 + 2j]), np.array([object()], dtype=object),
                                   np.array(['2026-01-01'], dtype='datetime64[D]'),
                                   np.array([[1, 2]])])
def test_non_real_or_multidimensional_arrays_are_rejected(values):
    with pytest.raises(ValidationError, match='hasNumericalValue'):
        NumericalVariable(hasNumericalValue=values)


def test_zero_dimensional_real_array_is_a_scalar():
    variable = NumericalVariable(id=str(SUBJECT), hasNumericalValue=np.array(3.5))
    assert variable.hasNumericalValue == 3.5
    assert variable.ndim == 0
    assert variable.size == 1
    graph = Graph().parse(data=variable.serialize('ttl'), format='ttl')
    assert list(graph.objects(SUBJECT, M4I.hasNumericalValue)) == [Literal(3.5)]


def reject_non_json_number(token):
    raise ValueError(f'Non-JSON numerical token: {token}')


@pytest.mark.parametrize('values', [float('nan'), float('inf'), -float('inf'),
                                   np.array([float('nan'), float('inf'), -float('inf')])])
def test_nonfinite_values_use_typed_literals_in_valid_jsonld(values):
    variable = NumericalVariable(id=str(SUBJECT), hasNumericalValue=values)
    payload = variable.model_dump_jsonld()
    json.loads(payload, parse_constant=reject_non_json_number)
    expected = {'NaN', 'INF', '-INF'} if isinstance(values, np.ndarray) else {
        'NaN' if math.isnan(values) else 'INF' if values > 0 else '-INF'}
    value_objects = variable.get_jsonld_dict()['m4i:hasNumericalValue']
    objects = value_objects if isinstance(value_objects, list) else [value_objects]
    assert {item['@value'] for item in objects} == expected
    assert all(item['@type'] == str(XSD.double) for item in objects)
    graph = Graph().parse(data=payload, format='json-ld')
    assert all(item.datatype == XSD.double for item in graph.objects(SUBJECT, M4I.hasNumericalValue))
    for format in ['ttl', 'json-ld', 'xml']:
        exported = variable.serialize(format)
        if format == 'json-ld':
            json.loads(exported, parse_constant=reject_non_json_number)
        restored = NumericalVariable.from_graph(Graph().parse(data=exported, format=format), limit=1)
        data = restored.to_numpy().reshape(-1)
        assert {('NaN' if math.isnan(item) else 'INF' if item > 0 else '-INF') for item in data} == expected
