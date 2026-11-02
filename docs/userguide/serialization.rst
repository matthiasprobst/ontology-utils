Save, load, and query RDF
=========================

This page continues with a built-in person model. The examples use inline
contexts and do not need to fetch an ontology from the web.

Save metadata
-------------

.. testcode::

   from pathlib import Path
   from ontolutils.ex.prov import Person

   person = Person(id="https://example.org/people/ada", first_name="Ada")
   document = person.model_dump_jsonld()
   Path("person.jsonld").write_text(document, encoding="utf-8")
   Path("person.ttl").write_text(person.serialize("ttl"), encoding="utf-8")
   assert isinstance(document, str)

``get_jsonld_dict()`` returns a dictionary instead of a JSON string.
``model_dump_json()`` is ordinary Pydantic JSON; use ``model_dump_jsonld()``
when you need RDF context and predicate mappings. Fields with ``None`` values
are omitted by default.

``serialize(format)`` supports ``"json-ld"``, ``"ttl"`` (or ``"turtle"``),
``"n3"``, ``"nt"``, and ``"xml"``. It exports one RDF graph, without named
graph information. Use RDFLib directly when working with datasets of named graphs.

Load one object or a list
-------------------------

.. testcode::

   restored = Person.from_jsonld(source="person.jsonld", limit=1)
   people = Person.from_jsonld(data=document)
   from_turtle = Person.from_ttl(source="person.ttl", limit=1)
   assert restored.firstName == from_turtle.firstName == "Ada"
   assert len(people) == 1

JSON-LD input can be a file or URL (``source``), or a string/dictionary (``data``).
Without ``limit=1``, the loader returns a list. With ``limit=1``, it returns one
matching model, or ``[]`` if none match. An IRI-only reference stays a reference;
the loader does not automatically fetch the referenced resource's description.

Combine resources and use RDFLib
--------------------------------

.. testcode::

   from rdflib import Graph, URIRef
   from ontolutils import serialize

   colleague = Person(id="https://example.org/people/grace", first_name="Grace")
   combined = serialize([person, colleague], format="ttl")
   graph = Graph().parse(data=combined, format="ttl")
   first_name = URIRef(Person.iri("firstName"))
   assert str(graph.value(URIRef(person.id), first_name)) == "Ada"

There is no ``Thing.to_graph()`` method. Parse a serialization with
``Graph().parse`` as above. Prefix names, triple order, and blank node labels may
change between serializers; compare RDF graphs rather than raw strings.

Find resources of a model class
-------------------------------

.. testcode::

   from ontolutils import query

   found = query(Person, data=combined, format="ttl")
   assert {item.firstName for item in found} == {"Ada", "Grace"}
   selected = Person.from_graph(graph, subject=person.id)
   assert len(selected) == 1

``query`` builds model instances; it is not a general SPARQL-string API.
``Person.from_graph`` also returns a list. Use ``graph.query(...)`` for arbitrary
SPARQL, or ``Person.create_query()`` to inspect the model's generated query.

Choose stable IDs
-----------------

A missing ``id`` gets a generated blank node ID, meaningful only within its
graph. Assign persistent IRIs yourself when publishing or joining metadata.
``base_uri`` can turn blank node IDs into IRIs during serialization:

.. testcode::

   from ontolutils import Thing

   local = Thing(id="_:run1", label="Run 1")
   expanded = local.get_jsonld_dict(base_uri="https://example.org/runs/")
   assert expanded["@id"] == "https://example.org/runs/run1"
   assert local.id == "_:run1"

This does not change the object's ID or guarantee a persistent identifier.
Remote JSON-LD contexts may require network access; use a dictionary context
for reproducible, self-contained examples.
