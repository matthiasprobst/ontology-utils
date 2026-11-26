Generate models from an ontology
================================

Use ``onto.load`` to generate ``Thing`` subclasses for the named OWL and RDFS
classes declared in a Turtle document. It accepts an HTTP(S) URL or a local
path. The returned object exposes the parsed graph as ``graph`` and model
classes as attributes of ``models``. If the document declares several class
namespaces, pass the desired term namespace with ``namespace=``.

The generated classes start with the common ``Thing`` fields such as
``id`` and ``label``. The loader also discovers optional
fields from property domains, including named superclasses and OWL domain
unions and intersections. Call ``Tool.rdf_fields()`` to see Python names
and their exact predicate IRIs. Properties with several domain statements
must match each statement. Object properties accept a resource reference,
a ``Thing``, or a list of either. Other discovered fields accept literals
and explicitly typed RDF values.

Use a profile to rename or constrain a discovered field or add an explicit
mapping when the ontology omits a domain. For each profile field, supply a
Python annotation and the exact RDF predicate IRI. A
``ModelField`` is required by default. To give it a default or an alias,
pass a value or a Pydantic ``Field(...)`` as its third argument.

This example pins Metadata4Ing 1.5.0 and adds a parameter reference to the
generated ``Tool`` class.

.. code-block:: python

   from ontolutils import onto
   from ontolutils.typing import AnyIri

   m4i = "http://w3id.org/nfdi4ing/metadata4ing#"
   profile = {
       "Tool": {"parameter": onto.ModelField(m4i + "hasParameter", AnyIri)},
   }
   ontology = onto.load(
       "https://w3id.org/nfdi4ing/metadata4ing/ontology.ttl",
       expected_sha256="7b0e6859272e75da01c4b9b4a048b3f62be9a575afb9a47aa6947af18a4b1f76",
       profile=profile,
   )
   Tool = ontology.models.Tool
   tool = Tool(
       id="https://example.org/instruments/laser",
       parameter="https://example.org/parameters/power",
   )
   print(tool.serialize("ttl"))

The resulting graph contains a resource of type ``m4i:Tool`` and an
``m4i:hasParameter`` link to the power parameter IRI. Use the same
generated class to read the graph back with ``Tool.from_graph``.

For a released package, ship the verified Turtle snapshot and pass its local
path to ``onto.load`` so the package works offline. The SHA-256 check also
applies to local files. The loader uses declarations in the supplied document.
OWL imports, full reasoning, and SHACL validation are separate steps. Domain and
range statements do not specify Python field requirements or defaults. Put
those decisions in your profile and add scientific methods in a Python
subclass when your application needs them.
