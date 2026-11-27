Models and scientific data
==========================

Define a :doc:`Thing subclass <classes>` for the fields and validation your
application needs. Use :doc:`ontology_loader` to generate models from a Turtle
ontology and inspect their fields and RDF predicates.

Numerical arrays
----------------

Keep ordered data, coordinates and shape in array formats such as NetCDF or
HDF5, and use RDF to describe the data. Repeated RDF values have set semantics.
They cannot preserve repeated samples or sequence order.

Use the standalone ``ontolutils.arrays.to_xarray`` function to build an
xarray DataArray. Install xarray and add Pint if supplying a QUDT unit.

.. code-block:: python

   from ontolutils import QUDT_UNIT
   from ontolutils.arrays import to_xarray

   velocity = to_xarray(
       [1.0, 1.2],
       dims=["sample"],
       coords={"sample": [0, 1]},
       attrs={"long_name": "Velocity"},
       unit=QUDT_UNIT.M_PER_SEC,
   )
   assert velocity.dims == ("sample",)
   assert velocity.attrs["units"] == "m/s"

Unit conversions
----------------

Use ``ontolutils.units.to_pint(value, unit)`` for arithmetic with Pint
quantities. Pass a QUDT unit IRI or a model with that IRI as its ``id``.
For conversions based directly on QUDT coefficients, pass unit descriptions
to ``ontolutils.units.convert_value_qudt``. Each description has ``id``,
``conversionMultiplier``, ``conversionOffset`` and ``scalingOf`` attributes.
Use nested descriptions for the scaling chain. The function applies
QUDT reference coefficients and requires a shared scaling root.
