# OntoUtils

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

from ontoutils import M4I

print(M4I.Tool)
# rdflib.URIRef('http://w3id.org/nfdi4ing/metadata4ing#Tool')
```

## Ontology wrapper classes

```python

from pydantic import EmailStr

from ontoutils import Thing, namespaces, urirefs


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

```

## Limitations

Some namespaces may be incomplete due to vocabularies with names that are reserved words in Python. E.g. for
`schema.org`, "yield" or "True" will not be available like this:

```python
from ontoutils import SCHEMA

SCHEMA.yield  # AttributeError: 'SchemaOrg' object has no attribute 'yield'
```
