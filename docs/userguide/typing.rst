.. _typing:

Types, references, and optional fields
======================================

Use ordinary Python types for literal values and a model type for nested
metadata. Use the helpers in ``ontolutils.typing`` when a field can contain
either an object or its IRI.

.. testcode::

   from typing import Optional
   from pydantic import Field
   from ontolutils import Thing, namespaces, urirefs
   from ontolutils.typing import AnyIriOf, AnyIriOrListOf


   @namespaces(prov="http://www.w3.org/ns/prov#", foaf="http://xmlns.com/foaf/0.1/")
   @urirefs(Person="prov:Person", firstName="foaf:firstName", lastName="foaf:lastName")
   class Person(Thing):
       firstName: str = Field(alias="first_name")
       lastName: str | None = Field(default=None, alias="last_name")

   @namespaces(ex="https://example.org/vocab/")
   @urirefs(Review="ex:Review", lead="ex:lead", contributors="ex:contributors")
   class Review(Thing):
       lead: Optional[AnyIriOf[Person]] = None
       contributors: Optional[AnyIriOrListOf[Person]] = None

   review = Review(
       lead=Person(first_name="Ada"),
       contributors=["https://example.org/people/grace", Person(first_name="Katherine")],
   )
   assert isinstance(review.lead, Person)

Choose a helper
---------------

.. list-table::
   :header-rows: 1
   :widths: 40 60

   * - Type
     - Intended use
   * - ``AnyIri``
     - A reference supplied as HTTP(S) text, ``_:`` blank-node text, a Pydantic
       URL, or an RDFLib ``URIRef``/``BNode``.
   * - ``IdType``
     - ``Thing.id`` validation, including URN and file URL strings.
   * - ``AnyIriOf[T]``
     - A model of type ``T`` or an IRI reference.
   * - ``AnyIriOrListOf[T]``
     - ``T``/IRI values, singly or in a list.
   * - ``AnyThing``, ``AnyThingOrList``
     - Any ``Thing`` subclass or IRI; the latter also allows lists of models.
   * - ``AnyThingOf[T]``
     - ``T``, any ``Thing``, or an IRI; broader than ``AnyIriOf[T]``.
   * - ``IriList``
     - IRI references, singly or in a list.
   * - ``BlankNodeType``
     - A string starting with ``_:``.

These helpers are permissive: ``AnyIri`` itself also accepts lists of reference
values, and a plain ``URIRef`` is not checked for a specific URL scheme. Use
your own Pydantic validator when you need stricter cardinality or IRI rules.
Validated IRI references compare as strings and serialize as JSON-LD ``@id``
objects. Ordinary ``str`` values are literals, including URL-looking text and
compact-IRI-looking text. In a field accepting both text and IRIs, use an
explicit RDFLib ``URIRef`` or a Pydantic URL object to request a reference.
RDFLib ``Literal`` objects cannot be passed to an IRI-only field.
During RDF loading, fields accepting only IRI/URL references keep the target's
identifier even if that target has a description in the source graph. A field
that also accepts a model can load its mapped metadata. Lists of references
still support finite RDF collections, preserving member order and duplicates
when loading. Reference-only projection omits the target's description from
subsequent model export; retain the source graph when it must survive.
``NoneBlankNodeType`` is an ID type that rejects ``_:`` strings and RDFLib
``BNode`` objects when a named resource is required.

Nullable does not mean omittable
--------------------------------

``Optional[T]`` allows ``None``. Add ``= None`` if callers may omit the field.
The same applies to the runtime helper ``make_optional_type_or_list``:

.. testcode::

   from pydantic import BaseModel
   from ontolutils.typing import make_optional_type_or_list, make_type_or_list

   class Contributors(BaseModel):
       people: make_type_or_list(Person)
       contact: make_optional_type_or_list(Person) = None

   contributors = Contributors(people=[Person(first_name="Ada")])
   assert contributors.contact is None

Pass concrete types to these factories. The older ``ResourceType`` helper is
deprecated; use ``AnyIriOrListOf[Person]`` or ``make_type_or_list(Person)`` in
new models.
