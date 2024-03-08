# Ontolutils - Utilities for work with ontologies

![Tests](https://github.com/matthiasprobst/ontology-utils/actions/workflows/tests.yml/badge.svg)
![pyvers](https://img.shields.io/badge/python-3.8%20%7C%203.9%20%7C%203.10%20%7C%203.11%20%7C%203.12-blue)

Utility library for the work with ontologies. Provides two features:

- [ontology wrapper classes](#ontology-wrapper-classes)
- [namespaces](#namespaces)

## Ontology wrapper classes

With the ontology wrapper classes, you can create objects of ontology classes, write them to a JSON-LD file and query
them again. Below, an example is made with the `prov` ontology:

```python

from pydantic import EmailStr

from ontolutils import Thing, namespaces, urirefs


@namespaces(prov="http://www.w3.org/ns/prov#",
            foaf="http://xmlns.com/foaf/0.1/")
@urirefs(Agent='prov:Agent',
         mbox='foaf:mbox')
class Agent(Thing):
    """Implementation of http://www.w3.org/ns/prov#Agent

    Parameters
    ----------
    mbox: EmailStr = None
        Email address (foaf:mbox)
    """
    mbox: EmailStr = None  # foaf:mbox

```

### Dump/Serialize

What is very useful is serialization of the object. Since the class is a `pydantic` model, you can use the
`model_dump_json` method. However, this will return a JSON string. What we are interested in, is a JSON-LD string. For
this call the `model_dump_jsonld` method:

```python
agent = Agent(mbox="a@email.com")
agent.model_dump_jsonld()
# {
#     "@context": {
#         "owl": "http://www.w3.org/2002/07/owl#",
#         "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
#         "local": "http://example.org/",
#         "prov": "http://www.w3.org/ns/prov#",
#         "foaf": "http://xmlns.com/foaf/0.1/"
#     },
#     "@type": "prov:Agent",
#     "foaf:mbox": "e@mail.com"
# }
```

## Load from file

Let's load an agent from a file:

```python

# usage:
agent = Agent(mbox="a@email.com")
# Agent(mbox=e@mail.com)

with open("agent.json", "w") as f:
    f.write(agent.dump_jsonld())

found_agents = Agent.from_jsonld(source="agent.json")

found_agent = found_agents[0]
print(found_agent.mbox)
# Agent(mbox=e@mail.com)
```

## Namespaces

You may know namespaces from `rdflib`, which implements namespaces like `PROV` or `FOAF`:

```python
import rdflib

print(rdflib.PROV.Agent)
# rdflib.URIRef('http://www.w3.org/ns/prov#Agent')
```

But not all. The package `ontoutils` let's you generate namespaces from other resources. Some of them are
part of this package, like `CODEMETA` or `M4I`. Thus, you can do:

```python

from ontolutils import M4I

print(M4I.Tool)
# rdflib.URIRef('http://w3id.org/nfdi4ing/metadata4ing#Tool')
```

## Limitations

Some namespaces may be incomplete due to vocabularies with names that are reserved words in Python. E.g. for
`schema.org`, "yield" or "True" will not be available like this:

```python
from ontolutils import SCHEMA

SCHEMA.yield  # AttributeError: 'SchemaOrg' object has no attribute 'yield'
```
