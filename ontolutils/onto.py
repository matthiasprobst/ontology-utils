"""Load Turtle ontologies and construct Python models for declared RDF classes."""

from dataclasses import dataclass
from hashlib import sha256
from keyword import iskeyword
from pathlib import Path
from types import SimpleNamespace
from typing import Any, Mapping
from unicodedata import normalize
from urllib.parse import urlsplit

from pydantic import create_model
from rdflib import Graph, OWL, RDF, RDFS, URIRef
from rdflib.namespace import split_uri
from requests import Session

from .classes import Thing, urirefs
from .classes.decorator import _get_predicate_fields
from .classes.utils import request_with_backoff


@dataclass(frozen=True)
class ModelField:
    """A mapped Pydantic field. The default is required unless supplied."""

    predicate: str
    annotation: Any
    default: Any = ...


@dataclass(frozen=True)
class Ontology:
    """Loaded RDF graph, class namespace, and generated model classes."""

    graph: Graph
    namespace: str
    models: SimpleNamespace


def _http_iri(iri: str) -> bool:
    parts = urlsplit(iri)
    return iri.startswith(("http://", "https://")) and bool(parts.hostname) and not any(
        character.isspace() for character in iri
    )


def _public_name(name: str) -> bool:
    return (name.isidentifier() and not name.startswith("_") and not iskeyword(name)
            and normalize("NFKC", name) == name)


def _class_namespace(graph: Graph, classes: set[str]) -> str:
    declared = {
        candidate
        for ontology in graph.subjects(RDF.type, OWL.Ontology)
        if isinstance(ontology, URIRef)
        for candidate in (str(ontology), f"{ontology}#", f"{ontology}/")
        if candidate.endswith(("#", "/")) and any(
            iri.startswith(candidate) for iri in classes
        )
    }
    if len(declared) == 1:
        return declared.pop()
    inferred = set()
    for iri in classes:
        try:
            inferred.add(split_uri(iri)[0])
        except ValueError:
            continue
    if not declared and len(inferred) == 1:
        return inferred.pop()
    raise ValueError("Pass namespace= to select the ontology's class vocabulary")


def load(
    source: str | Path,
    *,
    namespace: str | None = None,
    profile: Mapping[str, Mapping[str, ModelField]] | None = None,
    expected_sha256: str | None = None,
) -> Ontology:
    """Load a Turtle document from a local path or an HTTP(S) URL.

    Generate Thing subclasses for named OWL and RDFS classes in the selected
    namespace. Without a profile, each class has the common Thing fields.
    Use a profile to add field types, predicate IRIs, and Pydantic defaults.
    This loader uses the document's explicit declarations. It applies no
    entailment and does not fetch owl:imports.
    """
    if isinstance(source, str) and _http_iri(source):
        with Session() as session:
            response = request_with_backoff(
                "GET", source, session=session, headers={"Accept": "text/turtle"}
            )
            response.raise_for_status()
            data, base = response.content, response.url
    else:
        path = Path(source).resolve()
        data, base = path.read_bytes(), path.as_uri()
    if expected_sha256 is not None and sha256(data).hexdigest() != expected_sha256:
        raise ValueError("Ontology document does not match the expected SHA-256")

    graph = Graph().parse(data=data, format="turtle", publicID=base)
    classes = {
        str(subject)
        for kind in (OWL.Class, RDFS.Class)
        for subject in graph.subjects(RDF.type, kind)
        if isinstance(subject, URIRef) and _http_iri(str(subject))
    }
    namespace = namespace if namespace is not None else _class_namespace(graph, classes)
    if not _http_iri(namespace):
        raise ValueError("The class namespace must be an HTTP(S) IRI")
    names = {
        iri[len(namespace):]: iri for iri in classes
        if iri.startswith(namespace) and _public_name(iri[len(namespace):])
        and iri[len(namespace):] not in Thing.model_fields
    }
    if not names:
        raise ValueError(f"No named classes with Python identifiers in {namespace!r}")
    profile = profile or {}
    unknown = profile.keys() - names.keys()
    if unknown:
        raise ValueError(f"Profile refers to unknown classes: {', '.join(sorted(unknown))}")

    models = SimpleNamespace()
    for name, class_iri in sorted(names.items()):
        fields = {}
        predicates = {name: class_iri}
        for field_name, field in profile.get(name, {}).items():
            if (not _public_name(field_name) or field_name == name
                    or field_name in Thing.model_fields or hasattr(Thing, field_name)):
                raise ValueError(f"Invalid or inherited field {field_name!r} on {name}")
            if not _http_iri(field.predicate):
                raise ValueError(f"Field {name}.{field_name} needs an HTTP(S) predicate IRI")
            fields[field_name] = (field.annotation, field.default)
            predicates[field_name] = field.predicate
        model = urirefs(**predicates)(create_model(name, __base__=Thing, **fields))
        _get_predicate_fields(model)
        setattr(models, name, model)
    return Ontology(graph, namespace, models)
