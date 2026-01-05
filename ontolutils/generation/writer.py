from __future__ import annotations
from typing import Any, Dict, Tuple

import rdflib


def to_string(
    cls: Dict[str, Any],
    *,
    prefix_map: Dict[str, str] | None = None,   # baseIRI -> prefix
    namespace_value_for_prefix: Dict[str, str] | None = None,  # prefix -> decorator value
) -> str:
    """
    Convert a class dictionary into a Python class definition string.

    No file I/O. Pure string generation.
    """

    prefix_map = dict(prefix_map or {})
    namespace_value_for_prefix = dict(namespace_value_for_prefix or {})

    def split_iri(iri: str) -> Tuple[str, str]:
        if "#" in iri:
            base, local = iri.rsplit("#", 1)
            return base + "#", local
        base, local = iri.rsplit("/", 1)
        return base + "/", local

    def local_name(iri: str) -> str:
        return split_iri(iri)[1]

    auto_prefix_counter = 0

    def prefix_for_base(base: str) -> str:
        nonlocal auto_prefix_counter
        if base in prefix_map:
            return prefix_map[base]
        pfx = f"ns{auto_prefix_counter}"
        auto_prefix_counter += 1
        prefix_map[base] = pfx
        return pfx

    def qname(iri: str) -> str:
        base, local = split_iri(iri)
        return f"{prefix_for_base(base)}:{local}"

    # ---- class & inheritance ----
    class_iri = cls["class"]
    class_name = local_name(class_iri)

    supers = cls.get("superclasses") or []
    base_class = local_name(supers[0]) if supers else "object"

    # ---- URIs used ----
    urirefs: Dict[str, str] = {class_name: qname(class_iri)}

    for p in cls.get("properties", []):
        iri = p.get("property")
        if iri:
            urirefs[local_name(iri)] = qname(iri)

    # ---- namespaces ----
    used_prefixes = {v.split(":", 1)[0] for v in urirefs.values()}
    namespaces: Dict[str, str] = {}

    for base, pfx in prefix_map.items():
        if pfx in used_prefixes:
            namespaces[pfx] = namespace_value_for_prefix.get(pfx, base)

    # ---- typing helpers ----
    def is_single(prop: Dict[str, Any]) -> bool:
        r = prop.get("restriction") or prop.get("implied")
        if not r:
            return False
        if r.get("type") == "cardinality" and r.get("cardinality") == 1:
            return True
        if r.get("type") == "maxCardinality" and r.get("maxCardinality") == 1:
            return True
        if r.get("type") == "qualifiedCardinality" and r.get("qualifiedCardinality") == 1:
            return True
        return False

    def py_type(prop: Dict[str, Any]) -> str:
        range = prop['range']
        if range.startswith("http"):
            range_uri = rdflib.URIRef(range)
            range = rdflib.namespace.split_uri(range_uri)[1]
        return f"Optional[AnyIriOf[{range}]" if is_single(prop) else f"Optional[AnyIriOrList[{range}]"

    # ---- generate source ----
    lines: list[str] = []

    lines.append("@namespaces(")
    for pfx, val in sorted(namespaces.items()):
        if val == "_NS":
            lines.append(f"    {pfx}=_NS,")
        else:
            lines.append(f"    {pfx}={val!r},")
    lines.append(")")

    lines.append("@urirefs(")
    for k, v in urirefs.items():
        lines.append(f"    {k}='{v}',")
    lines.append(")")

    lines.append(f"class {class_name}({base_class}):")

    label = cls.get("label")
    if label:
        lines.append(f'    """{label}."""')

    for prop in cls.get("properties", []):
        iri = prop.get("property")
        if not iri:
            continue
        name = local_name(iri)
        lines.append(f"    {name}: {py_type(prop)} = None  # {qname(iri)}")

    return "\n".join(lines) + "\n"
