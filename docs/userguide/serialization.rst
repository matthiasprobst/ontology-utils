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
graph information. It returns text by default or bytes if you pass an encoding.
With ``destination=...``, it writes to that destination using RDFLib. Use
RDFLib directly when working with datasets of named graphs.

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

Loading is a projection onto the selected model's mapped predicates. Unknown
predicates and additional source ``rdf:type`` assertions may be omitted when
the model is exported again. Retain the original RDFLib graph if all triples
must survive. This is not a lossless editor for arbitrary RDF documents.

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

Use ``Graph().parse`` as above to work with the exported triples. Prefix names,
triple order, and blank node labels can vary across serializations. Compare RDF
graphs, allowing for different blank node labels.

Find resources of a model class
-------------------------------

.. testcode::

   from ontolutils import query

   found = query(Person, data=combined, format="ttl")
   assert {item.firstName for item in found} == {"Ada", "Grace"}
   selected = Person.from_graph(graph, subject=person.id)
   assert len(selected) == 1

``query`` builds model instances; it is not a general SPARQL-string API.
``Person.from_graph`` uses the same resource-limit and return-type rules as the
other loaders. ``limit=1`` returns one complete model or ``[]``. Use
``graph.query(...)`` for arbitrary
SPARQL, or ``Person.create_query()`` to inspect the model's generated query.

``Model.from_sparql(result)`` projects SELECT rows into one model per resource.
Bind ``?id`` to an IRI or blank node and use Python field names for the other
variables. Distinct RDF terms are aggregated in first-seen order; identical
bindings are omitted, and fields declared as lists accept singleton values.
Supply ``ORDER BY`` in your query when binding order matters. This projection
does not encode an ordered RDF collection or preserve duplicate result rows.
``raise_on_error=False`` skips models failing Pydantic validation; a row without
a resource-valued ``?id`` always raises ``ValueError``.

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
for reproducible, self-contained examples. A local input file can still refer to
a remote context. For reproducible research, archive the contexts as well as the
data, record their versions and checksums, and use explicit local context paths
or inline definitions.
