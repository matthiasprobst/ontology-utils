.. _configuration:

Configuration
=============

You may override the default configuration of `ontolutils` dynamically using `set_config`.

You can set the prefix suffix for all blank nodes. That is, that instead of using the default `_:1234`,
you can use something like `ex:1234`. Hence, in the example, we would be using `set_config(blank_node_prefix_name="ex:")`.

You can also define the number generated for blank nodes. By default, the `rdflib.BNode().n3()` is called. However,
by using `set_config(blank_id_generator=...)` you can provide your own function that returns a string.

Consider for both settings the below example:

.. code-block:: python
    from ontolutils import Thing, urirefs, namespaces, set_config
    from pydantic import EmailStr

    @namespaces(prov="http://www.w3.org/ns/prov#",
               foaf="http://xmlns.com/foaf/0.1/")
    @urirefs(Person='prov:Person',
             firstName='foaf:firstName',
             lastName='foaf:lastName',
             mbox='foaf:mbox')
    class Person(Thing):
        firstName: str
        lastName: str = None
        mbox: EmailStr = None

    # define an ID generator:
    from itertools import count
    counter = count()
    def my_id_generator():
        return f"_:{next(counter)}"

    # set the config, stating that "ex" and the custom ID-generator must be used:
    with set_config(blank_node_prefix_name="ex:", blank_id_generator=my_id_generator):

        person = Person(label='test_person', firstName="John", mbox="e@mail.com")

        print(person)

    # returns:
    # Person(id=ex:0, label=test_person, firstName=John, mbox=e@mail.com)
