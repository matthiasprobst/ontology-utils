"""Literal metadata must survive unconstrained model and dictionary projection."""
import json
from typing import Any, List, Union

import pytest
from pydantic import AnyUrl, ValidationError
from rdflib import BNode, Graph, Literal, URIRef, XSD
from rdflib.compare import isomorphic

from ontolutils import Thing, dquery, namespaces, urirefs
from ontolutils.ex.qudt import QuantityKind, Unit
from ontolutils.typing import AnyIri


@namespaces(ex='https://example.org/')
@urirefs(Sample='ex:Sample', value='ex:value')
class Sample(Thing):
    value: Any


@pytest.mark.parametrize('literal', [Literal('hello', lang='de'),
    Literal('typed string', datatype=XSD.string),
    Literal('https://example.org/text'), Literal('003.120', datatype=XSD.decimal, normalize=False),
    Literal('code', datatype='https://example.org/custom'), Literal(True)])
def test_literal_round_trip(literal):
    original = Sample(id='https://example.org/item', value=literal)
    payload = original.model_dump_jsonld()
    graph = Graph().parse(data=payload, format='json-ld')
    restored = Sample.from_jsonld(data=payload, limit=1)
    assert isinstance(restored.value, Literal)
    assert restored.value.datatype == literal.datatype
    assert restored.value.language == literal.language
    assert isomorphic(graph, Graph().parse(data=restored.model_dump_jsonld(), format='json-ld'))
    result = dquery('ex:Sample', data=payload, context={'ex': 'https://example.org/'})[0]
    assert isomorphic(graph, Graph().parse(data=json.dumps(result), format='json-ld'))


@namespaces(ex='https://example.org/')
@urirefs(Text='ex:Text', value='ex:value', values='ex:values')
class Text(Thing):
    value: str
    values: List[str]


@pytest.mark.parametrize('value', ['https://example.org/text', 'ex:sample',
                                  'urn:example:literal', '_:literal', 'hello@de'])
def test_plain_string_fields_preserve_literal_text(value):
    model = Text(id='https://example.org/item', value=value, values=[value, 'other'])
    graph = Graph().parse(data=model.model_dump_jsonld(), format='json-ld')
    assert (URIRef(model.id), URIRef(Text.iri('value')), Literal(value)) in graph
    assert (URIRef(model.id), URIRef(Text.iri('values')), Literal(value)) in graph
    restored = Text.from_graph(graph, limit=1)
    assert restored.value == value
    assert isomorphic(graph, Graph().parse(data=restored.serialize('ttl'), format='ttl'))


@namespaces(ex='https://example.org/')
@urirefs(Reference='ex:Reference', value='ex:value')
class Reference(Thing):
    value: AnyIri


@pytest.mark.parametrize('value', ['https://example.org/external', '_:external',
                                  BNode('external'), URIRef('urn:example:external'),
                                  AnyUrl('urn:example:external')])
def test_iri_fields_preserve_resource_terms_and_string_compatibility(value):
    model = Reference(id='https://example.org/item', value=value)
    expected = value.n3() if isinstance(value, BNode) else str(value)
    assert model.value == expected
    assert isinstance(model.value, str)
    assert model.model_dump()['value'] == expected
    assert json.loads(model.model_dump_json())['value'] == expected
    graph = Graph().parse(data=model.model_dump_jsonld(), format='json-ld')
    target = next(graph.objects(URIRef(model.id), URIRef(Reference.iri('value'))))
    assert isinstance(target, BNode if expected.startswith('_:') else URIRef)
    restored = Reference.from_graph(graph, limit=1)
    assert isomorphic(graph, Graph().parse(data=restored.model_dump_jsonld(), format='json-ld'))


def test_rdf_literal_cannot_become_an_iri_through_iri_validation():
    with pytest.raises(ValidationError, match='literal'):
        Reference(value=Literal('https://example.org/literal'))


@pytest.mark.parametrize('value', [URIRef('urn:example:external'), BNode('external')])
def test_unconstrained_resource_values_retain_rdf_term_kind(value):
    model = Sample(id='https://example.org/item', value=value)
    graph = Graph().parse(data=model.model_dump_jsonld(), format='json-ld')
    restored = Sample.from_graph(graph, limit=1)
    assert isinstance(restored.value, type(value))
    assert isomorphic(graph, Graph().parse(data=restored.model_dump_jsonld(), format='json-ld'))


@pytest.mark.parametrize('value,term_type', [('https://example.org/value', Literal),
                                          (URIRef('https://example.org/value'), URIRef)])
def test_mixed_text_and_iri_field_uses_explicit_term_kind(value, term_type):
    @namespaces(ex='https://example.org/')
    @urirefs(Mixed='ex:Mixed', value='ex:value')
    class Mixed(Thing):
        value: Union[str, AnyIri]

    model = Mixed(value=value)
    graph = Graph().parse(data=model.model_dump_jsonld(), format='json-ld')
    assert isinstance(next(graph.objects(None, URIRef(Mixed.iri('value')))), term_type)


@pytest.mark.parametrize('model_type,field', [(Unit, 'dbpediaMatch'),
                                           (Unit, 'informativeReference'),
                                           (QuantityKind, 'informativeReference')])
def test_qudt_uri_literals_retain_their_datatype_and_term_kind(model_type, field):
    literal = Literal('https://example.org/reference', datatype=XSD.anyURI)
    original = model_type(id='https://example.org/item', **{field: [literal, URIRef('https://example.org/other')]})
    graph = Graph().parse(data=original.model_dump_jsonld(), format='json-ld')
    predicate = URIRef(model_type.iri(field))
    assert set(graph.objects(URIRef(original.id), predicate)) == {literal, URIRef('https://example.org/other')}
    restored = model_type.from_graph(graph, limit=1)
    assert isomorphic(graph, Graph().parse(data=restored.model_dump_jsonld(), format='json-ld'))
    with pytest.raises(ValidationError, match='anyURI'):
        model_type(**{field: Literal('plain string')})
