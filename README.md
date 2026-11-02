# Ontolutils: validated scientific metadata in RDF

![Tests](https://github.com/matthiasprobst/ontology-utils/actions/workflows/tests.yml/badge.svg)
[![Documentation](https://readthedocs.org/projects/ontology-utils/badge/?version=latest)](https://ontology-utils.readthedocs.io/en/latest/)

Describe people, datasets, instruments, and measurements as Python objects;
validate their fields with Pydantic; export JSON-LD or Turtle with RDFLib.
Use the included ontology models or map your own fields to RDF terms.

## Install

Requires Python **3.9–3.14**, Pydantic **2.x**, and RDFLib **7.x**.

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

Python field validation checks the model's declared types and constraints.
Use SHACL for additional rules on the RDF graph; ontology conformance is not
automatically guaranteed by creating a Python object.

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

## Development

See [test instructions](tests/README.md) and [documentation build instructions](docs/README.md).
Compatibility checks must use a fresh install so installed metadata matches the
checkout. Validate model and RDF contracts before changing dependency bounds.

Keep local investigations in `.work/`. Its contents are ignored by Git and must
not be committed or force-added; accepted guidance belongs in regular docs.
