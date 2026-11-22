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

For array values, every RDF export keeps numerical values on the original
resource. RDF properties describe unordered sets, so export does not preserve
element order, duplicates, shape or NumPy dtype. An empty value sequence has no
value triples; it cannot be distinguished from an unset value after RDF loading.
Keep scientific arrays in their data files and use RDF to describe their
metadata. When separate scalar resources are intended, create them with explicit
IDs and relationships before calling ``serialize``; export does not mint IDs.

NumPy input must contain real integers or floating-point numbers up to float64.
Complex, boolean, string, object and multidimensional arrays are rejected.
A zero-dimensional real array is normalized to a scalar.
NaN and positive/negative infinity are exported as explicit ``xsd:double``
value objects with lexical forms ``NaN``, ``INF`` and ``-INF``. These preserve
IEEE values in valid JSON-LD; they do not establish an application-level
missing-value policy or make an otherwise invalid measurement scientifically
valid. Add application constraints when nonfinite values must be rejected.

``to_pint()`` additionally requires Pint. ``to_xarray()`` additionally requires
Pint and xarray. ``has_unit="m/s"`` uses a built-in QUDT lookup, not arbitrary
unit-expression parsing. See :doc:`namespacelib`.
