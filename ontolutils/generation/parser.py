from __future__ import annotations

import json
from typing import Any, Iterable

from rdflib import BNode, Graph, Literal, RDF, RDFS, URIRef
from rdflib.collection import Collection
from rdflib.namespace import OWL

# rdflib doesn't expose all OWL terms as attributes on OWL, so define the URIs we need:
OWL_QUALIFIED_CARD = URIRef("http://www.w3.org/2002/07/owl#qualifiedCardinality")
OWL_MIN_QUALIFIED_CARD = URIRef("http://www.w3.org/2002/07/owl#minQualifiedCardinality")
OWL_MAX_QUALIFIED_CARD = URIRef("http://www.w3.org/2002/07/owl#maxQualifiedCardinality")
OWL_ON_CLASS = URIRef("http://www.w3.org/2002/07/owl#onClass")
OWL_ON_DATA_RANGE = URIRef("http://www.w3.org/2002/07/owl#onDataRange")

CARD_PREDICATES = [
    (OWL.cardinality, "cardinality"),
    (OWL.minCardinality, "minCardinality"),
    (OWL.maxCardinality, "maxCardinality"),
    (OWL_QUALIFIED_CARD, "qualifiedCardinality"),
    (OWL_MIN_QUALIFIED_CARD, "minQualifiedCardinality"),
    (OWL_MAX_QUALIFIED_CARD, "maxQualifiedCardinality"),
]

FILLER_PREDICATES = [
    (OWL.someValuesFrom, "someValuesFrom"),
    (OWL.allValuesFrom, "allValuesFrom"),
    (OWL.hasValue, "hasValue"),
]


def as_python(node):
    if node is None:
        return None
    if isinstance(node, URIRef):
        return str(node)
    if isinstance(node, Literal):
        return node.toPython()
    # BNode or other
    return str(node)


def first_label(g: Graph, s: URIRef) -> str | None:
    for o in g.objects(s, RDFS.label):
        if isinstance(o, Literal):
            return str(o)
    return None


def is_functional_property(g: Graph, p: URIRef) -> bool:
    return (p, RDF.type, OWL.FunctionalProperty) in g


def prop_kind(g: Graph, p: URIRef) -> str:
    if (p, RDF.type, OWL.ObjectProperty) in g:
        return "object"
    if (p, RDF.type, OWL.DatatypeProperty) in g:
        return "data"
    if (p, RDF.type, RDF.Property) in g:
        return "rdf"
    return "unknown"


def expand_class_expression(g: Graph, expr: URIRef | BNode) -> set[URIRef]:
    """
    Returns the set of named classes that appear in a domain/range expression.
    Supports owl:unionOf lists, which your ontology uses in several domains. :contentReference[oaicite:2]{index=2}
    """
    if isinstance(expr, URIRef):
        return {expr}

    # owl:unionOf ( ... )
    union_list = next(g.objects(expr, OWL.unionOf), None)
    if union_list is not None:
        out: set[URIRef] = set()
        for item in Collection(g, union_list):
            out |= expand_class_expression(g, item)
        return out

    # otherwise unknown expression type
    return set()


def parse_datatype_range(g: Graph, node: URIRef | BNode) -> Any:
    """
    Minimal serialization for ranges that are not named URIs.
    Handles common owl:onDatatype + owl:withRestrictions pattern seen in your ontology datatypes. :contentReference[oaicite:3]{index=3}
    """
    if isinstance(node, URIRef):
        return str(node)

    on_dt = next(g.objects(node, OWL.onDatatype), None)
    with_restr = next(g.objects(node, OWL.withRestrictions), None)
    if on_dt is None and with_restr is None:
        return str(node)

    data: dict[str, Any] = {"onDatatype": as_python(on_dt), "withRestrictions": []}
    if with_restr is not None:
        for r in Collection(g, with_restr):
            # each r is usually a bnode like [ xsd:minInclusive "0"^^xsd:int ]
            r_dict = {}
            for p, o in g.predicate_objects(r):
                r_dict[as_python(p)] = as_python(o)
            data["withRestrictions"].append(r_dict)
    return data


def parse_restriction(g: Graph, rnode: BNode) -> dict[str, Any]:
    """
    Parses an owl:Restriction blank node into a dict.
    """
    out: dict[str, Any] = {"type": "restriction"}

    on_prop = next(g.objects(rnode, OWL.onProperty), None)
    out["onProperty"] = as_python(on_prop)

    # cardinalities
    for pred, key in CARD_PREDICATES:
        v = next(g.objects(rnode, pred), None)
        if v is not None:
            out["type"] = key
            out[key] = int(v) if isinstance(v, Literal) else as_python(v)

    # fillers (some/all/hasValue)
    for pred, key in FILLER_PREDICATES:
        v = next(g.objects(rnode, pred), None)
        if v is not None:
            out[key] = as_python(v)

    # qualified targets
    v = next(g.objects(rnode, OWL_ON_CLASS), None)
    if v is not None:
        out["onClass"] = as_python(v)
    v = next(g.objects(rnode, OWL_ON_DATA_RANGE), None)
    if v is not None:
        out["onDataRange"] = as_python(v)

    return out


def iter_class_restriction_nodes(g: Graph, cls: URIRef) -> Iterable[BNode]:
    """
    Finds restriction nodes from:
      - rdfs:subClassOf [ a owl:Restriction ; ... ]
      - owl:equivalentClass [ a owl:Restriction ; ... ]
      - owl:equivalentClass [ owl:intersectionOf ( ... [a owl:Restriction] ... ) ]
    """
    # subClassOf restrictions
    for o in g.objects(cls, RDFS.subClassOf):
        if isinstance(o, BNode) and (o, RDF.type, OWL.Restriction) in g:
            yield o

    # equivalentClass restrictions / intersections
    for o in g.objects(cls, OWL.equivalentClass):
        if isinstance(o, BNode) and (o, RDF.type, OWL.Restriction) in g:
            yield o
            continue

        if isinstance(o, BNode):
            inter_list = next(g.objects(o, OWL.intersectionOf), None)
            if inter_list is not None:
                for item in Collection(g, inter_list):
                    if isinstance(item, BNode) and (item, RDF.type, OWL.Restriction) in g:
                        yield item

def named_superclasses(g: Graph, cls: URIRef) -> list[str]:
    """Direct superclasses that are named classes (ignore restriction bnodes)."""
    supers: set[str] = set()
    for o in g.objects(cls, RDFS.subClassOf):
        if isinstance(o, URIRef):
            supers.add(str(o))
    return sorted(supers)


def direct_subclasses(g: Graph, cls: URIRef) -> list[str]:
    """Direct subclasses (named classes only)."""
    subs: set[str] = set()
    for s in g.subjects(RDFS.subClassOf, cls):
        if isinstance(s, URIRef):
            subs.add(str(s))
    return sorted(subs)

def turtle_to_class_dicts(ttl_path: str) -> list[dict[str, Any]]:
    g = Graph()
    g.parse(ttl_path, format="turtle")

    # Classes
    classes: set[URIRef] = set(g.subjects(RDF.type, OWL.Class)) | set(g.subjects(RDF.type, RDFS.Class))

    # Build: class -> properties whose domain includes class (including unionOf)
    domain_map: dict[URIRef, list[URIRef]] = {c: [] for c in classes}
    for p, d in g.subject_objects(RDFS.domain):
        if not isinstance(p, URIRef):
            continue
        for c in expand_class_expression(g, d):
            if c in domain_map:
                domain_map[c].append(p)

    result: list[dict[str, Any]] = []

    for c in sorted(classes, key=str):
        props_out: list[dict[str, Any]] = []

        # 1) Explicit class restrictions
        for rnode in iter_class_restriction_nodes(g, c):
            r = parse_restriction(g, rnode)
            p_iri = r.get("onProperty")
            kind = prop_kind(g, URIRef(p_iri)) if p_iri else "unknown"

            # attach range if declared
            rng = next(g.objects(URIRef(p_iri), RDFS.range), None) if p_iri else None

            props_out.append({
                "property": p_iri,
                "kind": kind,
                "range": parse_datatype_range(g, rng) if rng is not None else None,
                "restriction": r,
                "implied": None,
            })

        # 2) Domain-based properties (no explicit restriction), + implied maxCardinality=1 if FunctionalProperty
        seen = {p["property"] for p in props_out}
        for p in sorted(set(domain_map.get(c, [])), key=str):
            p_iri = str(p)
            if p_iri in seen:
                continue

            rng = next(g.objects(p, RDFS.range), None)
            implied = {"type": "maxCardinality", "maxCardinality": 1} if is_functional_property(g, p) else None

            props_out.append({
                "property": p_iri,
                "kind": prop_kind(g, p),
                "range": parse_datatype_range(g, rng) if rng is not None else None,
                "restriction": None,
                "implied": implied,
            })

        result.append({
            "class": str(c),
            "label": first_label(g, c),
            "superclasses": named_superclasses(g, c),
            "subclasses": direct_subclasses(g, c),
            "properties": props_out,
        })

    return result


if __name__ == "__main__":
    ttl_file = "dcat3.ttl"
    data = turtle_to_class_dicts(ttl_file)
    print(json.dumps(data, indent=2, ensure_ascii=False))
