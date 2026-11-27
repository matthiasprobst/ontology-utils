Ontology sources and reproducibility
====================================

Ontolutils provides RDF model tools and curated namespace constants. Projects
can define their own ``Thing`` classes or generate them with
:doc:`userguide/ontology_loader`. Choose the ontology release you model and
record its source and checksum with your data. Keep a local Turtle snapshot
when the workflow must run offline.

A namespace constant identifies an RDF term. The associated model field,
ontology axioms and application validation have separate responsibilities.
Use :doc:`userguide/validation` for checks expressed as SHACL shapes.

Schema.org interoperability
---------------------------

Schema.org publishes HTTP and HTTPS vocabulary forms. These are distinct
RDF IRIs. Ontolutils matches the exact registered class and predicate IRIs;
it does not rewrite one form into the other. When combining data using both
forms, map the source IRIs explicitly or perform a vocabulary migration on
RDF terms. Document-wide text replacement can corrupt literal text and
unrelated resource identifiers.
