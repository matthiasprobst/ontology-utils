from hashlib import sha256

import pytest
from pydantic import Field, ValidationError
from rdflib import Graph, Literal, RDF, URIRef
from rdflib.compare import isomorphic
from requests import Response

from ontolutils import Thing, onto
from ontolutils.typing import AnyIri


M4I = "http://w3id.org/nfdi4ing/metadata4ing#"
ONTOLOGY = """\
@prefix m4i: <http://w3id.org/nfdi4ing/metadata4ing#> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .

m4i: a owl:Ontology ; owl:imports <https://example.org/import.ttl> .
m4i:Tool a owl:Class .
m4i:hasParameter a owl:ObjectProperty ;
    rdfs:domain [ owl:unionOf (m4i:Method m4i:Tool) ] .
m4i:Laser a owl:Class ; rdfs:subClassOf m4i:Tool .
m4i:Sample a owl:Class .
m4i:Combined a owl:Class ; rdfs:subClassOf m4i:Tool, m4i:Sample .
m4i:intersection a owl:DatatypeProperty ;
    rdfs:domain [ owl:intersectionOf (m4i:Tool m4i:Sample) ] .
m4i:multipleDomains a owl:DatatypeProperty ; rdfs:domain m4i:Tool, m4i:Sample .
m4i:annotation a owl:DatatypeProperty ; rdfs:domain m4i:Tool .
<https://example.org/Other> a owl:Class .
"""
TOOL_IRI = "https://example.org/instruments/laser"
PARAMETER_IRI = "https://example.org/parameters/power"


def test_profile_generates_model_that_validates_and_round_trips_rdf(tmp_path):
    path = tmp_path / "m4i.ttl"
    path.write_text(ONTOLOGY, encoding="utf-8")
    profile = {"Tool": {"parameter": onto.ModelField(M4I + "hasParameter", AnyIri,
                                                   Field(alias="parameter_iri"))}}

    loaded = onto.load(path, profile=profile)
    tool_model = loaded.models.Tool
    assert issubclass(tool_model, Thing)
    assert loaded.namespace == M4I
    assert "hasParameter" not in tool_model.rdf_fields()
    assert not hasattr(loaded.models, "Other")
    with pytest.raises(ValidationError):
        tool_model(id=TOOL_IRI)
    with pytest.raises(ValidationError):
        tool_model(id=TOOL_IRI, parameter_iri="not an IRI")

    tool = tool_model(id=TOOL_IRI, parameter_iri=PARAMETER_IRI)
    actual = Graph().parse(data=tool.serialize("ttl"), format="turtle")
    expected = Graph().parse(
        data=f"<{TOOL_IRI}> a <{M4I}Tool> ; <{M4I}hasParameter> <{PARAMETER_IRI}> .",
        format="turtle",
    )
    assert isomorphic(actual, expected)
    restored = tool_model.from_graph(actual, limit=1)
    assert restored.parameter == PARAMETER_IRI


def test_load_url_honors_digest_and_ignores_owl_imports(monkeypatch):
    url = "https://example.org/m4i.ttl"
    response = Response()
    response.status_code = 200
    response.url = url
    response._content = ONTOLOGY.encode()
    calls = []

    def get(method, source, **kwargs):
        calls.append((method, source, kwargs["headers"]["Accept"]))
        return response

    monkeypatch.setattr(onto, "request_with_backoff", get)
    digest = sha256(response.content).hexdigest()
    assert onto.load(url, expected_sha256=digest).models.Tool(id=TOOL_IRI).id == TOOL_IRI
    assert calls == [("GET", url, "text/turtle")]
    with pytest.raises(ValueError, match="SHA-256"):
        onto.load(url, expected_sha256="0" * 64)


def test_profile_typo_and_ambiguous_namespace_fail(tmp_path):
    path = tmp_path / "classes.ttl"
    path.write_text(ONTOLOGY.replace("m4i: a owl:Ontology ; owl:imports <https://example.org/import.ttl> .", ""),
                    encoding="utf-8")
    with pytest.raises(ValueError, match="Pass namespace"):
        onto.load(path)
    with pytest.raises(ValueError, match="unknown classes"):
        onto.load(path, namespace=M4I, profile={"tool": {}})


def test_discovers_union_and_inherited_domains_without_a_profile(tmp_path):
    path = tmp_path / "m4i.ttl"
    path.write_text(ONTOLOGY, encoding="utf-8")
    models = onto.load(path).models
    assert models.Tool.rdf_fields()["hasParameter"] == M4I + "hasParameter"
    assert models.Laser.rdf_fields()["hasParameter"] == M4I + "hasParameter"
    assert "hasParameter" not in models.Sample.rdf_fields()
    assert "multipleDomains" not in models.Tool.rdf_fields()
    assert "multipleDomains" not in models.Sample.rdf_fields()
    assert "intersection" not in models.Tool.rdf_fields()
    assert models.Combined.rdf_fields()["intersection"] == M4I + "intersection"
    assert models.Combined.rdf_fields()["multipleDomains"] == M4I + "multipleDomains"
    assert models.Tool().hasParameter is None

    tool = models.Tool(id=TOOL_IRI, hasParameter=[PARAMETER_IRI], annotation="calibrated")
    graph = Graph().parse(data=tool.serialize("ttl"), format="turtle")
    assert (URIRef(TOOL_IRI), RDF.type, URIRef(M4I + "Tool")) in graph
    assert (URIRef(TOOL_IRI), URIRef(M4I + "hasParameter"), URIRef(PARAMETER_IRI)) in graph
    assert (URIRef(TOOL_IRI), URIRef(M4I + "annotation"), Literal("calibrated")) in graph
    assert models.Tool.from_graph(graph, limit=1).hasParameter == PARAMETER_IRI
