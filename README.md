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
from pydantic import EmailStr, Field
from pydantic import HttpUrl, model_validator

from ontolutils import Thing, urirefs, namespaces, as_id


@namespaces(prov="https://www.w3.org/ns/prov#",
            foaf="https://xmlns.com/foaf/0.1/",
            m4i='http://w3id.org/nfdi4ing/metadata4ing#')
@urirefs(Person='prov:Person',
         firstName='foaf:firstName',
         last_name='foaf:lastName',
         mbox='foaf:mbox',
         orcidId='m4i:orcidId')
class Person(Thing):
    firstName: str
    lastName: str = Field(default=None, alias="last_name")  # you may provide an alias
    mbox: EmailStr = Field(default=None, alias="email")
    orcidId: HttpUrl = Field(default=None, alias="orcid_id")

    # the following will ensure, that if orcidId is set, it will be used as the id
    @model_validator(mode="before")
    def _change_id(self):
        return as_id(self, "orcidId")


p = Person(id="https://orcid.org/0000-0001-8729-0482",
           firstName='Matthias', last_name='Probst')
# as we have set an alias, we can also use "lastName":
p = Person(id="https://orcid.org/0000-0001-8729-0482",
           firstName='Matthias', lastName='Probst')
# The jsonld representation of the object will be the same in both cases:
p.model_dump_jsonld()
# Alternatively use
serialized_str = p.serialize(format="ttl") # or "json-ld", "n3", "nt", "xml"
```

Now, you can instantiate the class and use the `model_dump_jsonld()` method to get a JSON-LD string:

```json
{
  "@context": {
    "owl": "https://www.w3.org/2002/07/owl#",
    "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
    "prov": "https://www.w3.org/ns/prov#",
    "foaf": "https://xmlns.com/foaf/0.1/"
  },
  "@id": "https://orcid.org/0000-0001-8729-0482",
  "@type": "prov:Person",
  "foaf:firstName": "Matthias",
  "foaf:lastName": "Probst"
}
```

### Ontolutils does not implement your Ontology class? Well, build your own:

```python
from typing import List, Union

from ontolutils import build, Property, Thing

Event = build(
    namespace="https://schema.org/",
    namespace_prefix="schema",
    class_name="Event",
    properties=[Property(
        name="about",
        default=None,
        property_type=Union[Thing, List[Thing]]
    )]
)
conference = Event(label="my conference", about=[Thing(label='The thing it is about')])
```

## Documentation

Please visit the [documentation](https://ontology-utils.readthedocs.io/en/latest/) for more information.

