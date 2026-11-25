# Ontolutils: Python models for scientific metadata and RDF

![Tests](https://github.com/matthiasprobst/ontology-utils/actions/workflows/tests.yml/badge.svg)
[![Documentation](https://readthedocs.org/projects/ontology-utils/badge/?version=latest)](https://ontology-utils.readthedocs.io/en/latest/)

Ontolutils helps you describe things and concepts in Python and express how they
relate to one another. For example, you can describe a dataset, the researcher
who created it, and the instrument used to collect the data. Use the built-in
models or map your own fields to ontology terms. Pydantic validates the fields,
and you can share the resulting RDF graph as JSON-LD or Turtle.

## Install

This version requires Python **3.11–3.15**, Pydantic **2.x**,
and RDFLib **7.x**. Python 3.14 requires Pydantic 2.12 or newer; Python 3.15
requires Pydantic 2.14 or newer.
Python 3.10 and earlier are not supported by this branch.

**This is unreleased 1.0 documentation.** To use the behavior described here,
install from this branch's checkout in a virtual environment:

```bash
python -m pip install .
```

To install the latest published release instead (whose API and Python support
may differ):

```bash
python -m pip install ontolutils
```

## Create, save, and reload metadata

```python
from pathlib import Path
from ontolutils.ex.prov import Person

researcher = Person(
    id="https://example.org/people/ada",
    first_name="Ada",
    last_name="Lovelace",
)
Path("researcher.jsonld").write_text(researcher.model_dump_jsonld(), encoding="utf-8")
restored = Person.from_jsonld(source="researcher.jsonld", limit=1)
assert restored.firstName == "Ada"
print(researcher.serialize("ttl"))
```

`first_name` is an input alias for `firstName`, mapped to `foaf:firstName`.
`model_dump_jsonld()` returns a **string**; `get_jsonld_dict()` returns a dictionary.
Loading normally returns a list; `limit=1` returns one matching object, or `[]`
if none match. Assign stable `id` values when sharing metadata.

Pydantic checks the model’s declared field types and constraints. Use SHACL
to check an RDF graph against a set of shapes. Scientific validity still
depends on the data and the rules you apply.

Models contain selected ontology terms. Loading projects RDF onto their mapped
fields, so unknown predicates and additional source types may be omitted on
export. Keep the source graph when all triples must survive. Numerical arrays
export as unordered RDF values; order, duplicates, shape and dtype are not
preserved. See the [1.0 migration guide](docs/migration.rst).

## Generate Python vocabulary terms

Use `render_namespace` to generate an importable RDFLib namespace for your
project. This example uses two class declarations from Metadata4Ing (M4I) so
you can run it offline.

```python
from pathlib import Path

from rdflib import Graph

from ontolutils.namespace_generation import render_namespace

namespace = "http://w3id.org/nfdi4ing/metadata4ing#"
graph = Graph().parse(
    data=f'''
        @prefix m4i: <{namespace}> .
        @prefix owl: <http://www.w3.org/2002/07/owl#> .

        m4i:NumericalVariable a owl:Class .
        m4i:ProcessingStep a owl:Class .
    ''',
    format="turtle",
)
module = render_namespace(graph, namespace, "M4I")
Path("m4i_terms.py").write_text(module, encoding="utf-8", newline="\n")

from m4i_terms import M4I

assert str(M4I.NumericalVariable) == namespace + "NumericalVariable"
```

For the full vocabulary, download the [M4I Turtle snapshot](https://w3id.org/nfdi4ing/metadata4ing/ontology.ttl)
as `m4i.ttl` and verify it against the SHA-256 recorded for your chosen
revision. The [publisher verifier](scripts/verify_publisher_namespaces.py)
records the tested M4I 1.5.0 digest. Replace the example's graph with
`Graph().parse("m4i.ttl", format="turtle")` and keep the exact M4I namespace
above. Ship `m4i_terms.py` with your package for offline imports. Define
Pydantic models and application-specific aliases in your own code.

See the [namespace guide](docs/userguide/namespacelib.rst) for file-based
generation and the [publisher snapshot checks](tests/README.md#publisher-vocabulary-snapshots)
to reproduce verification against M4I, Allotrope HDF5, SSNO, QUDT, and other
vocabularies.

## Learn by task

- [Define and validate your own model](docs/userguide/classes.rst)
- [Save, load, combine, and query RDF](docs/userguide/serialization.rst)
- [Use built-in models and numerical variables](docs/userguide/models.rst)
- [Validate RDF with SHACL](docs/userguide/validation.rst)
- [Work through the notebook](tutorials/Classes.ipynb)
- [API reference](docs/api.rst)

The example above runs with the base installation. For numerical variables,
install NumPy. Add Pint for unit conversions and xarray to create DataArrays.
Install pySHACL to validate RDF graphs against shapes. See the
[installation guide](docs/installation.rst) for the commands.

## Development

See [test instructions](tests/README.md) and [documentation build instructions](docs/README.md).
