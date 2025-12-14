from typing import Tuple, Union, Any

from . import Unit


def _pick_one_scaling_of(scaling_of: Any) -> Any:
    if scaling_of is None:
        return None
    if isinstance(scaling_of, list):
        return scaling_of[0] if scaling_of else None
    return scaling_of


def _resolve_to_base_affine(unit: Unit, max_hops: int = 50) -> Tuple[Unit, float, float]:
    """
    Follow scalingOf chain and compose:
        v_base = M * v_unit + B
    """
    current: Any = unit
    M, B = 1.0, 0.0
    seen_obj_ids = set()

    for _ in range(max_hops):
        obj_id = id(current)
        if obj_id in seen_obj_ids:
            raise RuntimeError(f"Cycle detected in scalingOf chain starting at {unit}")
        seen_obj_ids.add(obj_id)

        parent = _pick_one_scaling_of(getattr(current, "scalingOf", None))
        if parent is None:
            return current, M, B

        if not isinstance(parent, Unit):
            raise TypeError(
                f"scalingOf is {type(parent)} not Unit. "
                f"You likely need to dereference a URI/ResourceType into a Unit object."
            )

        m_raw = getattr(current, "conversionMultiplier", None)
        b_raw = getattr(current, "conversionOffset", None)
        m = float(m_raw) if m_raw is not None else 1.0
        b = float(b_raw) if b_raw is not None else 0.0

        B = m * B + b
        M = m * M
        current = parent

    raise RuntimeError(f"scalingOf chain too long starting at {unit} (>{max_hops} hops)")


def convert_value_qudt(value: Union[int, float], from_unit: Unit, to_unit: Unit) -> Union[int, float]:
    if from_unit.id == to_unit.id:
        return value
    base_f, m_f, b_f = _resolve_to_base_affine(from_unit)
    base_t, m_t, b_t = _resolve_to_base_affine(to_unit)

    if base_f != base_t:
        raise ValueError(f"Incompatible units: {from_unit} -> {base_f}, {to_unit} -> {base_t}")

    v_base = m_f * float(value) + b_f
    return (v_base - b_t) / m_t
