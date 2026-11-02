API reference
=============

Use the :doc:`user guide <userguide/index>` for a workflow; use this reference
to check signatures and return values.

.. list-table::
   :header-rows: 1
   :widths: 45 55

   * - Task
     - Entry point
   * - Create a custom model
     - ``Thing``, ``namespaces``, ``urirefs``
   * - Get JSON-LD text / a dictionary
     - ``Thing.model_dump_jsonld`` / ``Thing.get_jsonld_dict``
   * - Export or combine RDF
     - ``Thing.serialize(format)`` / ``serialize(things, format)``
   * - Load JSON-LD or Turtle
     - ``Thing.from_jsonld`` / ``Thing.from_ttl`` / ``query``
   * - Work with an existing graph
     - ``Thing.from_graph`` / RDFLib's ``graph.query``
   * - Check RDF constraints
     - ``Thing.validate`` (requires ``pyshacl``)
   * - Build a class at runtime
     - ``build`` and ``Property``

Loading with ``from_jsonld``, ``from_ttl``, or ``query`` normally returns a list;
``limit=1`` returns a matching object, or ``[]`` when nothing matches.
``from_graph`` always returns a list. JSON-LD text is a string, not a dictionary.

.. toctree::
   :maxdepth: 1

   generated/ontolutils.classes.thing.Thing
   generated/ontolutils

Core model
----------

The class reference focuses on RDF operations; ordinary Pydantic methods remain
available. These method pages are generated from their signatures and docstrings:

.. autosummary::
   :toctree: generated

   ontolutils.classes.thing.Thing.from_jsonld
   ontolutils.classes.thing.Thing.get_context
   ontolutils.classes.thing.Thing.get_jsonld_dict
   ontolutils.classes.thing.Thing.model_dump_jsonld
   ontolutils.classes.thing.Thing.serialize
   ontolutils.classes.thing.Thing.from_ttl
   ontolutils.classes.thing.Thing.from_file
   ontolutils.classes.thing.Thing.from_graph
   ontolutils.classes.thing.Thing.create_query
   ontolutils.classes.thing.Thing.validate
   ontolutils.classes.thing.Thing.add_property
   ontolutils.classes.thing.Thing.iri
   ontolutils.classes.thing.Thing.namespaces
   ontolutils.classes.thing.Thing.urirefs

Helpers
-------

.. autofunction:: ontolutils.namespaces
.. autofunction:: ontolutils.urirefs
.. autofunction:: ontolutils.serialize
.. autofunction:: ontolutils.query
.. autofunction:: ontolutils.dquery
.. autofunction:: ontolutils.build
.. autoclass:: ontolutils.Property
.. autoclass:: ontolutils.LangString
.. autoclass:: ontolutils.URIValue
.. autofunction:: ontolutils.get_namespaces
.. autofunction:: ontolutils.get_urirefs
.. autofunction:: ontolutils.as_id
.. autofunction:: ontolutils.parse_unit
.. autoclass:: ontolutils.set_config
.. autofunction:: ontolutils.get_config
