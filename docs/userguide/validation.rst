Validate an RDF graph with SHACL
================================

Pydantic checks the fields declared in a Python model. SHACL checks requirements
on the RDF graph, such as a mandatory label or a property's cardinality.

Install the optional validator:

.. code-block:: console

   python -m pip install pyshacl

Check that a resource has a label
---------------------------------

.. testcode::

   from ontolutils import Thing

   shapes = """
   @prefix sh: <http://www.w3.org/ns/shacl#> .
   @prefix owl: <http://www.w3.org/2002/07/owl#> .
   @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
   @prefix ex: <https://example.org/> .
   ex:LabelShape a sh:NodeShape ;
       sh:targetClass owl:Thing ;
       sh:property [ sh:path rdfs:label ; sh:minCount 1 ] .
   """

   sample = Thing(id="https://example.org/sample", label="Sample 1")
   report = sample.validate(shacl_data=shapes)
   assert report.conforms

   missing_label = Thing(id="https://example.org/unlabelled")
   failed = missing_label.validate(shacl_data=shapes, raise_on_error=False)
   assert not failed

``validate`` returns a ``ValidationResult`` with ``conforms``, ``results_graph``,
and ``results_text``. Its truth value is ``conforms``. By default, a failed
validation raises ``ValueError``; use ``raise_on_error=False`` to inspect the
report. Shapes can also be an RDFLib graph, or a Turtle file supplied through
``shacl_source``. Supply one shapes source, not both.
