# Ontolutils: Python models for scientific metadata and RDF

![Tests](https://github.com/matthiasprobst/ontology-utils/actions/workflows/tests.yml/badge.svg)
[![Documentation](https://readthedocs.org/projects/ontology-utils/badge/?version=latest)](https://ontology-utils.readthedocs.io/en/latest/)

Describe things and concepts in the world using Python, including people,
datasets, instruments, and measurements. Use ontology models to express their
properties and relationships, validate fields with Pydantic, and share their
descriptions as RDF in JSON-LD or Turtle. Start with the included models or
define your own mappings to ontology terms.

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

## Learn by task

- [Define and validate your own model](https://ontology-utils.readthedocs.io/en/latest/userguide/classes.html)
- [Save, load, combine, and query RDF](https://ontology-utils.readthedocs.io/en/latest/userguide/serialization.html)
- [Use built-in models and numerical variables](https://ontology-utils.readthedocs.io/en/latest/userguide/models.html)
- [Validate RDF with SHACL](https://ontology-utils.readthedocs.io/en/latest/userguide/validation.html)
- [Work through the notebook](tutorials/Classes.ipynb)
- [API reference](https://ontology-utils.readthedocs.io/en/latest/api.html)

The base installation supports core models and RDF serialization. Install
`numpy` for `ontolutils.ex.m4i`, `pint` for its unit conversions, `xarray` for
DataArray conversion, or `pyshacl` for RDF validation as needed.

## Units and numerical data

Numerical variables construct Pint quantities explicitly, so absolute offset
units such as Celsius convert correctly. Subtract absolute temperatures to obtain
a temperature difference; absolute offsets must not be applied to differences.
Unknown QUDT-to-Pint mappings raise `ValueError`; `to_pint_unit(..., lookup=...)`
accepts an optional custom symbol mapping.

## Development

See [test instructions](tests/README.md) and [documentation build instructions](docs/README.md).
