Usage
=====

.. _installation:

Installation
------------

To use **ontolutils**, first install it using pip:

.. code-block:: console

   (.venv) $ pip install ontolutils


Things wrapper classes
----------------------

Let's explore what how to work with the package. Every concept that you want to describe inherites from a base class
called `Thing`. This class is a `pydantic` model, which means that it (among other useful features) validates the input.

Building your own classes
.........................

The package `ontolutils` provides a set of classes that are based on `pydantic` models. You can build your own
concept classes by inheriting from `ontolutils.Thing`. The attributes, that you add to your concept class are
the properties of the *Thing* you are describing.

For example, let's build a class for a `prov:Agent`. It has a `name` and an `mbox`. We need to tell the class
which `IRI` (internationalized resource identifier) it represents. This is done by adding the decorators
`@urirefs` and `@namespace` to the class. With `@namespaces`, you can explain the prefixes used. In  `@urirefs`
you assign the class name (Agent) and its properties (firstName, mbox) to the IRIs.

One important last aspect is
to provide the data type of the properties. This is done by adding the type to the attribute. In this case, `str`.
If you were to used a number for the first name during instantiation, you would get an error.

.. code-block:: python

    from ontolutils import Thing

    @ontolutils.urirefs(prov="http://www.w3.org/ns/prov#",
                        foaf="http://xmlns.com/foaf/0.1/")
    @ontolutils.namespace(Agent="prov:Agent",
                         firstName="foaf:firstName"
                         mbox="foaf:mbox")
    class Agent(Thing):
        firstName: str
        mbox: str

    my_agent = MyAgent(name="John Doe", mbox="my@email.com")

    print(my_agent)
    # MyAgent(name=John Doe, mbox=my@email.com)



Dump/Serialize
..............

What is very useful is serialization of the object. Since the class is a `pydantic` model, you can use the
`model_dump_json` method. However, this will return a JSON string. What we are interested in, is a JSON-LD string. For
this call the `model_dump_jsonld` method:

.. code-block:: python

    agent = Agent(mbox="a@email.com")
    agent.model_dump_jsonld()


    {
        "@context": {
            "owl": "http://www.w3.org/2002/07/owl#",
            "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
            "local": "http://example.org/",
            "prov": "http://www.w3.org/ns/prov#",
            "foaf": "http://xmlns.com/foaf/0.1/"
        },
        "@type": "prov:Agent",
        "foaf:mbox": "e@mail.com"
    }


Load from file
..............

Let's load an agent from a file:

.. code-block:: python3

    # usage:
    agent = Agent(mbox="a@email.com")
    # Agent(mbox=e@mail.com)

    with open("agent.json", "w") as f:
        f.write(agent.dump_jsonld())

    found_agents = Agent.from_jsonld(source="agent.json")

    found_agent = found_agents[0]
    print(found_agent.mbox)
    # Agent(mbox=e@mail.com)



Namespaces
----------


Existing namespaces
...................

You may know namespaces from `rdflib`, which implements namespaces like `PROV` or `FOAF`:

.. code-block:: python

    import rdflib

    print(rdflib.PROV.Agent)
    # rdflib.URIRef('http://www.w3.org/ns/prov#Agent')



But not all. The package `ontoutils` let's you generate namespaces from other resources. Some of them are
part of this package, like `CODEMETA` or `M4I`. Thus, you can do:

.. code-block:: python

    from ontolutils import M4I

    print(M4I.Tool)
    # rdflib.URIRef('http://w3id.org/nfdi4ing/metadata4ing#Tool')



Custom namespaces
..................

t.b.d.

Limitations
...........

Some namespaces may be incomplete due to vocabularies with names that are reserved words in Python. E.g. for
`schema.org`, "yield" or "True" will not be available like this:

.. code-block:: python

    from ontolutils import SCHEMA

    SCHEMA.yield  # AttributeError: 'SchemaOrg' object has no attribute 'yield'

