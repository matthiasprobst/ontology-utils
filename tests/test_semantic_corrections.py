"""Regression contracts for mailbox resources and unit identity."""
import pathlib

import pytest
from rdflib import Graph, Namespace, URIRef

from ontology_fixtures import foaf, prov
from ontology_fixtures.qudt import Unit

FOAF = Namespace('http://xmlns.com/foaf/0.1/')


@pytest.fixture(name='convert')
def conversion_function():
    """Keep mailbox checks usable without the optional Pint dependency."""
    pytest.importorskip('pint')
    from ontolutils.units import convert_value_qudt
    return convert_value_qudt


@pytest.mark.parametrize('model,alias', [(foaf.Person, 'email'),
                                       (prov.Person, 'personal mailbox')])
@pytest.mark.parametrize('address', ['ada@example.org', 'mailto:ada@example.org',
                                   URIRef('mailto:ada@example.org')])
def test_mailbox_resource_round_trip(model, alias, address):
    person = model(id='https://example.org/ada', **{alias: address})
    assert person.mbox == 'ada@example.org'
    assert person.model_dump()['mbox'] == 'ada@example.org'
    for format in ('ttl', 'json-ld'):
        graph = Graph().parse(data=person.serialize(format), format=format)
        assert list(graph.objects(None, FOAF.mbox)) == [URIRef('mailto:ada@example.org')]
        restored = model.from_graph(graph, limit=1)
        assert restored.mbox == person.mbox
    person.mbox = 'mailto:other@example.org'
    assert person.mbox == 'other@example.org'


def test_unit_identity_ignores_descriptive_labels(convert):
    metre = Unit(id='http://qudt.org/vocab/unit/M', label='metre')
    centimetre = Unit(id='http://qudt.org/vocab/unit/CentiM',
                      scalingOf=metre, conversionMultiplier=0.01)
    target = Unit(id=metre.id)
    assert convert(150, centimetre, target) == 1.5
    assert convert(1.5, target, centimetre) == 150


def test_partial_qudt_root_uses_coefficients_from_matching_description(convert):
    gram = Unit(id='http://qudt.org/vocab/unit/GM', conversionMultiplier=1e-3)
    milligram = Unit(id='http://qudt.org/vocab/unit/MilliGM', scalingOf=gram,
                     conversionMultiplier=1e-6)
    partial_gram = Unit(id=gram.id)
    assert convert(1000, milligram, partial_gram) == pytest.approx(1)
    assert convert(1, partial_gram, milligram) == pytest.approx(1000)


@pytest.mark.parametrize('reverse', [False, True])
def test_conflicting_scaling_targets_are_rejected(reverse, convert):
    metre = Unit(id='http://qudt.org/vocab/unit/M')
    second = Unit(id='http://qudt.org/vocab/unit/SEC')
    parents = [metre, second]
    if reverse:
        parents.reverse()
    ambiguous = Unit(id='https://example.org/ambiguous', scalingOf=parents,
                     conversionMultiplier=0.01)
    with pytest.raises(ValueError, match='Multiple scalingOf'):
        convert(150, ambiguous, metre)


def test_local_prov_fixture_contains_resource_objects():
    graph = Graph().parse(pathlib.Path(__file__).parent / 'data/prov_person.jsonld',
                          format='json-ld')
    assert list(graph.objects(None, FOAF.mbox)) == [URIRef('mailto:john.doe@mail.de')]
    role = URIRef('http://www.w3.org/ns/dcat#hadRole')
    assert list(graph.objects(None, role)) == [
        URIRef('http://w3id.org/nfdi4ing/metadata4ing#ContactPerson')]


def test_same_base_identity_does_not_hide_conflicting_factors(convert):
    metre = Unit(id='http://qudt.org/vocab/unit/M', conversionMultiplier=1)
    centimetre = Unit(id='http://qudt.org/vocab/unit/CentiM', scalingOf=metre,
                      conversionMultiplier=0.01)
    conflicting = Unit(id=metre.id, conversionMultiplier=2)
    with pytest.raises(ValueError, match='Conflicting conversionMultiplier'):
        convert(150, centimetre, conflicting)


@pytest.mark.parametrize('fahrenheit,kelvin', [(32, 273.15), (212, 373.15),
                                             (-459.67, 0)])
def test_qudt_temperature_offsets_precede_multiplication(convert, fahrenheit, kelvin):
    # QUDT DEG_F: multiplier 5/9, offset 459.67, scalingOf K.
    base = Unit(id='http://qudt.org/vocab/unit/K', conversionMultiplier=1)
    source = Unit(id='http://qudt.org/vocab/unit/DEG_F', scalingOf=base,
                  conversionMultiplier=5 / 9, conversionOffset=459.67)
    celsius = Unit(id='http://qudt.org/vocab/unit/DEG_C', scalingOf=base,
                   conversionMultiplier=1, conversionOffset=273.15)
    assert convert(fahrenheit, source, base) == pytest.approx(kelvin, abs=1e-12)
    assert convert(kelvin, base, source) == pytest.approx(fahrenheit, abs=1e-12)
    assert convert(fahrenheit, source, celsius) == pytest.approx(kelvin - 273.15)


def test_qudt_reference_factors_are_not_multiplied_along_scaling_chain(convert):
    # QUDT MilliGM scales GM but its multiplier is 1e-6 (relative to kg).
    kilogram = Unit(id='http://qudt.org/vocab/unit/KiloGM', conversionMultiplier=1)
    gram = Unit(id='http://qudt.org/vocab/unit/GM', scalingOf=kilogram,
                conversionMultiplier=1e-3)
    milligram = Unit(id='http://qudt.org/vocab/unit/MilliGM', scalingOf=gram,
                     conversionMultiplier=1e-6)
    assert convert(1000, milligram, gram) == pytest.approx(1)
    assert convert(1, gram, milligram) == pytest.approx(1000)
    assert convert(1e6, milligram, kilogram) == pytest.approx(1)
    # Describing the same reference path directly must not change the result.
    direct = milligram.model_copy(update={'scalingOf': kilogram})
    assert convert(1000, direct, gram) == convert(1000, milligram, gram)


@pytest.mark.parametrize('field,value', [('conversionMultiplier', 0),
    ('conversionMultiplier', float('nan')), ('conversionMultiplier', float('inf')),
    ('conversionOffset', float('inf')), ('conversionOffset', float('nan'))])
@pytest.mark.parametrize('reverse', [False, True])
def test_invalid_conversion_coefficients_fail_explicitly(convert, field, value, reverse):
    base = Unit(id='urn:unit:base', conversionMultiplier=1)
    fields = {'conversionMultiplier': 0.01, field: value}
    invalid = Unit(id='urn:unit:invalid', scalingOf=base, **fields)
    source, target = (base, invalid) if reverse else (invalid, base)
    with pytest.raises(ValueError, match='finite nonzero multiplier and finite offset'):
        convert(1, source, target)


def test_missing_scaled_unit_factor_is_not_assumed_to_be_one(convert):
    base = Unit(id='urn:unit:base')
    incomplete = Unit(id='urn:unit:unknown-scale', scalingOf=base)
    with pytest.raises(ValueError, match='Missing conversionMultiplier'):
        convert(1, incomplete, base)


def test_scaling_cycles_use_resource_identity(convert):
    base = Unit(id='urn:unit:base')
    repeated = Unit(id='urn:unit:cycle', conversionMultiplier=1)
    source = Unit(id=repeated.id, scalingOf=repeated, conversionMultiplier=1)
    with pytest.raises(RuntimeError, match='Cycle detected'):
        convert(1, source, base)


def test_same_unit_identity_does_not_hide_conflicting_factors(convert):
    source = Unit(id='urn:unit:conflict', conversionMultiplier=1)
    target = Unit(id=source.id, conversionMultiplier=2)
    with pytest.raises(ValueError, match='Conflicting conversionMultiplier'):
        convert(1, source, target)
