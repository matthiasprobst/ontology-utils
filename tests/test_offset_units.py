"""Absolute offsets, differences, and unknown QUDT unit errors."""
import numpy as np
import pint
import pytest

from ontolutils.ex.m4i import NumericalVariable
from ontolutils.ex.qudt.conversion import to_pint_unit


def test_absolute_celsius_and_array_conversion():
    registry = pint.UnitRegistry()
    variable = NumericalVariable(hasNumericalValue=[0., 100.], hasUnit='http://qudt.org/vocab/unit/DEG_C')
    quantity = variable.to_pint(ureg=registry)
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
