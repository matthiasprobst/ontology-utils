"""Absolute offsets, differences, and unknown QUDT unit errors."""
import numpy as np
import pint
import pytest

from ontology_fixtures.m4i import NumericalVariable
from ontolutils import QUDT_UNIT
from ontolutils.arrays import to_xarray
from ontolutils.units import to_pint, to_pint_unit


def test_absolute_celsius_and_array_conversion():
    registry = pint.UnitRegistry()
    quantity = to_pint([0., 100.], QUDT_UNIT.DEG_C, ureg=registry)
    assert quantity._REGISTRY is registry
    np.testing.assert_allclose(quantity.to('kelvin').magnitude, [273.15, 373.15])


def test_absolute_temperature_difference_is_a_delta():
    zero = NumericalVariable(hasNumericalValue=0., hasUnit='http://qudt.org/vocab/unit/DEG_C').to_pint()
    twenty = NumericalVariable(hasNumericalValue=20., hasUnit='http://qudt.org/vocab/unit/DEG_C').to_pint()
    assert (twenty - zero).to('kelvin').magnitude == pytest.approx(20.)


def test_unknown_unit_has_domain_error_and_custom_lookup_works():
    unknown = 'https://example.org/custom-unit'
    with pytest.raises(ValueError, match='not found in QUDT lookup'):
        to_pint_unit(unknown)
    assert str(to_pint_unit(unknown, lookup={'meter': unknown})) == 'meter'


def test_xarray_export_preserves_coordinates_and_formats_unit():
    pytest.importorskip("xarray")
    attrs = {"long_name": "Velocity"}
    velocity = to_xarray(
        [1.0, 1.2], dims=["sample"], coords={"sample": [0, 1]},
        attrs=attrs, unit=QUDT_UNIT.M_PER_SEC,
    )
    assert velocity.dims == ("sample",)
    assert velocity.coords["sample"].values.tolist() == [0, 1]
    assert velocity.values.tolist() == [1.0, 1.2]
    assert velocity.attrs == {"long_name": "Velocity", "units": "m/s"}
    assert attrs == {"long_name": "Velocity"}
