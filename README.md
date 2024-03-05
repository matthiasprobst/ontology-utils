# Ontolutils - Utilities for work with ontologies

![Tests](https://github.com/matthiasprobst/ontology-utils/actions/workflows/tests.yml/badge.svg)
![pyvers](https://img.shields.io/badge/python-3.8%20%7C%203.9%20%7C%203.10%20%7C%203.11%20%7C%203.12-blue)

Utility library for the work with ontologies. Provides two features:

- namespaces
- ontology wrapper classes

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

## Ontology wrapper classes
With the ontology wrapper classes, you can create objects of ontology classes, write them to a JSON-LD file and query 
them again. Below, an example is made with the `prov` ontology:

```python

from pydantic import EmailStr

from ontolutils import Thing, namespaces, urirefs


@namespaces(prov="https://www.w3.org/ns/prov#",
            foaf="http://xmlns.com/foaf/0.1/")
@urirefs(Agent='prov:Agent',
         mbox='foaf:mbox')
class Agent(Thing):
    """Implementation of https://www.w3.org/ns/prov#Agent

    Parameters
    ----------
    mbox: EmailStr = None
        Email address (foaf:mbox)
    """
    mbox: EmailStr = None  # foaf:mbox


# usage:
agent = Agent(mbox="a@email.com")
print(agent.mbox)
# Agent(id=None, label=None, mbox='m@email.com')

with open("agent.json", "w") as f:
    f.write(agent.dump_jsonld())

with open("agent.json", "r") as f:
    found_agents = Agent.load_jsonld(f.read())
found_agent = found_agents[0]
print(found_agent.mbox)
# Agent(id=..., label=None, mbox='m@email.com')
```

## Limitations

Some namespaces may be incomplete due to vocabularies with names that are reserved words in Python. E.g. for
`schema.org`, "yield" or "True" will not be available like this:

```python
from ontolutils import SCHEMA

SCHEMA.yield  # AttributeError: 'SchemaOrg' object has no attribute 'yield'
```
