Documentation
=============

**Ontolutils** is a Python package that provides a object-oriented way of working with ontologies.
Also, namespace objects are available to easily work with IRIs.
It is maintained on `GitHub <https://github.com/matthiasprobst/ontology-utils>`_ and can be installed via pip:

.. code-block:: bash

    pip install ontolutils

The package mainly depends on two libraries:

- rdflib
- pydantic


Quick example
-------------

The object oriented way of defining an ontology class which then can be used to create validated instances and
serialize them to RDF is shown below. More information can be found in the :doc:`documentation <userguide/classes>`

.. code-block:: python

    from ontolutils import Thing, urirefs, namespaces
    from pydantic import EmailStr
    from rdflib import FOAF

    @namespaces(prov="http://www.w3.org/ns/prov#",
               foaf="http://xmlns.com/foaf/0.1/")
    @urirefs(Person='prov:Person',
             firstName='foaf:firstName',
             lastName=FOAF.lastName,
             mbox='foaf:mbox')
    class Person(Thing):
        firstName: str
        lastName: str = None
        mbox: EmailStr = None

    p = Person(id="cde4c79c-21f2-4ab7-b01d-28de6e4aade4",
               firstName='John', lastName='Doe')
    p.model_dump_jsonld()

.. code-block:: json

    {
        "@context": {
            "owl": "http://www.w3.org/2002/07/owl#",
            "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
            "lastName": "http://xmlns.com/foaf/0.1/",
            "prov": "http://www.w3.org/ns/prov#",
            "foaf": "http://xmlns.com/foaf/0.1/"
        },
        "@id": "cde4c79c-21f2-4ab7-b01d-28de6e4aade4",
        "@type": "prov:Person",
        "foaf:firstName": "John",
        "lastName": "Doe"
    }


.. note::

   This project is under current development and is happy to receive ideas, code contributions as well as
   `bug and issue reports <https://github.com/matthiasprobst/ontology-utils/issues/new?title=Issue%20on%20page%20%2Findex.html&body=Your%20issue%20content%20here.>`_.
   Thank you!


.. toctree::

   installation
   userguide/index
   api