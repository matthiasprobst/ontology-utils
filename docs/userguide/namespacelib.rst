Namespace IRIs and units
========================

Namespace constants provide RDF term IRIs without repeatedly typing the full
URL. They do not load an entire ontology or apply reasoning.

.. testcode::

   from ontolutils import QUDT_UNIT, QUDT_KIND, SCHEMA, parse_unit

   assert str(QUDT_UNIT.M_PER_SEC) == "http://qudt.org/vocab/unit/M-PER-SEC"
   assert parse_unit("m/s") == QUDT_UNIT.M_PER_SEC
   assert str(SCHEMA.Person) == "https://schema.org/Person"

Common exports
--------------

.. list-table::
   :header-rows: 1
   :widths: 40 60

   * - Name in ``ontolutils.namespacelib``
     - Use
   * - ``QUDT_UNIT``, ``QUDT_KIND``
     - Units and quantity kinds (for example, ``M``, ``SEC``, ``Velocity``).
   * - ``SCHEMA``, ``CODEMETA``
     - Web metadata and software descriptions.
   * - ``M4I``, ``HDF5``, ``SSN_SYSTEM``
     - Scientific metadata, HDF5 structure, and SSN system terms.
   * - ``SPDX``, ``OBO``
     - Checksums and OBO terms included in the generated namespace snapshot.
   * - ``IANA``
     - Media-type lookup; registry tables may be downloaded and cached.

Use RDFLib for other namespaces, including PROV, FOAF, DCAT, and SKOS:

.. testcode::

   from rdflib import Namespace
   from rdflib.namespace import PROV, FOAF

   assert str(PROV.Person) == "http://www.w3.org/ns/prov#Person"
   laboratory = Namespace("https://example.org/vocab/")
   assert str(laboratory["yield"]) == "https://example.org/vocab/yield"

``QUDT_UNIT.M`` denotes metres and ``QUDT_UNIT.SEC`` denotes seconds;
``QUDT_UNIT.METER`` and ``QUDT_QUANTITY`` are not provided.
``parse_unit`` is an exact lookup of supported spellings, not a general unit
parser; an unknown spelling raises ``KeyError``. Use Pint for unit arithmetic.

Generated namespaces can omit terms. Unknown terms raise ``AttributeError``;
bracket syntax does not add them. For an external term absent from the snapshot,
construct an RDFLib ``Namespace`` or ``URIRef`` explicitly after checking the
ontology's exact IRI.

Generating a namespace for your project
---------------------------------------

Choose an RDF snapshot from the vocabulary publisher and record its version
and SHA-256 digest in your project. Parse the verified snapshot with RDFLib
and render the Python module as a development step. Use the exact namespace
of the terms in the graph, including its trailing delimiter.

.. code-block:: python

   from pathlib import Path

   from rdflib import Graph

   from ontolutils.namespace_generation import render_namespace

   graph = Graph().parse(Path("vocabulary.ttl"), format="turtle")
   source = render_namespace(graph, "https://example.org/vocab#", "VOCAB")
   Path("my_package/vocabulary.py").write_text(
       source, encoding="utf-8", newline="\n"
   )

Review the generated term changes when you update the snapshot. Ship the
module with your package so that imports work offline. Use bracket lookup for
terms such as ``VOCAB["M-PER-SEC"]`` when the local name is unsuitable as a Python
attribute. Keep application-specific aliases in your package.
