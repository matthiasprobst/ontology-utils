Built-in models for research metadata
=====================================

Import a model from ``ontolutils.ex`` when its fields fit your vocabulary.
These modules implement selected terms; they are not complete implementations
of every ontology. Inspect ``Model.model_fields`` for accepted fields and
``Model.iri("fieldName")`` for their RDF predicates.

.. list-table::
   :header-rows: 1
   :widths: 25 35 40

   * - Module
     - Example classes
     - Typical use
   * - ``prov``
     - ``Person``, ``Organization``, ``Entity``, ``Activity``
     - People, data, and provenance.
   * - ``dcat``
     - ``Dataset``, ``Distribution``, ``Resource``
     - Data catalogs and downloadable resources.
   * - ``schema``
     - ``Project``, ``ResearchProject``, ``SoftwareSourceCode``
     - Research projects and software.
   * - ``m4i``
     - ``NumericalVariable``, ``TextVariable``, ``Tool``
     - Scientific variables and tools; requires NumPy.
   * - ``sosa`` / ``ssn``
     - ``Sensor``, ``Observation``, ``ObservableProperty``
     - Sensors and observations; required fields depend on the class.
   * - ``hdf5``
     - ``File``, ``Group``, ``Dataset``
     - Metadata describing HDF5 structure, not HDF5 file I/O.
   * - ``skos``, ``spdx``, ``qudt``
     - ``Concept``, ``Checksum``, ``Unit``
     - Vocabulary concepts, checksums, and units.

Record who produced a dataset
-----------------------------

.. testcode::

   from ontolutils import LangString
   from ontolutils.ex.prov import Entity, Organization, Person

   lab = Organization(id="https://example.org/lab", name=LangString(value="Flow laboratory"))
   researcher = Person(id="https://example.org/people/ada", first_name="Ada", affiliation=lab)
   dataset = Entity(
       id="https://example.org/datasets/run-01",
       label="Velocity measurements",
       was_attributed_to=researcher,
   )
   assert dataset.wasAttributedTo is researcher
   document = dataset.model_dump_jsonld()

The nested person and laboratory are included in the RDF graph. An IRI string
can be used instead when the related resource is described elsewhere.

Describe a numerical variable
-----------------------------

Install NumPy for this example: ``python -m pip install numpy``.

.. testcode::

   from ontolutils import QUDT_UNIT
   from ontolutils.ex.m4i import NumericalVariable

   velocity = NumericalVariable(
       id="https://example.org/variables/velocity",
       label="Velocity",
       has_numerical_value=[1.0, 1.2],
       has_unit="m/s",
   )
   assert str(velocity.hasUnit) == str(QUDT_UNIT.M_PER_SEC)
   assert velocity.to_numpy().tolist() == [1.0, 1.2]
   turtle = velocity.serialize("ttl")

For array values, ``NumericalVariable.serialize`` creates a scalar variable per
element, with IDs ending in ``/0``, ``/1``, etc. ``model_dump_jsonld`` instead
keeps the numerical values on the original model. Do not treat these two
representations as interchangeable array formats; keep large scientific arrays
in their data files and use RDF to describe them.

``to_pint()`` additionally requires Pint. ``to_xarray()`` additionally requires
Pint and xarray. ``has_unit="m/s"`` uses a built-in QUDT lookup, not arbitrary
unit-expression parsing. See :doc:`namespacelib`.
