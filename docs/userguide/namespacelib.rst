Namespacelib
============

The subpackage `namespacelib` provides popular namespace objects similar to the package `rdflib`. The classes
are used as a simple way of using IRIs (Internationalized Resource Identifiers). By using the `namespacelib` subpackage,
you can avoid having to write the full IRI each time you want to use a namespace and be sure that the IRI is correct.

The `namespacelib` subpackage is a simple way to use IRIs in your code. It is not a full ontology library and does not
provide any reasoning capabilities. It is just a simple way to use IRIs in your code.

Available namespaces:

- `QUDT_UNIT`: The `QUDT <https://qudt.org/>`_ ontology for units of measure.
- `QUDT_QUANTITY`: The `QUDT <https://qudt.org/>`_ ontology for quantities.
- `M4I`: `The M4I ontology <https://nfdi4ing.pages.rwth-aachen.de/metadata4ing/metadata4ing/>`_
- `PIVMETA`: The PIVMeta `ontology for particle image velocimetry <https://matthiasprobst.github.io/pivmeta/>`_.
- `SCHEMA`: The `schema.org ontology <https://schema.org/>`_.
- `CODEMETA`: The `codemeta ontology <https://codemeta.github.io/>`_.
- `OBO`: The `Open Biological and Biomedical Ontologies <http://www.obofoundry.org/>`_.
- `IANA`: The `Internet Assigned Numbers Authority <https://www.iana.org/>`_.


Examples
--------


A popular way to describe units is to use the `QUDT` ontology. The following code shows how to use the QUDT namespace:


.. code-block:: python

    >>> from ontolutils.namespacelib import QUDT_UNIT
    >>> QUDT_UNIT.M_PER_SEC
    rdflib.term.URIRef('http://qudt.org/vocab/unit/M-PER-SEC')




Limitations
-----------

Some namespaces may be incomplete due to vocabularies with names that are reserved words in Python. E.g. the
ontology `schema.org` contains "yield" and "True", which are reserved words in Python. This means that the following
code will raise an AttributeError:

.. code-block:: python

    from ontolutils import SCHEMA

    SCHEMA.yield  # AttributeError: 'SCHEMA' object has no attribute 'yield'