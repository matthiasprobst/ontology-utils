"""Controlled ontology resources for deterministic domain-model checks."""
from pathlib import Path

import pytest
from rdflib import BNode, Graph


@pytest.fixture(autouse=True)
def local_qudt_lookups(request, monkeypatch):
    """Exercise domain lookups against archived QUDT subject descriptions."""
    if request.module.__name__.rsplit('.', 1)[-1] not in {'test_qudt', 'test_m4i', 'test_sosa'}:
        yield
        return
    from ontolutils.ex.qudt import utils
    graph = Graph().parse(Path(__file__).parent / 'data/qudt_lookup.ttl', format='turtle')
    units = Graph()
    kinds = Graph()
    for triple in graph:
        subject = triple[0]
        if isinstance(subject, BNode) or str(subject).startswith('http://qudt.org/vocab/unit/'):
            units.add(triple)
        else:
            kinds.add(triple)
    utils._get_unit_by_iri.cache_clear()
    utils._get_quantity_kind_by_iri.cache_clear()
    monkeypatch.setattr(utils, '_get_qudt_unit_graph', lambda: units)
    monkeypatch.setattr(utils, '_get_qudt_kind_graph', lambda: kinds)
    try:
        yield
    finally:
        utils._get_unit_by_iri.cache_clear()
        utils._get_quantity_kind_by_iri.cache_clear()
