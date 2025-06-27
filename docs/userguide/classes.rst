.. _classes:

Classes
=======

This subpackage provides an object-oriented interface to work with ontologies. It is based on `pydantic` models and
`rdflib` for the serialization and deserialization of the objects.

Design a class
..............

The core class is called `Thing`. A realization of a concept of an ontology inherits from it.
For instance, a "Person" from ontology "prov" can be constructed to describe and validate a person.
The properties of a "prov:Person" are defined as attributes of the class. To refer the properties to the ontology,
the class is decorated with `@urirefs` and `@namespaces`. The former assigns the properties to the IRIs of the ontology
(e.g. `firstName='foaf:firstName'`), the latter provides the context and assigns the prefixes to the full IRI
(`prov="http://www.w3.org/ns/prov#"`).

.. code-block:: python

    from ontolutils import Thing, urirefs, namespaces
    from pydantic import EmailStr

    @namespaces(prov="http://www.w3.org/ns/prov#",
               foaf="http://xmlns.com/foaf/0.1/")
    @urirefs(Person='prov:Person',
             firstName='foaf:firstName',
             lastName='foaf:lastName',
             mbox='foaf:mbox')
    class Person(Thing):
        firstName: str
        lastName: str = None
        mbox: EmailStr = None

Note, that in the above example, `mbox` must be of type `EmailStr` (from `pydantic`), which is a string that is a valid
email address. The `firstName` is a string. The `lastName` is not required (in this example),
as it is not annotated with a default value.

Also note, that `Thing` already defines two properties, `id` and `label`.

The like this created class can be used to create an instance of a person:

.. code-block:: python

    person = Person(id='_:123uf4', label='test_person', firstName="John", mbox="john@email.com")

The advantage of creating such classes are twofold:

1. The properties (predicates of the ontology) are (type-)validated.
2. The class can be serialized to JSON-LD and back. The latter is shown next:


Add a field posterior to the class definition:
..............................................

Sometimes the definition of a "Thing", e.g. "Person", is not complete and one wants to add a field later during the
runtime. This can be done by using the `URIValue` class, which allows to define a property with a URI and a namespace:

.. code-block:: python

    from ontolutils import URIValue

    a = Person(id='_:123uf4', label='test_person', firstName="John", mbox="john@email.com", homeTown=URIValue("Berlin", "http://example.org", "ex"))


Define an ontology class dynamically:
.....................................

If you cannot define the class statically as above, you can also define it dynamically:

.. code-block:: python

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

The serialization in turtle format looks like this:

.. code-block:: turtle

    @prefix owl: <http://www.w3.org/2002/07/owl#> .
    @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
    @prefix schema: <https://schema.org/> .

    [] a schema:Event ;
        rdfs:label "my conference" ;
        schema:about [ a owl:Thing ;
                rdfs:label "The thing it is about" ] .


Dump/Serialize
..............

.. code-block:: python

    person = Person(id='_:123uf4', label='test_person', firstName="John", mbox="john@email.com")
    person.model_dump_jsonld()


The return value is a JSON-LD string:

.. code-block:: json

    {
        "@context": {
            "owl": "http://www.w3.org/2002/07/owl#",
            "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
            "prov": "http://www.w3.org/ns/prov#",
            "foaf": "http://xmlns.com/foaf/0.1/"
        },
        "@type": "prov:Person",
        "@id": "_:123uf4",
        "rdfs:label": "test_person",
        "foaf:mbox": "john@email.com",
        "firstName": "John"
    }


You may also use `model_dump_ttl()` to serialize the object to Turtle format or `serialize(...)` to serialize it to
other formats supported by `rdflib` (e.g. RDF/XML, N-Triples, etc.).


Save to file
............

The use case of the serialization is to store the object in a file or to send it over the network. Storing the data
in a file is shown next:

.. code-block:: python

    with open("person.json", "w") as f:
        f.write(person.model_dump_jsonld())


Load from file
..............

Let's load a person from a file:

.. code-block:: python

    loaded_person = Person.from_jsonld(source="person.json", limit=1)
    print(loaded_person)
    # Person(id=123uf4, label=test_person, firstName=John, mbox=john@email.com)


Conversion between semantically identical classes but different instances
.........................................................................

Sometimes two codes may implement the same ontology class, that are the same thing, meaning they have the same
URI and therefore properties. Since `pydantic` ensures the types of the properties, an option is needed to convert
between these two classes. Normally, this should not be done, but since the URI is the same, it is possible to convert between them.
For this `.map()` method is provided:

.. code-block:: python

    @namespaces(prov="http://www.w3.org/ns/prov#",
           foaf="http://xmlns.com/foaf/0.1/")
    @urirefs(PersonAlternative='prov:PersonAlternative',
             firstName='foaf:firstName',
             lastName='foaf:lastName',
             mbox='foaf:mbox')
    class PersonAlternative(Thing):
        firstName: str
        lastName: str = None
        mbox: EmailStr = None

    person_alt = PersonAlternative(label='test_person', firstName="John", mbox="e@mail.com", homeTown=URIValue("Berlin", "https://example.org", "ex"))
    person_alt.map(Person)  # map to Person class (see above)