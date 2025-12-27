.. _typing:

Type Hints
==========

The `ontolutils.typing` module provides specialized type hints and validators for working with RDF/IRI data in ontolutils. These types help ensure type safety when working with IRIs, URIs, and Thing instances.

Core Types
----------

IRI and ID Types
................

The module provides several annotated types for validating IRIs and IDs:

**AnyIri**
    Accepts HTTP/HTTPS URLs, blank nodes (starting with ``_:``), pydantic ``AnyUrl`` objects, ``URIRef`` or ``BNode`` instances.

**IdType** 
    Similar to ``AnyIri`` but also accepts URN and file URLs.

**NoneBlankNodeType**
    Same as ``IdType`` but explicitly rejects blank nodes.

**BlankNodeType**
    Only accepts blank node strings (must start with ``_:``).

.. code-block:: python

    from ontolutils.typing import AnyIri, IdType, NoneBlankNodeType, BlankNodeType
    from pydantic import BaseModel

    class MyModel(BaseModel):
        iri_field: AnyIri
        id_field: IdType  
        no_blank: NoneBlankNodeType
        blank_only: BlankNodeType

    # Valid usage
    model = MyModel(
        iri_field="https://example.org/resource",
        id_field="urn:uuid:1234-5678",
        no_blank="https://example.org/resource",
        blank_only="_:myblanknode"
    )

Generic Type Aliases
....................

The module provides several generic type aliases for common patterns:

**AnyThing**
    Union of a Thing instance or an IRI.

**AnyThingOf[T]**
    Union of type T, a Thing instance, or an IRI.

**AnyThingOrList**
    Union of a Thing instance, an IRI, or a list of those.

**IriList**
    An IRI or a list of IRIs.

**AnyIriOf[T]**
    Union of type T or an IRI.

**AnyIriOrListOf[T]**
    Union of an IRI, type T, or a list containing T or IRIs.

.. code-block:: python

    from ontolutils.typing import AnyThing, AnyThingOf, AnyThingOrList, IriList
    from ontolutils import Thing

    class Person(Thing):
        name: str

    class MyModel(BaseModel):
        thing_field: AnyThing  # Person instance or IRI
        person_or_iri: AnyThingOf[Person]  # Person, IRI, or Thing
        multiple: AnyThingOrList  # Single or list of Things/IRIs
        iri_list: IriList  # Single IRI or list of IRIs

Runtime Type Factories
----------------------

The module provides factory functions for creating runtime-safe type annotations that avoid unresolved TypeVars:

**make_type_or_list(*types)**
    Creates a typing object equivalent to ``Union[<types...>, AnyIri, List[Union[<types...>, AnyIri]]]``.

**make_optional_type_or_list(*types)**
    Creates an optional variant of ``make_type_or_list``.

.. code-block:: python

    from ontolutils.typing import make_type_or_list, make_optional_type_or_list

    # Create a type that accepts Person, IRIs, or lists of those
    PersonOrIriOrList = make_type_or_list(Person)

    class MyModel(BaseModel):
        person_field: PersonOrIriOrList
        optional_person: make_optional_type_or_list(Person)

    # These are all valid:
    model1 = MyModel(person_field=Person(name="John"))
    model2 = MyModel(person_field="https://example.org/person/1")  
    model3 = MyModel(person_field=[Person(name="Jane"), "https://example.org/person/2"])

Deprecated ResourceType
-----------------------

**ResourceType** is deprecated but still available for backward compatibility. It provides runtime validation for resources that can be instances of allowed types or IRIs.

.. code-block:: python

    from ontolutils.typing import ResourceType
    import warnings

    # This will emit a deprecation warning
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", DeprecationWarning)
        
        class MyModel(BaseModel):
            resource: ResourceType[Person]  # Accepts Person instances or IRIs

    # Prefer using make_type_or_list instead:
    PersonOrIri = make_type_or_list(Person)
    class BetterModel(BaseModel):
        resource: PersonOrIri

Validation Behavior
-------------------

The type validators perform the following checks:

* **IRI validation**: Accepts HTTP/HTTPS URLs, blank nodes, pydantic URL objects, URIRef, and BNode instances
* **ID validation**: Same as IRI validation plus URN and file URL schemes  
* **Blank node validation**: Ensures blank nodes start with ``_:`` prefix
* **List handling**: All validators automatically handle both single values and lists

Error messages include field names when available to help identify validation issues.

Integration with Pydantic
------------------------

All types are designed to work seamlessly with pydantic models:

* Automatic validation during model construction
* Proper serialization to JSON-LD and other formats
* Type checking support for static analysis tools
* Runtime-safe type annotations that avoid TypeVar issues

The types integrate with ontolutils' serialization system, ensuring that IRI fields are properly formatted in RDF output formats.