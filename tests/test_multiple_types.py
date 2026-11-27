"""Multiple type assertions must not remove descriptions or duplicate values."""
import json

from rdflib import Graph
from rdflib.compare import isomorphic

from ontolutils import LangString, Thing, dquery


def test_dictionary_keeps_root_and_nested_types():
    data = {'@id': 'https://example.org/root',
            '@type': ['https://example.org/Root', 'https://example.org/Other'],
            'https://example.org/child': {
                '@id': 'https://example.org/child1',
                '@type': ['https://example.org/Child', 'https://example.org/Extra'],
                'https://example.org/name': 'described'}}
    payload = json.dumps(data)
    result = dquery('<https://example.org/Root>', data=payload)[0]
    assert set(result['@type']) == set(data['@type'])
    assert set(result['child']['@type']) == set(data['https://example.org/child']['@type'])
    assert result['child']['name'] == 'described'
    assert isomorphic(Graph().parse(data=payload, format='json-ld'),
                      Graph().parse(data=json.dumps(result), format='json-ld'))


def test_generic_model_does_not_duplicate_fields_for_each_type():
    payload = json.dumps({'@id': 'https://example.org/root',
                         '@type': ['https://example.org/A', 'https://example.org/B'],
                         'http://www.w3.org/2000/01/rdf-schema#label': 'once'})
    result = Thing.from_jsonld(data=payload, limit=1)
    assert isinstance(result.label, LangString)
    assert result.label.value == 'once'
