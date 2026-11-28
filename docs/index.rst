Ontolutils
==========

Describe things and concepts in the world using Python. Define Python models for people, datasets, observations and scientific variables,
or generate models from an ontology. Validate fields with Pydantic and share
properties and relationships as RDF.

See :doc:`installation` to install the current checkout. Existing projects
upgrading from an earlier release can consult the :doc:`migration` guide.

Start with a person
-------------------

.. testcode::

   from pydantic import Field
   from ontolutils import Thing, namespaces, urirefs


   @namespaces(prov="http://www.w3.org/ns/prov#", foaf="http://xmlns.com/foaf/0.1/")
   @urirefs(Person="prov:Person", firstName="foaf:firstName", lastName="foaf:lastName")
   class Person(Thing):
       firstName: str = Field(alias="first_name")
       lastName: str | None = Field(default=None, alias="last_name")

   researcher = Person(
       id="https://example.org/people/ada",
       first_name="Ada",
       last_name="Lovelace",
   )
   assert researcher.firstName == "Ada"
   turtle = researcher.serialize("ttl")

``turtle`` is a string containing RDF triples, including
``<https://example.org/people/ada> a prov:Person`` and
``foaf:firstName "Ada"``. The PROV namespace is
``http://www.w3.org/ns/prov#``.

Choose your next step
---------------------

* :doc:`Install the package and optional tools <installation>`.
* :doc:`Define fields and validate metadata <userguide/classes>`.
* :doc:`Save, load, and query RDF <userguide/serialization>`.
* :doc:`Describe datasets and measurements <userguide/models>`.
* :doc:`Check graph constraints with SHACL <userguide/validation>`.

An IRI identifies a resource. For example, the dataset and the person who
created it can each have an IRI. An RDF triple can link those resources through
a named property or give one of them a literal value, such as a person's name.
JSON-LD and Turtle are two ways to write
those same triples. Ontolutils maps Python fields to their RDF property IRIs;
it does not infer an entire ontology's constraints from a class definition.

.. toctree::
   :maxdepth: 2

   installation
   userguide/index
   api
   development
   migration
   ontologies
