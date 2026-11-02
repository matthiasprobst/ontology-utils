Ontolutils
==========

Create validated scientific metadata as Python objects and exchange it as RDF.
Ontolutils combines Pydantic field validation with RDFLib serialization. It
includes models for provenance, datasets, observations, and numerical variables.

Start with a person
-------------------

.. testcode::

   from ontolutils.ex.prov import Person

   researcher = Person(
       id="https://example.org/people/ada",
       first_name="Ada",
       last_name="Lovelace",
   )
   assert researcher.firstName == "Ada"
   turtle = researcher.serialize("ttl")

``turtle`` is a string containing RDF triples, including
``<https://example.org/people/ada> a prov:Person`` and
``foaf:firstName "Ada"``. The built-in PROV namespace is
``http://www.w3.org/ns/prov#``.

Choose your next step
---------------------

* :doc:`Install the package and optional tools <installation>`.
* :doc:`Define fields and validate metadata <userguide/classes>`.
* :doc:`Save, load, and query RDF <userguide/serialization>`.
* :doc:`Describe datasets and measurements <userguide/models>`.
* :doc:`Check graph constraints with SHACL <userguide/validation>`.

An IRI is a globally named resource, such as a dataset URL. An RDF triple links
a subject, a property, and a value. JSON-LD and Turtle are two ways to write
those same triples. Ontolutils maps Python fields to their RDF property IRIs;
it does not infer an entire ontology's constraints from a class definition.

.. toctree::
   :maxdepth: 2

   installation
   userguide/index
   api
   development
