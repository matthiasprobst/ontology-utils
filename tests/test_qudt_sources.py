"""QUDT resolution must use verified release bytes and fail predictably."""
from hashlib import sha256

import pytest
import requests

from ontology_fixtures.qudt import Unit
from ontology_fixtures.qudt import utils


def test_verified_source_and_timeout(monkeypatch):
    content = b'<urn:example:unit> a <http://qudt.org/schema/qudt/Unit> .'
    response = requests.Response()
    response.status_code = 200
    response._content = content
    monkeypatch.setitem(utils._QUDT_SOURCES, 'unit', ('test.ttl', sha256(content).hexdigest()))

    def get(url, **kwargs):
        assert utils.QUDT_SOURCE_COMMIT in url
        assert kwargs['timeout'] == (5, 30)
        return response

    monkeypatch.setattr(utils.requests, 'get', get)
    assert len(utils._load_qudt_graph('unit')) == 1
    response._content = b'changed'
    with pytest.raises(ValueError, match='checksum mismatch'):
        utils._load_qudt_graph('unit')
    response.status_code = 404
    with pytest.raises(requests.HTTPError):
        utils._load_qudt_graph('unit')


def test_missing_quantity_kind_is_domain_error():
    with pytest.raises(ValueError, match='has no quantity kind'):
        utils.get_quantity_kind(Unit(id='https://example.org/unit/no-kind'))


def test_list_of_quantity_kind_iris(monkeypatch):
    graph = utils.rdflib.Graph().parse(data='''
        <https://example.org/kind> a <http://qudt.org/schema/qudt/QuantityKind> .
    ''', format='turtle')
    monkeypatch.setattr(utils, '_get_qudt_kind_graph', lambda: graph)
    unit = Unit(id='urn:example:unit', hasQuantityKind=['https://example.org/kind'])
    assert utils.get_quantity_kind(unit).id == 'https://example.org/kind'
    unit.hasQuantityKind = ['https://example.org/kind', 'https://example.org/other']
    with pytest.raises(ValueError, match='multiple quantity kinds'):
        utils.get_quantity_kind(unit)


def test_cached_models_are_not_shared_with_callers(monkeypatch):
    graph = utils.rdflib.Graph().parse(data='''
        <https://example.org/cache-unit> a <http://qudt.org/schema/qudt/Unit> .
        <https://example.org/cache-kind> a <http://qudt.org/schema/qudt/QuantityKind> .
    ''', format='turtle')
    monkeypatch.setattr(utils, '_get_qudt_unit_graph', lambda: graph)
    monkeypatch.setattr(utils, '_get_qudt_kind_graph', lambda: graph)
    for lookup, iri in [(utils.get_unit, 'https://example.org/cache-unit'),
                        (utils.get_quantity_kind, 'https://example.org/cache-kind')]:
        first = lookup(iri)
        first.label = 'changed by caller'
        assert lookup(iri).label is None


@pytest.mark.parametrize('kinds', [
    ['https://example.org/energy', 'https://example.org/torque'],
    ['https://example.org/torque', 'https://example.org/energy'],
])
def test_multiple_quantity_kinds_require_explicit_selection(kinds, monkeypatch):
    def unexpected_fetch():
        pytest.fail('Ambiguous scientific interpretation must fail before downloading')

    monkeypatch.setattr(utils, '_get_qudt_kind_graph', unexpected_fetch)
    unit = Unit(id='https://example.org/ambiguous-unit', hasQuantityKind=kinds)
    with pytest.raises(ValueError, match='multiple quantity kinds'):
        utils.get_quantity_kind(unit)
