"""Verify namespace generation against digest-pinned publisher snapshots."""

import argparse
from hashlib import sha256
import json
from pathlib import Path

import requests
from rdflib import Graph, RDF, URIRef
from rdflib.plugins.shared.jsonld.context import Context

from ontolutils import namespacelib
from ontolutils.namespace_generation import render_namespace


# (export, fixture, publisher URL, SHA-256, expected term count)
SOURCES = (
    ("SSNO", "ssno.ttl", "https://matthiasprobst.github.io/ssno/2.2.0/ssno.ttl",
     "12bb1834e7acb16d97b2fbc50089e2bdb5e575ac8a2ff94b5e32fc1f8996b68e", 37),
    ("M4I", "m4i.ttl", "https://w3id.org/nfdi4ing/metadata4ing/ontology.ttl",
     "7b0e6859272e75da01c4b9b4a048b3f62be9a575afb9a47aa6947af18a4b1f76", 100),
    ("HDF5", "hdf5.ttl", "https://purl.allotrope.org/voc/adf/REC/2024/12/hdf.ttl",
     "19bfd76c3b9203bc9800eee30f23e1ad6bbfca12f871f6a8a6c237a00fd582bd", 382),
    ("QUDT_UNIT", "qudt_unit.ttl", "https://qudt.org/3.5.2/vocab/unit",
     "1578ec226340ab2b3265f8d3f10f82a585e2dc8ed66c07a86b7008ab66dd990f", 2932),
    ("QUDT_KIND", "qudt_kind.ttl", "https://qudt.org/3.5.2/vocab/quantitykind",
     "32575971bbadadb9dc397720fa0d3abaee063ace0ae44866566b9d48f88ecc73", 1224),
    ("SCHEMA", "schema.ttl", "https://schema.org/version/latest/schemaorg-current-https.ttl",
     "7f15ca89398c4f235f478a4b3b8d1f975d63c5a860b77c8a8fce01f791b7ae2f", 3023),
    ("SPDX", "spdx.xml", "https://raw.githubusercontent.com/spdx/spdx-spec/"
     "refs/heads/development/v2.2.2/ontology/spdx-ontology.owl.xml",
     "2e61b00476c6337c2b30c661e4035b85ebc815bc27b7cfc072726ce9f4a25635", 196),
    ("SSN_SYSTEM", "ssn_2017.ttl", "https://www.w3.org/ns/ssn/systems/2017/ssn-system.ttl",
     "1750d2b3bb5635261586ef49ecd43278942e84e3328b172a046011b18a11af02", 31),
    ("CODEMETA", "codemeta.jsonld", "https://raw.githubusercontent.com/codemeta/"
     "codemeta/2.0/codemeta.jsonld",
     "12e26aedb8a179b9842fd755a48cf95c7ec5223db8505d6a243f90eba9f257f3", 10),
    ("OBO", "m4i.jsonld", "https://w3id.org/nfdi4ing/metadata4ing/m4i_context.jsonld",
     "f2dc90ac61b8ad70c7c5ce12462c044984779e3aa694c88dd26b39062989f9b0", 19),
)


def read_terms(path, data, namespace, base_url):
    """Parse RDF or adapt the two publisher context term lists."""
    graph = Graph()
    if path.suffix == ".jsonld":
        context = Context(json.loads(data)["@context"])
        # These sources define term mappings in a JSON-LD context.
        # Use internal triples to carry the exact mapped IRIs into the renderer.
        terms = {
            URIRef(term.id) for term in context.terms.values()
            if term.id and not term.prefix and term.id.startswith(namespace)
            and term.id != namespace
        }
        for term in terms:
            graph.add((term, RDF.type, RDF.Property))
    else:
        rdf_format = "xml" if path.suffix == ".xml" else "turtle"
        graph.parse(data=data, format=rdf_format, publicID=base_url)
        terms = {
            subject for subject in graph.subjects(RDF.type)
            if isinstance(subject, URIRef) and str(subject).startswith(namespace)
            and subject != URIRef(namespace)
        }
    return graph, terms


def verify(folder, download):
    for name, filename, url, expected_hash, expected_count in SOURCES:
        path = folder / filename
        if download and not path.exists():
            accept = "text/turtle" if path.suffix == ".ttl" else "*/*"
            response = requests.get(url, headers={"Accept": accept}, timeout=30)
            response.raise_for_status()
            data = response.content
        else:
            data = path.read_bytes()
        if sha256(data).hexdigest() != expected_hash:
            raise ValueError(f"{filename} does not match the pinned SHA-256")
        if download and not path.exists():
            path.write_bytes(data)

        bundled = getattr(namespacelib, name, None)
        namespace = str(bundled) if bundled is not None else "https://matthiasprobst.github.io/ssno#"
        graph, expected = read_terms(path, data, namespace, url)
        source = render_namespace(graph, namespace, name)
        reversed_graph = Graph()
        for triple in reversed(list(graph)):
            reversed_graph.add(triple)
        if source != render_namespace(reversed_graph, namespace, name):
            raise ValueError(f"{name} output depends on triple order")
        module = {}
        exec(compile(source, f"{name.lower()}.py", "exec"), module)
        generated = module[name]
        term_names = [*vars(generated).get("__annotations__", {}), *generated._extras]
        actual = {generated[term] for term in term_names}
        if actual != expected or len(actual) != expected_count:
            raise ValueError(f"{name} generated terms do not match the publisher snapshot")

        print(f"{name}: {len(actual)} verified IRIs", end="")
        if bundled is not None:
            existing = {bundled[term] for term in vars(bundled).get("__annotations__", {})}
            existing.update(value for value in vars(bundled).values() if isinstance(value, URIRef))
            print(f"; {len(existing - actual)} bundled-only, {len(actual - existing)} source-only",
                  end="")
        print()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("folder", type=Path, help="Directory containing the pinned publisher snapshots")
    parser.add_argument("--download", action="store_true", help="Fetch and verify any missing snapshots")
    args = parser.parse_args()
    if args.download:
        args.folder.mkdir(parents=True, exist_ok=True)
    verify(args.folder, args.download)
