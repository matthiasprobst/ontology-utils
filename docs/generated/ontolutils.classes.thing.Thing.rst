Thing
=====

.. currentmodule:: ontolutils.classes.thing

.. autoclass:: Thing

RDF operations
--------------

.. autosummary::

   ~Thing.get_jsonld_dict
   ~Thing.model_dump_jsonld
   ~Thing.serialize
   ~Thing.from_jsonld
   ~Thing.from_ttl
   ~Thing.from_file
   ~Thing.from_graph
   ~Thing.create_query
   ~Thing.validate
   ~Thing.iri
   ~Thing.get_context
   ~Thing.add_property

Ordinary Pydantic operations such as ``model_dump``, ``model_validate``, and
``model_fields`` remain available. Use the RDF methods above when predicate
mappings and JSON-LD contexts are needed. The user guide explains common
fields, labels, and references.
