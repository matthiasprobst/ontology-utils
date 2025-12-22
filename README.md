# Ontolutils - Object-oriented "Things"

![Tests Status](https://github.com/matthiasprobst/ontology-utils/actions/workflows/tests.yml/badge.svg)
[![codecov](https://codecov.io/gh/matthiasprobst/ontology-utils/graph/badge.svg?token=KKZ3PTO73T)](https://codecov.io/gh/matthiasprobst/ontology-utils)
[![Documentation Status](https://readthedocs.org/projects/ontology-utils/badge/?version=latest)](https://ontology-utils.readthedocs.io/en/latest/)
![pyvers Status](https://img.shields.io/badge/python-3.9%20%7C%203.10%20%7C%203.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-blue)

This package helps you in generating ontology-related objects and lets you easily create JSON-LD files.

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
import rdflib
from pydantic import EmailStr, Field
from pydantic import HttpUrl, model_validator

from ontolutils import Thing, urirefs, namespaces, as_id


@namespaces(prov="https://www.w3.org/ns/prov#",
            foaf="https://xmlns.com/foaf/0.1/",
            m4i='http://w3id.org/nfdi4ing/metadata4ing#')
@urirefs(Person='prov:Person',
         firstName='foaf:firstName',
         lastName='foaf:lastName',
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


p = Person(
    id="https://orcid.org/0000-0001-8729-0482",
    label=rdflib.Literal("The creator of this package", lang="en"),
    firstName='Matthias',
    last_name='Probst'
)
# as we have set an alias, we can also use "lastName":
p = Person(
    id="https://orcid.org/0000-0001-8729-0482",
    label=rdflib.Literal("The creator of this package", lang="en"),
    firstName='Matthias',
    lastName='Probst'
)
# The jsonld representation of the object will be the same in both cases:
json_ld_serialization = p.model_dump_jsonld()
# Alternatively use
serialized_str = p.serialize(format="json-ld")  # or "ttl", "n3", "nt", "xml"
```

The result of the serialization is shown below:

```json
{
  "@context": {
    "owl": "http://www.w3.org/2002/07/owl#",
    "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
    "schema": "http://schema.org/",
    "prov": "https://www.w3.org/ns/prov#",
    "foaf": "https://xmlns.com/foaf/0.1/",
    "m4i": "http://w3id.org/nfdi4ing/metadata4ing#"
  },
  "@id": "https://orcid.org/0000-0001-8729-0482",
  "@type": "prov:Person",
  "foaf:firstName": "Matthias",
  "foaf:lastName": "Probst"
}
```

### Define an ontology class dynamically:

If you cannot define the class statically as above, you can also define it dynamically:

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
ttl = conference.serialize(format="ttl")
```

The serialization in turtle format looks like this:
```turtle
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix schema: <https://schema.org/> .

[] a schema:Event ;
    rdfs:label "my conference" ;
    schema:about [ a owl:Thing ;
            rdfs:label "The thing it is about" ] .
```

### Add a property at runtime

Say, we forgot to add the location to the above Event class. No problem, we can add it at runtime:

```python
Event.add_property(
    name="location",
    property_type=Union[Thing, List[Thing]],
    default=None,
    namespace="https://schema.org/",
    namespace_prefix="schema"
)
conference = Event(
    label="my conference",
    location=Thing(label="The location")
)
ttl = conference.serialize(format="ttl")
```

The above fives us this Turtle serialization:

```turtle
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix schema: <https://schema.org/> .

[] a schema:Event ;
    rdfs:label "my conference" ;
    schema:location [ a owl:Thing ;
            rdfs:label "The location" ] .
```


## Documentation

Please visit the [documentation](https://ontology-utils.readthedocs.io/en/latest/) for more information.


