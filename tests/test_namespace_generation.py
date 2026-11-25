from rdflib import Graph, OWL, RDF, URIRef
import pytest

from ontolutils.namespace_generation import render_namespace


def test_render_namespace_is_deterministic_and_preserves_term_iris():
    base = "https://example.org/terms#"
    terms = ["Device", "M-PER-SEC", "_42", "class", "mro"]
    triples = [(URIRef(base + name), RDF.type, OWL.Class) for name in terms]
    triples.append((URIRef("https://example.org/elsewhere"), RDF.type, OWL.Class))
    first, second = Graph(), Graph()
    for triple in triples:
        first.add(triple)
    for triple in reversed(triples):
        second.add(triple)

    source = render_namespace(first, base, "EX")
    assert source == render_namespace(second, base, "EX")
    generated = {}
    exec(source, generated)
    namespace = generated["EX"]
    assert namespace.Device == URIRef(base + "Device")
    for name in terms:
        assert namespace[name] == URIRef(base + name)
    with pytest.raises(AttributeError):
        namespace["elsewhere"]


def test_render_namespace_rejects_empty_namespace_selection():
    with pytest.raises(ValueError, match="No typed RDF terms"):
        render_namespace(Graph(), "https://example.org/terms#", "EX")
