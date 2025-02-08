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

    from pydantic import EmailStr, Field
    from pydantic import HttpUrl, model_validator

    from ontolutils import Thing, urirefs, namespaces, as_id


    @namespaces(prov="https://www.w3.org/ns/prov#",
                foaf="https://xmlns.com/foaf/0.1/",
                m4i='http://w3id.org/nfdi4ing/metadata4ing#')
    @urirefs(Person='prov:Person',
             firstName='foaf:firstName',
             lastName='foaf:lastName',
             mbox='foaf:mbox',
             orcidId='m4i:orcidId')
    class Person(Thing):
        firstName: str
        lastName: str = Field(default=None, alias="last_name")  # you may provide an alias
        mbox: EmailStr = Field(default=None, alias="email")
        orcidId: HttpUrl = Field(default=None, alias="orcid_id")

        # the following will ensure, that if orcidId is set, it will be used as the id
        @model_validator(mode="before")
        def _change_id(self):
            return as_id(self, "orcidId")


    p = Person(id="https://orcid.org/0000-0001-8729-0482",
               firstName='Matthias', last_name='Probst')
    # as we have set an alias, we can also use "lastName":
    p = Person(id="https://orcid.org/0000-0001-8729-0482",
               firstName='Matthias', lastName='Probst')
    # The jsonld representation of the object will be the same in both cases:
    json_ld_serialization = p.model_dump_jsonld()
    # Alternatively use
    serialized_str = p.serialize(format="json-ld")

.. code-block:: json

    {
      "@context": {
        "owl": "http://www.w3.org/2002/07/owl#",
        "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
        "prov": "https://www.w3.org/ns/prov#",
        "foaf": "https://xmlns.com/foaf/0.1/",
        "m4i": "http://w3id.org/nfdi4ing/metadata4ing#"
      },
      "@id": "https://orcid.org/0000-0001-8729-0482",
      "@type": "prov:Person",
      "foaf:firstName": "Matthias",
      "foaf:lastName": "Probst"
    }


.. note::

   This project is under current development and is happy to receive ideas, code contributions as well as
   `bug and issue reports <https://github.com/matthiasprobst/ontology-utils/issues/new?title=Issue%20on%20page%20%2Findex.html&body=Your%20issue%20content%20here.>`_.
   Thank you!


.. toctree::

   installation
   userguide/index
   api