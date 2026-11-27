from functools import lru_cache
from math import isfinite
from typing import Tuple, Union, Any, Dict

import pint
import rdflib

from ontolutils.utils.qudt_units import qudt_lookup
from . import Unit

try:
    from pint import UnitRegistry
except ImportError:
    raise ImportError("pint is required for to_pint_unit function. Please install pint package.")


@lru_cache(maxsize=1)
def _get_ureg():
    return UnitRegistry(force_ndarray_like=True)


def _pick_one_scaling_of(scaling_of: Any) -> Any:
    """Require an explicitly selected scaling description."""
    if scaling_of is None:
        return None
    if isinstance(scaling_of, list):
        if len(scaling_of) > 1:
            raise ValueError('Multiple scalingOf descriptions require explicit selection')
        return scaling_of[0] if scaling_of else None
    return scaling_of


def _resolve_scaling_root(unit: Unit, max_hops: int = 50) -> Unit:
    """
    Find the scaling root of the unit.

    QUDT coefficients describe ``reference = (value + offset) * multiplier``.
    They are not successive edge weights: milligrams and grams, for example,
    both carry multipliers relative to kilograms. Traverse only to establish
    compatibility; multiplying the coefficients along the chain double counts
    the intermediate units.
    """
    current: Any = unit
    seen_ids = set()

    for _ in range(max_hops):
        if current.id in seen_ids:
            raise RuntimeError(f"Cycle detected in scalingOf chain starting at {unit.id}")
        seen_ids.add(current.id)

        parent = _pick_one_scaling_of(getattr(current, "scalingOf", None))
        if parent is None:
            return current

        if not isinstance(parent, Unit):
            raise TypeError(
                f"scalingOf is {type(parent)} not Unit. "
                f"You likely need to dereference a URI/ResourceType into a Unit object."
            )

        current = parent

    raise RuntimeError(f"scalingOf chain too long starting at {unit.id} (>{max_hops} hops)")


def _reference_affine(unit: Unit, root: Unit, other_root: Unit) -> Tuple[float, float]:
    multiplier = unit.conversionMultiplier
    offset = unit.conversionOffset
    if unit is root:
        if multiplier is None:
            multiplier = other_root.conversionMultiplier
        if offset is None:
            offset = other_root.conversionOffset
    if multiplier is None:
        if unit is not root:
            raise ValueError(f'Missing conversionMultiplier for scaled unit {unit.id}')
        multiplier = 1.0
    multiplier = float(multiplier)
    offset = float(offset) if offset is not None else 0.0
    if not isfinite(multiplier) or multiplier == 0 or not isfinite(offset):
        raise ValueError('Conversion requires a finite nonzero multiplier and finite offset')
    intercept = multiplier * offset
    if not isfinite(intercept):
        raise ValueError('Conversion offset times multiplier must be finite')
    return multiplier, intercept


def convert_value_qudt(value: Union[int, float], from_unit: Unit, to_unit: Unit) -> Union[int, float]:
    """Convert absolute values using QUDT reference multipliers and offsets.

    Both units must resolve to the same explicit scaling root. This function
    does not fetch missing descriptions or infer compatibility from dimensions.
    Temperature differences require a separate interval conversion.
    """
    if from_unit.id == to_unit.id:
        for field in ('conversionMultiplier', 'conversionOffset'):
            left, right = getattr(from_unit, field), getattr(to_unit, field)
            if left is not None and right is not None and left != right:
                raise ValueError(f'Conflicting {field} descriptions for unit {from_unit.id}')
        return value
    base_f = _resolve_scaling_root(from_unit)
    base_t = _resolve_scaling_root(to_unit)

    if base_f.id != base_t.id:
        raise ValueError(f"Incompatible units: {from_unit} -> {base_f}, {to_unit} -> {base_t}")
    for field in ('conversionMultiplier', 'conversionOffset'):
        left, right = getattr(base_f, field), getattr(base_t, field)
        if left is not None and right is not None and left != right:
            raise ValueError(f'Conflicting {field} descriptions for base unit {base_f.id}')

    m_f, b_f = _reference_affine(from_unit, base_f, base_t)
    m_t, b_t = _reference_affine(to_unit, base_t, base_f)
    v_base = m_f * float(value) + b_f
    return (v_base - b_t) / m_t


def to_pint_unit(unit: Union[Unit, str, rdflib.URIRef], ureg=None, lookup: Dict = None) -> str:
    if isinstance(unit, (str, rdflib.URIRef)):
        unit_iri = str(unit)
    else:
        unit_iri = unit.id

    # convert found_symbol into pint-compatible string
    if ureg is None:
        ureg = _get_ureg()

    found_pint_unit = None
    for k, v in qudt_lookup.items():
        if str(v) == unit_iri:
            try:
                found_pint_unit = ureg.__getattr__(k)
                break
            except pint.UndefinedUnitError:
                pass
    if found_pint_unit is None:
        for k, v in (lookup or {}).items():
            if str(v) == unit_iri:
                try:
                    found_pint_unit = ureg.__getattr__(k)
                    break
                except pint.UndefinedUnitError:
                    pass

    if found_pint_unit is None:
        raise ValueError(f"Unit {unit_iri} not found in QUDT lookup for pint conversion")

    return found_pint_unit
