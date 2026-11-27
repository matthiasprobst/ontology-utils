"""QUDT reference conversion and optional Pint integration."""

from functools import lru_cache
from math import isfinite
from typing import Any, Protocol, runtime_checkable

from ontolutils.utils.qudt_units import qudt_lookup


@runtime_checkable
class UnitDescription(Protocol):
    """Fields a project-defined unit model supplies for QUDT conversion."""

    id: str
    conversionMultiplier: float | None
    conversionOffset: float | None
    scalingOf: Any


@lru_cache(maxsize=1)
def _get_ureg():
    from pint import UnitRegistry

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


def _resolve_scaling_root(unit: UnitDescription, max_hops: int = 50) -> UnitDescription:
    """
    Find the scaling root of the unit.

    QUDT coefficients describe ``reference = (value + offset) * multiplier``.
    They are not successive edge weights: milligrams and grams, for example,
    both carry multipliers relative to kilograms. Traverse only to establish
    compatibility; multiplying the coefficients along the chain double counts
    the intermediate units.
    """
    current = unit
    seen_ids = set()

    for _ in range(max_hops):
        if current.id in seen_ids:
            raise RuntimeError(f"Cycle detected in scalingOf chain starting at {unit.id}")
        seen_ids.add(current.id)

        parent = _pick_one_scaling_of(getattr(current, "scalingOf", None))
        if parent is None:
            return current

        if not isinstance(parent, UnitDescription):
            raise TypeError(
                f"Expected a unit description for scalingOf, got {type(parent).__name__}. "
                "Resolve resource references before converting."
            )

        current = parent

    raise RuntimeError(f"scalingOf chain too long starting at {unit.id} (>{max_hops} hops)")


def _reference_affine(unit: UnitDescription, root: UnitDescription, other_root: UnitDescription) -> tuple[float, float]:
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


def convert_value_qudt(value: int | float, from_unit: UnitDescription, to_unit: UnitDescription) -> int | float:
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


def to_pint_unit(unit, ureg=None, lookup=None):
    """Resolve a QUDT unit IRI or an object with an ID to a Pint unit."""
    from pint import UndefinedUnitError

    unit_iri = str(getattr(unit, "id", unit))
    if ureg is None:
        ureg = _get_ureg()
    for units in (qudt_lookup, lookup or {}):
        for symbol, iri in units.items():
            if str(iri) == unit_iri:
                try:
                    return ureg.Unit(symbol)
                except UndefinedUnitError:
                    continue
    raise ValueError(f"Unit {unit_iri} not found in QUDT lookup for pint conversion")


def to_pint(value, unit, ureg=None, lookup=None):
    """Create a Pint Quantity from a value and a QUDT unit."""
    if value is None or unit is None:
        raise ValueError("A value and unit are required for Pint conversion")
    pint_unit = to_pint_unit(unit, ureg=ureg, lookup=lookup)
    return pint_unit._REGISTRY.Quantity(value, pint_unit)
