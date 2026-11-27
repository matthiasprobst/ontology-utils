"""Export numerical data and metadata to xarray."""

from .units import to_pint_unit


def to_xarray(data, *, dims=None, coords=None, attrs=None, unit=None, name=None):
    """Build a DataArray from numerical data and optional metadata.

    Supply dimension names and coordinates for ordered measurements. If a QUDT
    unit is supplied, Pint formats it into the DataArray's units attribute.
    """
    import xarray as xr

    if data is None:
        raise ValueError("Numerical data is required to create a DataArray")
    metadata = dict(attrs or {})
    if unit is not None:
        metadata["units"] = f"{to_pint_unit(unit):~f}".replace(" ", "")
    return xr.DataArray(data=data, dims=dims, coords=coords, attrs=metadata, name=name)
