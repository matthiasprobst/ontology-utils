"""SPARQL result aggregation must compare RDF terms, not string substrings."""
from typing import Any, List

import pytest
from rdflib import BNode, Graph, Literal, Namespace, RDF

from ontolutils import Thing, namespaces, urirefs


EX = Namespace('https://example.org/')


@namespaces(ex=str(EX))
@urirefs(Record='ex:Record', values='ex:value')
class Record(Thing):
    values: List[Any]


def test_distinct_substrings_and_duplicate_rows_survive_aggregation():
    result = Graph().query('''SELECT ?id ?values WHERE {
        VALUES (?id ?values) {
            (<https://example.org/one> "alphabet")
            (<https://example.org/one> "alpha")
            (<https://example.org/one> "alphabet")
        }
    } ORDER BY DESC(STR(?values))''')
    records = Record.from_sparql(result)
    assert len(records) == 1
    assert records[0].values == [Literal('alphabet'), Literal('alpha')]


@pytest.mark.parametrize('subject', [EX.one, BNode('record')])
def test_singleton_list_and_rdf_metadata_are_preserved(subject):
    graph = Graph()
    graph.add((subject, RDF.type, EX.Record))
    graph.add((subject, EX.value, Literal('same text', lang='de')))
    records = Record.from_sparql(graph.query(Record.create_query()))
    assert len(records) == 1
    assert records[0].id == (subject.n3() if isinstance(subject, BNode) else str(subject))
    assert records[0].values == [Literal('same text', lang='de')]


def test_term_identity_includes_language_and_datatype():
    graph = Graph()
    graph.add((EX.one, RDF.type, EX.Record))
    expected = [Literal('alpha'), Literal('alpha', lang='de'),
                Literal('alpha', datatype=EX.datatype)]
    for value in expected:
        graph.add((EX.one, EX.value, value))
    records = Record.from_sparql(graph.query(Record.create_query()))
    assert set(records[0].values) == set(expected)


def test_validation_failure_policy_is_applied_per_resource():
    @namespaces(ex=str(EX))
    @urirefs(Count='ex:Count', values='ex:value')
    class Count(Thing):
        values: List[int]

    graph = Graph()
    for subject, value in [(EX.good, Literal(0)), (EX.bad, Literal('not a number'))]:
        graph.add((subject, RDF.type, EX.Count))
        graph.add((subject, EX.value, value))
    query = Count.create_query()
    with pytest.raises(ValueError):
        Count.from_sparql(graph.query(query))
    records = Count.from_sparql(graph.query(query), raise_on_error=False)
    assert len(records) == 1
    assert records[0].id == str(EX.good)
    assert records[0].values == [0]


@pytest.mark.parametrize('query', [
    'SELECT ?values WHERE { VALUES ?values { "value" } }',
    'SELECT ?id ?values WHERE { VALUES (?id ?values) { ("https://example.org/literal" "value") } }',
    'SELECT ?id ?values WHERE { VALUES ?values { "value" } OPTIONAL { ?id <urn:absent> ?values } }'])
def test_result_rows_must_identify_an_rdf_resource(query):
    with pytest.raises(ValueError, match=r'bind \?id'):
        Record.from_sparql(Graph().query(query), raise_on_error=False)
