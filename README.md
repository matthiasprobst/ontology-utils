# Ontolutils - Object-oriented "Things"

![Tests Status](https://github.com/matthiasprobst/ontology-utils/actions/workflows/tests.yml/badge.svg)
![Coverage](https://codecov.io/gh/matthiasprobst/ontology-utils/branch/main/graph/badge.svg)
[![Documentation Status](https://readthedocs.org/projects/ontology-utils/badge/?version=latest)](https://ontology-utils.readthedocs.io/en/latest/)
![pyvers Status](https://img.shields.io/badge/python-3.8%20%7C%203.9%20%7C%203.10%20%7C%203.11%20%7C%203.12-blue)

This package helps you in generating ontology-related objects and let's you easily create JSON-LD files.

## Quickstart

### Installation

Install the package:

```bash
pip install ontolutils
```

### Usage

Imagine you want to describe a `prov:Person` with a first name, last name and an email address but writing
the JSON-LD file yourself is too cumbersome *and* you want validation of the parsed parameters. The package
lets you design classes, which describe ontology classes like this:

```python
from ontolutils import Thing, urirefs, namespaces
from pydantic import EmailStr
from rdflib import FOAF


@namespaces(prov="http://www.w3.org/ns/prov#",
            foaf="http://xmlns.com/foaf/0.1/")
@urirefs(Person='prov:Person',
         firstName='foaf:firstName',
         lastName=FOAF.lastName,
         mbox='foaf:mbox')
class Person(Thing):
    firstName: str
    lastName: str = None
    mbox: EmailStr = None


p = Person(id="local:cde4c79c-21f2-4ab7-b01d-28de6e4aade4",
           firstName='John', lastName='Doe')
p.model_dump_jsonld()
```

Now, you can instantiate the class and use the `model_dump_jsonld()` method to get a JSON-LD string:

```json
{
  "@context": {
    "owl": "http://www.w3.org/2002/07/owl#",
    "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
    "local": "http://example.org/",
    "lastName": "http://xmlns.com/foaf/0.1/",
    "prov": "http://www.w3.org/ns/prov#",
    "foaf": "http://xmlns.com/foaf/0.1/"
  },
  "@id": "local:cde4c79c-21f2-4ab7-b01d-28de6e4aade4",
  "@type": "prov:Person",
  "foaf:firstName": "John",
  "lastName": "Doe"
}
```

## Documentation

Please visit the [documentation](https://ontology-utils.readthedocs.io/en/latest/) for more information.

