"""Model fields are selected by complete RDF predicates, never local names."""
from typing import Optional

from pydantic import Field
from rdflib import Graph, Literal, URIRef
from rdflib.compare import isomorphic

from ontolutils import Thing, namespaces, urirefs


@namespaces(a='https://example.org/a/', b='https://example.org/b/')
@urirefs(Measurement='a:Measurement', measured='a:value', reference='b:value')
class Measurement(Thing):
    measured: Optional[float] = Field(default=None, alias='measured_value')
    reference: Optional[float] = None


def test_same_local_name_maps_to_distinct_fields():
    source = Measurement(id='https://example.org/sample', measured_value=2, reference=3)
    payload = source.model_dump_jsonld()
    restored = Measurement.from_jsonld(data=payload, limit=1)
    assert restored.measured == 2
    assert restored.reference == 3
    assert isomorphic(Graph().parse(data=payload, format='json-ld'),
                      Graph().parse(data=restored.model_dump_jsonld(), format='json-ld'))


def test_foreign_predicate_cannot_populate_mapped_field():
    restored = Measurement.from_ttl(data='''
        <https://example.org/sample> a <https://example.org/a/Measurement> ;
            <https://unrelated.org/value> 99 .
    ''', limit=1)
    assert restored.measured is None
    assert restored.reference is None
    assert 'https://unrelated.org/value' not in restored.model_dump()


def test_load_context_does_not_modify_registered_namespaces():
    before = dict(Thing.get_context())
    Thing.from_jsonld(data=Thing(id='https://example.org/sample').model_dump_jsonld(),
                     context={'temporary': 'https://temporary.org/'})
    assert Thing.get_context() == before


def test_nested_predicates_keep_their_namespace():
    @namespaces(a='https://example.org/a/')
    @urirefs(Container='a:Container', measurement='a:measurement')
    class Container(Thing):
        measurement: Measurement

    original = Container(measurement=Measurement(id='https://example.org/measurement',
                                                 measured=2, reference=3))
    expected = Graph().parse(data=original.model_dump_jsonld(), format='json-ld')
    source = Graph() + expected
    source.add((URIRef(original.measurement.id), URIRef('https://unmapped.org/value'),
                Literal('unmapped')))
    restored = Container.from_jsonld(data=source.serialize(format='json-ld'), limit=1)
    assert restored.measurement.measured == 2
    assert restored.measurement.reference == 3
    assert isomorphic(expected, Graph().parse(data=restored.model_dump_jsonld(), format='json-ld'))
