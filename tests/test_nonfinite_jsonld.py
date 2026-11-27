"""Every JSON-LD export path must retain nonfinite values in valid JSON."""
import json
import math
from typing import Any, List

import pytest
from rdflib import Graph, Literal, Namespace, XSD
from rdflib.compare import isomorphic

from ontolutils import Thing, namespaces, serialize, urirefs


EX = Namespace('https://example.org/')


@namespaces(ex=str(EX))
@urirefs(Reading='ex:Reading', values='ex:values')
class Reading(Thing):
    values: List[Any]


def reject_constant(token):
    raise ValueError(f'Invalid JSON number: {token}')


@pytest.mark.parametrize('context', [None, {'v': '@value', 't': '@type'},
    {'number': {'@id': str(EX['values']), '@type': str(XSD.double)}}])
def test_jsonld_paths_keep_nonfinite_values_with_keyword_aliases_and_coercion(context, tmp_path):
    model = Reading(id=str(EX.reading), values=[float('nan'), float('inf'), -float('inf')])
    expected = Graph().parse(data=model.model_dump_jsonld(), format='json-ld')
    payloads = [model.model_dump_jsonld(context=context, rdflib_serialize=True),
                model.serialize('json-ld', context=context),
                model.serialize('application/ld+json', context=context, encoding='utf-8'),
                serialize([model], 'json-ld', context=context, auto_compact=True)]
    path = tmp_path / 'reading.jsonld'
    model.serialize('json-ld', context=context, destination=path, encoding='utf-8')
    payloads.append(path.read_bytes())
    for payload in payloads:
        json.loads(payload, parse_constant=reject_constant)
        graph = Graph().parse(data=payload, format='json-ld')
        assert isomorphic(graph, expected)
        values = list(graph.objects(EX.reading, EX['values']))
        assert len(values) == 3
        assert all(value.datatype == XSD.double for value in values)
        assert any(math.isnan(float(value)) for value in values)
        assert Literal(float('inf')) in values
        assert Literal(-float('inf')) in values


def test_nonfinite_graph_does_not_change_other_literal_metadata():
    model = Reading(id=str(EX.reading), values=[float('nan'),
        Literal('hello', lang='de'), Literal('003.120', datatype=XSD.decimal, normalize=False)])
    expected = Graph().parse(data=model.model_dump_jsonld(), format='json-ld')
    actual = Graph().parse(data=model.serialize('json-ld'), format='json-ld')
    assert isomorphic(actual, expected)
    assert (EX.reading, EX['values'], Literal('hello', lang='de')) in actual


def test_invalid_nonfinite_jsonld_context_is_rejected():
    model = Reading(values=[1])
    with pytest.raises(ValueError):
        model.model_dump_jsonld(context={'invalid': float('nan')})
