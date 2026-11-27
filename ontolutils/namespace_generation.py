"""Development-time generation of RDFLib namespace modules."""

import keyword
import unicodedata

from rdflib import RDF, Graph, URIRef


def render_namespace(graph: Graph, namespace: str, class_name: str) -> str:
    """Render a strict DefinedNamespace from typed subjects in a parsed graph.

    Pass the exact term namespace, including its trailing delimiter. The output
    is sorted and independent of triple order. Terms without a safe Python
    attribute name remain available through bracket lookup.
    """
    if (not class_name.isascii() or not class_name.isidentifier()
            or class_name.startswith("_") or keyword.iskeyword(class_name)
            or class_name in {"DefinedNamespace", "Namespace", "URIRef"}):
        raise ValueError(f"Invalid namespace class name: {class_name!r}")
    if not namespace:
        raise ValueError("A term namespace is required")

    terms = sorted({
        str(subject)[len(namespace):]
        for subject in graph.subjects(RDF.type)
        if isinstance(subject, URIRef)
        and str(subject).startswith(namespace)
        and str(subject) != namespace
    })
    if not terms:
        raise ValueError(f"No typed RDF terms found in namespace {namespace!r}")

    lines = [
        '"""Generated RDF vocabulary terms."""',
        "",
        "from rdflib.namespace import DefinedNamespace, Namespace",
        "from rdflib.term import URIRef",
        "",
        "",
        f"class {class_name}(DefinedNamespace):",
        f"    _NS = Namespace({namespace!r})",
        "    _fail = True",
    ]
    reserved = {"__slots__", "_NS", "_warn", "_fail", "_extras", "_underscore_num",
                "_pytestfixturefunction", "_partialmethod"}
    if collisions := reserved.intersection(terms):
        raise ValueError(f"Terms reserved by RDFLib: {', '.join(sorted(collisions))}")
    extras = []
    for term in terms:
        if (term.isidentifier() and not term.startswith("_") and not keyword.iskeyword(term)
                and not hasattr(type, term)
                and unicodedata.normalize("NFKC", term) == term):
            lines.append(f"    {term}: URIRef")
        else:
            extras.append(f"        {term!r},")
    if extras:
        lines.extend(["    _extras = [", *extras, "    ]"])
    return "\n".join(lines) + "\n"
