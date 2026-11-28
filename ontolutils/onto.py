"""Load Turtle ontologies and construct Python models for declared RDF classes."""

from dataclasses import dataclass
from datetime import date, datetime, time, timedelta
from decimal import Decimal
from hashlib import sha256
from keyword import iskeyword
from pathlib import Path
from types import SimpleNamespace
from typing import Any, Mapping, Union
from unicodedata import normalize
from urllib.parse import urlsplit

from pydantic import ConfigDict, create_model
from rdflib import BNode, Graph, Literal, OWL, RDF, RDFS, URIRef
from rdflib.namespace import split_uri
from requests import Session

from .classes import Thing, urirefs
from .classes.decorator import _get_predicate_fields
from .classes.utils import request_with_backoff
from .typing import AnyThingOrList


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


class _OntologyThing(Thing):
    model_config = ConfigDict(**Thing.model_config, arbitrary_types_allowed=True)

    @classmethod
    def rdf_fields(cls) -> dict[str, str]:
        """Return Python field names and their mapped predicate IRIs."""
        return {field: iri for iri, field in _get_predicate_fields(cls).items()}


def _matches_domain(graph, expression, ancestors, seen=frozenset()):
    if isinstance(expression, URIRef):
        return expression in ancestors
    if not isinstance(expression, BNode) or expression in seen:
        return False
    seen = seen | {expression}
    for operator, combine in ((OWL.unionOf, any), (OWL.intersectionOf, all)):
        lists = list(graph.objects(expression, operator))
        if len(lists) == 1:
            try:
                members = list(graph.items(lists[0]))
            except ValueError:
                return False
            return bool(members) and combine(
                _matches_domain(graph, member, ancestors, seen) for member in members
            )
    return False


_XSD = "http://www.w3.org/2001/XMLSchema#"
_XSD_PYTHON_TYPES = {
    URIRef(_XSD + "string"): str,
    URIRef(_XSD + "normalizedString"): str,
    URIRef(_XSD + "token"): str,
    URIRef(_XSD + "language"): str,
    URIRef(_XSD + "Name"): str,
    URIRef(_XSD + "NCName"): str,
    URIRef(_XSD + "NMTOKEN"): str,
    URIRef(_XSD + "anyURI"): str,
    URIRef(_XSD + "boolean"): bool,
    URIRef(_XSD + "decimal"): Decimal,
    URIRef(_XSD + "integer"): int,
    URIRef(_XSD + "nonPositiveInteger"): int,
    URIRef(_XSD + "negativeInteger"): int,
    URIRef(_XSD + "long"): int,
    URIRef(_XSD + "int"): int,
    URIRef(_XSD + "short"): int,
    URIRef(_XSD + "byte"): int,
    URIRef(_XSD + "nonNegativeInteger"): int,
    URIRef(_XSD + "unsignedLong"): int,
    URIRef(_XSD + "unsignedInt"): int,
    URIRef(_XSD + "unsignedShort"): int,
    URIRef(_XSD + "unsignedByte"): int,
    URIRef(_XSD + "positiveInteger"): int,
    URIRef(_XSD + "float"): float,
    URIRef(_XSD + "double"): float,
    URIRef(_XSD + "date"): date,
    URIRef(_XSD + "dateTime"): datetime,
    URIRef(_XSD + "time"): time,
    URIRef(_XSD + "duration"): timedelta,
}


def _range_members(graph, expression):
    """Expand a datatype range union into its member IRIs."""
    if not isinstance(expression, BNode):
        return [expression]
    unions = list(graph.objects(expression, OWL.unionOf))
    if len(unions) != 1:
        return None
    try:
        members = list(graph.items(unions[0]))
    except ValueError:
        return None
    if not members:
        return None
    result = []
    for member in members:
        nested = _range_members(graph, member)
        if nested is None:
            return None
        result.extend(nested)
    return result


def _datatype_annotation(graph, predicate):
    """Infer a Python annotation from one unambiguous datatype range."""
    ranges = list(graph.objects(predicate, RDFS.range))
    if len(ranges) != 1:
        return Any
    members = _range_members(graph, ranges[0])
    if members is None:
        return Any
    annotations = []
    for member in members:
        annotation = _XSD_PYTHON_TYPES.get(member)
        if annotation is None:
            if member == RDFS.Literal:
                return Any
            # Unknown datatypes are RDF literals. Keeping the RDFLib term
            # preserves its datatype IRI during model serialization.
            annotation = Literal
        if annotation not in annotations:
            annotations.append(annotation)
    return annotations[0] if len(annotations) == 1 else Union[tuple(annotations)]


def _discover_fields(graph, class_iri, domains, reserved_names, reserved_predicates):
    ancestors = {URIRef(class_iri)}
    pending = list(ancestors)
    while pending:
        for parent in graph.objects(pending.pop(), RDFS.subClassOf):
            if isinstance(parent, URIRef) and parent not in ancestors:
                ancestors.add(parent)
                pending.append(parent)

    candidates = {}
    for predicate, expressions in domains.items():
        if predicate in reserved_predicates or not all(
            _matches_domain(graph, domain, ancestors) for domain in expressions
        ):
            continue
        try:
            _, name = split_uri(predicate)
        except ValueError:
            continue
        if _public_name(name) and not (
            name in reserved_names or hasattr(_OntologyThing, name)
        ):
            candidates.setdefault(name, []).append(predicate)
    return {
        name: ModelField(
            str(predicates[0]),
            AnyThingOrList | None if (predicates[0], RDF.type, OWL.ObjectProperty) in graph
            else _datatype_annotation(graph, predicates[0]),
            None,
        )
        for name, predicates in sorted(candidates.items())
        if len(predicates) == 1
    }


def load(
    source: str | Path,
    *,
    namespace: str | None = None,
    profile: Mapping[str, Mapping[str, ModelField]] | None = None,
    expected_sha256: str | None = None,
) -> Ontology:
    """Load a Turtle document from a local path or an HTTP(S) URL.

    Generate Thing subclasses for named OWL and RDFS classes in the selected
    namespace. Discover optional fields from explicit property domains and
    named superclass links, including domain unions and intersections.
    Profiles can override discovered fields and add application mappings.
    The loader does not fetch owl:imports or run an OWL reasoner.
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

    domains = {}
    for predicate, domain in graph.subject_objects(RDFS.domain):
        if isinstance(predicate, URIRef) and _http_iri(str(predicate)):
            domains.setdefault(predicate, set()).add(domain)

    models = SimpleNamespace()
    inherited_predicates = {URIRef(iri) for iri in _OntologyThing.rdf_fields().values()}
    for name, class_iri in sorted(names.items()):
        fields = {}
        predicates = {name: class_iri}
        custom = profile.get(name, {})
        discovered = _discover_fields(
            graph, class_iri, domains,
            {name, *Thing.model_fields, *custom},
            inherited_predicates | {URIRef(field.predicate) for field in custom.values()},
        )
        for field_name, field in {**discovered, **custom}.items():
            if (not _public_name(field_name) or field_name == name
                    or field_name in Thing.model_fields or hasattr(_OntologyThing, field_name)):
                raise ValueError(f"Invalid or inherited field {field_name!r} on {name}")
            if not _http_iri(field.predicate):
                raise ValueError(f"Field {name}.{field_name} needs an HTTP(S) predicate IRI")
            fields[field_name] = (field.annotation, field.default)
            predicates[field_name] = field.predicate
        model = urirefs(**predicates)(create_model(name, __base__=_OntologyThing, **fields))
        _get_predicate_fields(model)
        setattr(models, name, model)
    return Ontology(graph, namespace, models)
