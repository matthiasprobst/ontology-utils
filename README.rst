Ontolutils - Utilities for "pythonic Things"
============================================

.. image:: https://github.com/matthiasprobst/ontology-utils/actions/workflows/tests.yml/badge.svg
    :target: https://github.com/matthiasprobst/ontology-utils/actions/workflows/tests.yml/badge.svg
    :alt: Tests Status

.. image:: https://img.shields.io/badge/python-3.8%20%7C%203.9%20%7C%203.10%20%7C%203.11%20%7C%203.12-blue
    :target: https://img.shields.io/badge/python-3.8%20%7C%203.9%20%7C%203.10%20%7C%203.11%20%7C%203.12-blue
    :alt: pyvers Status


This package helps you in generating ontology-related objects and let's you easily create JSON-LD files.

Imagine you want to describe a `prov:Agent` with an `foaf:mbox` (email address) but writing the JSON-LD file
yourself is too cumbersome. Do the following:


.. code-block:: python

    from pydantic import EmailStr

    from ontolutils import Thing, namespaces, urirefs


    @namespaces(prov="http://www.w3.org/ns/prov#",
                foaf="http://xmlns.com/foaf/0.1/")
    @urirefs(Agent='prov:Agent',
             mbox='foaf:mbox')
    class Agent(Thing):
        """Implementation of http://www.w3.org/ns/prov#Agent

        Parameters
        ----------
        mbox: EmailStr = None
            Email address (foaf:mbox)
        """
        mbox: EmailStr = None  # foaf:mbox


Now, you can instantiate the class and use the `model_dump_jsonld` method to get a JSON-LD string:

.. code-block:: python

    agent = Agent(mbox="my@email.com")
    print(agent.model_dump_jsonld())

    {
        "@context": {
            "prov": "http://www.w3.org/ns/prov#",
            "foaf": "http://xmlns.com/foaf/0.1/"
        },
        "@type": "prov:Agent",
        "foaf:mbox": "
    }



Please visit the `documentation <https://matthiasprobst.github.io/ontology-utils/>`_ for more information.


