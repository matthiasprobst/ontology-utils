"""Dictionary queries must not merge different RDF predicates."""
import json
import pytest
from rdflib import Graph
from rdflib.compare import isomorphic

from ontolutils import dquery


@pytest.mark.parametrize('identifier', ['https://example.org/item', 'https://example.org/label'])
def test_colliding_local_names_keep_full_iri_keys_and_context(identifier):
    data = {'@id': identifier, '@type': 'https://example.org/Type',
            'https://example.org/a/value': 'measured',
            'https://example.org/b/value': 'reference',
            'https://example.org/label': 'sample'}
    result = dquery('<https://example.org/Type>', data=json.dumps(data))[0]
    assert result['@id'] == identifier
    assert result['https://example.org/a/value'] == 'measured'
    assert result['https://example.org/b/value'] == 'reference'
    assert result['@context']['https://example.org/a/value'] == 'https://example.org/a/value'
    assert result['label'] == 'sample'
    assert 'value' not in result
    assert isomorphic(Graph().parse(data=json.dumps(data), format='json-ld'),
                      Graph().parse(data=json.dumps(result), format='json-ld'))
