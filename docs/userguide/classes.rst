.. _classes:

Define and validate a model
===========================

A ``Thing`` subclass describes the fields in your metadata. Python annotations
set their types; ``@urirefs`` maps the class and fields to RDF terms;
``@namespaces`` defines the prefixes used in those mappings.

Define a measurement
--------------------

.. testcode::

   from typing import Optional
   from pydantic import Field, ValidationError
   from ontolutils import Thing, namespaces, urirefs

   @namespaces(ex="https://example.org/vocab/")
   @urirefs(Measurement="ex:Measurement", value="ex:value", note="ex:note")
   class Measurement(Thing):
       value: float = Field(ge=0, alias="measured_value")
       note: Optional[str] = None

   measurement = Measurement(
       id="https://example.org/measurements/1",
       measured_value=1.5,
       label="Velocity magnitude",
   )
   assert measurement.value == 1.5

``value`` is required. ``Optional[str] = None`` makes ``note`` nullable and
omittable. ``Optional[str]`` without a default would still require the field.
Both ``measured_value`` and ``value`` are accepted at construction; an alias
changes the Python input name, not the RDF predicate ``ex:value``.

The example namespace is illustrative: replace it with the terms used by your
research community. Preserve the exact spelling of IRIs: ``http`` and ``https``
name different RDF resources.

Check invalid values
--------------------

Pydantic checks declared types and constraints at construction and assignment.
It may coerce compatible values, such as numeric strings, to the declared type.

.. testcode::

   try:
       measurement.value = -1
   except ValidationError as error:
       assert error.errors()[0]["loc"] == ("value",)
   else:
       raise AssertionError("Expected a validation error")
   assert measurement.value == 1.5

These checks do not enforce every rule of an ontology. Use
:doc:`SHACL <validation>` for graph-level requirements.

Labels and references
---------------------

``Thing`` already provides ``id``, ``label``, ``description``, ``comment``,
``altLabel`` (alias ``alt_label``), and several reference fields. Labels can be
plain text, language-tagged values, or lists of them:

.. testcode::

   from ontolutils import LangString
   from ontolutils.ex.prov import Person
   from ontolutils.typing import AnyIriOf

   measurement.label = [LangString(value="Velocity", lang="en"), "Geschwindigkeit@de"]

   @namespaces(ex="https://example.org/vocab/")
   @urirefs(ReviewedMeasurement="ex:ReviewedMeasurement", reviewer="ex:reviewer")
   class ReviewedMeasurement(Measurement):
       reviewer: Optional[AnyIriOf[Person]] = None

   reviewed = ReviewedMeasurement(
       value=1.5,
       reviewer=Person(id="https://example.org/people/ada", first_name="Ada"),
   )
   reviewed.reviewer = "https://example.org/people/ada"

Pass a model to include its properties in the serialized graph, or an IRI to
reference a resource described elsewhere. See :doc:`typing` for lists and
other reference types.

Add fields deliberately
-----------------------

Extra Python fields are allowed by default, but an unmapped field is not a
reliable way to add RDF. Prefer a declared field plus a ``@urirefs`` mapping.
For a one-off literal property, use ``URIValue``:

.. testcode::

   from ontolutils import URIValue

   annotated = Measurement(
       value=1.5,
       instrument_code=URIValue("LDV-01", "https://example.org/vocab/", "ex"),
   )
   assert annotated.get_jsonld_dict(resolve_keys=True)["ex:instrument_code"] == "LDV-01"

For these extra properties, use ``model_dump_jsonld()`` or
``get_jsonld_dict(resolve_keys=True)`` to retain the registered RDF key.

For classes defined from a configuration at runtime, use ``build``:

.. testcode::

   from ontolutils import Property, build

   Run = build(
       namespace="https://example.org/vocab/",
       namespace_prefix="ex",
       class_name="Run",
       properties=[Property(name="sample_count", property_type=int, default=0)],
   )
   run = Run(sample_count=3)
   assert run.sample_count == 3

``Property`` maps its name to the same local RDF name (here ``ex:sample_count``).
``Thing.add_property`` only registers an RDF mapping; it does not add a validated
Pydantic field to ``model_fields``. Define or rebuild a model when field
validation is required.
