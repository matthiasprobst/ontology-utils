Ontolutils
==========

Describe things and concepts in the world using Python. Ontolutils provides
models for people, datasets, observations, and scientific variables. You can
also define your own models, validate their fields with Pydantic, and share
their properties and relationships as RDF.

This guide describes the unreleased 1.0 branch. Published packages may have
different behavior. See :doc:`installation` to install this checkout and
:doc:`migration` for changes from 0.27.

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
   migration
   ontologies
