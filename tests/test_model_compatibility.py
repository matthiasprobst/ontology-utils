"""Offline behavioral contracts for the supported Pydantic/RDFLib API families."""
import json
from datetime import datetime, timezone
from typing import Optional

import pytest
from pydantic import Field, FileUrl, HttpUrl, ValidationError
from rdflib import BNode, Graph, Literal, Namespace, RDF, URIRef
from rdflib.compare import isomorphic

from ontolutils import Thing, namespaces, urirefs
from ontology_fixtures.prov import Organization, Person
from ontolutils.typing import AnyIriOf


EX = Namespace("https://example.org/compatibility/")


@pytest.mark.parametrize('text', ['ex:sample', 'schema:Person', 'urn:example:literal'])
def test_literal_prefixes_are_not_expanded(text):
    original = Thing(id=str(EX.resource), label=text)
    restored = Thing.from_jsonld(data=original.model_dump_jsonld(),
                                context={'ex': str(EX), 'schema': 'https://schema.org/'},
                                limit=1)
    assert str(restored.label) == text


def test_non_rdf_type_predicate_is_retained():
    # Dictionary querying must distinguish rdf:type from another namespace's type.
    from ontolutils import dquery
    payload = {'@context': {'ex': str(EX)}, '@id': str(EX.resource),
               '@type': 'ex:Classified', 'ex:type': 'measured'}
    result = dquery('ex:Classified', data=json.dumps(payload), context={'ex': str(EX)})
    assert result[0]['type'] == 'measured'


@pytest.mark.parametrize("input_kind", ["text", "dict", "file"])
def test_loading_preserves_schema_http_literals_and_subject(input_kind, tmp_path):
    original = Thing(id="http://schema.org/example",
                     label="Source: http://schema.org/",
                     comment=Literal("http://schema.org/Person", lang="en"))
    payload = original.model_dump_jsonld()
    expected = Graph().parse(data=payload, format="json-ld")
    if input_kind == "file":
        path = tmp_path / "resource.jsonld"
        path.write_text(payload, encoding="utf-8")
        restored = Thing.from_jsonld(source=path, limit=1)
    else:
        data = json.loads(payload) if input_kind == "dict" else payload
        restored = Thing.from_jsonld(data=data, limit=1)
    actual = Graph().parse(data=restored.model_dump_jsonld(), format="json-ld")
    assert isomorphic(actual, expected)


@namespaces(ex=str(EX))
@urirefs(Observation="ex:Observation", sampleCount="ex:sampleCount",
         active="ex:active", observedAt="ex:observedAt", creator="ex:creator")
class Observation(Thing):
    sampleCount: int = Field(alias="sample_count")
    active: bool
    observedAt: datetime = Field(alias="observed_at")
    creator: Optional[AnyIriOf[Person]] = None


def test_aliases_and_assignment_validation():
    fields = dict(id=str(EX.observation), active=True,
                  observed_at="2026-01-01T12:00:00Z")
    by_alias = Observation(sample_count="3", **fields)
    by_name = Observation(sampleCount=3, **fields)
    assert by_alias == by_name
    assert by_alias.sample_count == by_alias.sampleCount == 3
    assert by_alias.observedAt == datetime(2026, 1, 1, 12, tzinfo=timezone.utc)

    with pytest.raises(ValidationError) as error:
        by_alias.sampleCount = "invalid"
    assert error.value.errors()[0]["loc"] == ("sampleCount",)
    assert by_alias.sampleCount == 3


@pytest.mark.parametrize("value", ["invalid", None, []])
def test_invalid_field_values_raise_validation_errors(value):
    with pytest.raises(ValidationError) as error:
        Observation(sample_count=value, active=True, observed_at="2026-01-01")
    assert error.value.errors()[0]["loc"] == ("sample_count",)


def test_required_field_and_identifier_validation():
    with pytest.raises(ValidationError) as error:
        Observation(active=True, observed_at="2026-01-01")
    assert error.value.errors()[0]["type"] == "missing"
    assert error.value.errors()[0]["loc"] == ("sample_count",)


@pytest.mark.parametrize("identifier", ["not-an-iri", 123, [], {}])
def test_invalid_identifiers_raise_validation_errors(identifier):
    with pytest.raises(ValidationError):
        Thing(id=identifier)


@pytest.mark.parametrize("identifier", [FileUrl("file:///tmp/data.ttl"),
                                        HttpUrl("https://example.org/data"),
                                        "urn:example:data", "file:///tmp/data.ttl"])
def test_url_objects_and_non_http_identifiers(identifier):
    assert Thing(id=identifier).id == str(identifier)


@pytest.mark.parametrize("identifier", [str(EX.person), URIRef(EX.person),
                                        BNode("person"), "_:person"])
def test_identifiers_and_references_are_rdf_nodes(identifier):
    person = Person(id=identifier, first_name="Ada")
    observation = Observation(id=str(EX.observation), sample_count=3, active=True,
                              observed_at="2026-01-01T12:00:00Z", creator=person)
    graph = Graph().parse(data=observation.model_dump_jsonld(), format="json-ld")
    creator = graph.value(EX.observation, EX.creator)
    assert isinstance(creator, BNode if str(person.id).startswith("_:") else URIRef)
    assert (creator, RDF.type, URIRef(Person.iri())) in graph
    observation.creator = str(EX.external_person)
    graph = Graph().parse(data=observation.model_dump_jsonld(), format="json-ld")
    assert (EX.observation, EX.creator, EX.external_person) in graph
    assert (EX.external_person, RDF.type, URIRef(Person.iri())) not in graph
    with pytest.raises(ValidationError):
        observation.creator = 123


@pytest.fixture(params=["https://example.org/compatibility/lab", "_:lab"])
def person_and_graph(request):
    organization = Organization(id=request.param,
                                label=[Literal("Laboratory", lang="en"), Literal("Labor", lang="de")])
    person = Person(id=str(EX.person), first_name="Ada", lastName="Lovelace",
                    label=[Literal("Researcher", lang="en"), Literal("Forscherin", lang="de")],
                    affiliation=organization)
    lab = "_:lab" if request.param.startswith("_:") else f"<{request.param}>"
    expected = Graph().parse(data=f'''
        @prefix ex: <{EX}> .
        @prefix prov: <http://www.w3.org/ns/prov#> .
        @prefix foaf: <http://xmlns.com/foaf/0.1/> .
        @prefix schema: <https://schema.org/> .
        @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
        ex:person a prov:Person ; foaf:firstName "Ada" ; foaf:lastName "Lovelace" ;
            rdfs:label "Researcher"@en, "Forscherin"@de ; schema:affiliation {lab} .
        {lab} a prov:Organization ; rdfs:label "Laboratory"@en, "Labor"@de .
    ''', format="turtle")
    return person, expected


@pytest.mark.parametrize("format", ["json-ld", "ttl", "n3", "nt", "xml"])
def test_serialization_preserves_expected_graph(person_and_graph, format):
    person, expected = person_and_graph
    graph = Graph().parse(data=person.serialize(format=format), format=format)
    assert isomorphic(graph, expected)


@pytest.mark.parametrize("resolve_keys", [True, False])
@pytest.mark.parametrize("rdflib_serialize", [True, False])
def test_jsonld_options_preserve_expected_graph(person_and_graph, resolve_keys, rdflib_serialize):
    person, expected = person_and_graph
    data = person.model_dump_jsonld(resolve_keys=resolve_keys, rdflib_serialize=rdflib_serialize)
    assert isomorphic(Graph().parse(data=data, format="json-ld"), expected)


@pytest.mark.parametrize("format", ["json-ld", "ttl"])
def test_model_parse_round_trip_preserves_nested_language_tags(person_and_graph, format):
    person, expected = person_and_graph
    data = person.serialize(format=format)
    if format == "json-ld":
        restored = Person.from_jsonld(data=json.loads(data), limit=1)
    else:
        restored = Person.from_ttl(data=data, limit=1)
    assert restored.firstName == "Ada"
    assert restored.last_name == "Lovelace"
    actual = Graph().parse(data=restored.model_dump_jsonld(), format="json-ld")
    assert isomorphic(actual, expected)


@pytest.mark.parametrize("format", ["json-ld", "ttl", "n3", "nt", "xml"])
def test_typed_literals_survive_serialization_and_model_parsing(format):
    observation = Observation(id=str(EX.observation), sample_count=3, active=True,
                              observed_at="2026-01-01T12:00:00Z")
    expected = Graph().parse(data=f'''
        @prefix ex: <{EX}> .
        @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
        ex:observation a ex:Observation ; ex:sampleCount 3 ; ex:active true ;
            ex:observedAt "2026-01-01T12:00:00+00:00"^^xsd:dateTime .
    ''', format="turtle")
    actual = Graph().parse(data=observation.serialize(format=format), format=format)
    assert isomorphic(actual, expected)
    restored = Observation.from_jsonld(data=actual.serialize(format="json-ld"), limit=1)
    assert restored == observation
