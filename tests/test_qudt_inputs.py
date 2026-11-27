"""Curated QUDT conveniences must preserve exact resource identity."""
import pytest
from pydantic import ValidationError
from rdflib import Graph, Literal, URIRef

from ontology_fixtures.qudt import QuantityKind, Unit


KIND = 'http://qudt.org/vocab/quantitykind/'


@pytest.mark.parametrize('value,expected', [('Length', KIND + 'Length'),
    (KIND + 'Length', KIND + 'Length'),
    ('https://example.org/kind', 'https://example.org/kind'),
    (URIRef('urn:example:kind'), 'urn:example:kind')])
def test_quantity_kind_shorthand_and_explicit_iris(value, expected):
    unit = Unit(id='urn:example:unit', has_quantity_kind=value)
    assert unit.hasQuantityKind == expected
    graph = Graph().parse(data=unit.model_dump_jsonld(), format='json-ld')
    assert (URIRef(unit.id), URIRef(Unit.iri('hasQuantityKind')), URIRef(expected)) in graph


def test_quantity_kind_lists_normalize_each_shorthand_and_keep_models():
    kind = QuantityKind(id='urn:example:kind', label='Custom kind')
    unit = Unit(has_quantity_kind=['Length', KIND + 'Area', kind])
    assert unit.hasQuantityKind[:2] == [KIND + 'Length', KIND + 'Area']
    assert unit.hasQuantityKind[2].id == kind.id
    unit.hasQuantityKind = ['Time']
    assert unit.hasQuantityKind == [KIND + 'Time']


@pytest.mark.parametrize('value', [Literal(KIND + 'Length'), [Literal(KIND + 'Length')],
                                  '', 'not a kind', 'Length/Area'])
def test_quantity_kind_rejects_literal_and_malformed_shorthand(value):
    with pytest.raises(ValidationError):
        Unit(has_quantity_kind=value)


@pytest.mark.parametrize('alias', ['wikidataMatch', 'wikidata_match', 'wikidata_match '])
def test_wikidata_alias_accepts_legacy_input_and_serializes_canonical_name(alias):
    unit = Unit(**{alias: 'https://www.wikidata.org/entity/Q11573'})
    assert unit.wikidataMatch == 'https://www.wikidata.org/entity/Q11573'
    assert unit.wikidata_match == unit.wikidataMatch
    assert unit.model_dump(by_alias=True)['wikidata_match'] == unit.wikidataMatch
    assert 'wikidata_match ' not in unit.model_dump(by_alias=True)
