from typing import Optional

import rdflib

from ontolutils import QUDT_UNIT

qudt_lookup = {
    's': QUDT_UNIT.SEC,  # time
    'm': QUDT_UNIT.M,  # length
    'mm': QUDT_UNIT.MilliM,
    'cm': QUDT_UNIT.CentiM,
    'um': QUDT_UNIT.MicroM,
    'nm': QUDT_UNIT.NanoM,
    'km': QUDT_UNIT.KiloM,
    # derived units
    # velocity
    'm/s': QUDT_UNIT.M_PER_SEC,
    'm s-1': QUDT_UNIT.M_PER_SEC,
    'm*s-1': QUDT_UNIT.M_PER_SEC,
    'm*s^-1': QUDT_UNIT.M_PER_SEC,
    'm*s**-1': QUDT_UNIT.M_PER_SEC,
    'm s**-1': QUDT_UNIT.M_PER_SEC,
    # acceleration
    'm/s2': QUDT_UNIT.M_PER_SEC2,
    'm/s^2': QUDT_UNIT.M_PER_SEC2,
    'm/s**2': QUDT_UNIT.M_PER_SEC2,
    'm s^-2': QUDT_UNIT.M_PER_SEC2,
    'm s**-2': QUDT_UNIT.M_PER_SEC2,
    'm s-2': QUDT_UNIT.M_PER_SEC2,
    # velocity squared
    'm2/s2': QUDT_UNIT.M2_PER_SEC2,
    'm^2/s^2': QUDT_UNIT.M2_PER_SEC2,
    'm^2/s': QUDT_UNIT.M2_PER_SEC2,
    'm2/s^2': QUDT_UNIT.M2_PER_SEC2,
    'm2/s**2': QUDT_UNIT.M2_PER_SEC2,
    'm2 s^-2': QUDT_UNIT.M2_PER_SEC2,
    'm2 s-2': QUDT_UNIT.M2_PER_SEC2,
    'm2 s**-2': QUDT_UNIT.M2_PER_SEC2,
    'm**2/s**2': QUDT_UNIT.M2_PER_SEC2,
    'm**2/s^2': QUDT_UNIT.M2_PER_SEC2,
    # dynamic viscosity
    'kg m^-1 s^-1': QUDT_UNIT.KiloGM_PER_M_SEC,
    # SI unit of dynamic viscosity
    'Pa s': QUDT_UNIT.PA_SEC,
    'Pa*s': QUDT_UNIT.PA_SEC,
    # kinematic viscosity
    'm2/s': QUDT_UNIT.M2_PER_SEC,
    'm2 s-1': QUDT_UNIT.M2_PER_SEC,
    'm2*s-1': QUDT_UNIT.M2_PER_SEC,
    'm**2/s': QUDT_UNIT.M2_PER_SEC,
    'm**2 s-1': QUDT_UNIT.M2_PER_SEC,
    # area
    'm2': QUDT_UNIT.M2,
    'm^2': QUDT_UNIT.M2,
    'm**2': QUDT_UNIT.M2,
    'mm2': QUDT_UNIT.MilliM2,
    'mm^2': QUDT_UNIT.MilliM2,
    'mm**2': QUDT_UNIT.MilliM2,
    # volume
    'm3': QUDT_UNIT.M3,
    'm^3': QUDT_UNIT.M3,
    'm**3': QUDT_UNIT.M3,
    'mm3': QUDT_UNIT.MilliM3,
    'mm^3': QUDT_UNIT.MilliM3,
    'mm**3': QUDT_UNIT.MilliM3,
    # volume flow rate
    'm3/s': QUDT_UNIT.M3_PER_SEC,
    'm^3/s': QUDT_UNIT.M3_PER_SEC,
    'm3 s-1': QUDT_UNIT.M3_PER_SEC,
    'm3 s^-1': QUDT_UNIT.M3_PER_SEC,
    'm^3 s-1': QUDT_UNIT.M3_PER_SEC,
    'm^3 s^-1': QUDT_UNIT.M3_PER_SEC,
    'm3*s-1': QUDT_UNIT.M3_PER_SEC,
    'm3*s^-1': QUDT_UNIT.M3_PER_SEC,
    'm3*s**-1': QUDT_UNIT.M3_PER_SEC,
    'm**3/s': QUDT_UNIT.M3_PER_SEC,
    'm**3 s-1': QUDT_UNIT.M3_PER_SEC,
    'm**3*s-1': QUDT_UNIT.M3_PER_SEC,
    'm**3 s**-1': QUDT_UNIT.M3_PER_SEC,
    # density
    'kg/m**3': QUDT_UNIT.KiloGM_PER_M3,
    'kg/m^3': QUDT_UNIT.KiloGM_PER_M3,
    'kg/m3': QUDT_UNIT.KiloGM_PER_M3,
    'kg m-3': QUDT_UNIT.KiloGM_PER_M3,
    'kg m^-3': QUDT_UNIT.KiloGM_PER_M3,
    'kg*m-3': QUDT_UNIT.KiloGM_PER_M3,
    'kg*m^-3': QUDT_UNIT.KiloGM_PER_M3,
    # per length
    '1/m': QUDT_UNIT.PER_M,
    'm-1': QUDT_UNIT.PER_M,
    'm^-1': QUDT_UNIT.PER_M,
    'm**-1': QUDT_UNIT.PER_M,
    # per length squared
    '1/m2': QUDT_UNIT.PER_M2,
    '1/m**2': QUDT_UNIT.PER_M2,
    '1/m^2': QUDT_UNIT.PER_M2,
    'm-2': QUDT_UNIT.PER_M2,
    'm^-2': QUDT_UNIT.PER_M2,
    'm**-2': QUDT_UNIT.PER_M2,
    # per length cubed
    '1/m3': QUDT_UNIT.PER_M3,
    '1/m**3': QUDT_UNIT.PER_M3,
    '1/m^3': QUDT_UNIT.PER_M3,
    'm-3': QUDT_UNIT.PER_M3,
    'm^-3': QUDT_UNIT.PER_M3,
    'm**-3': QUDT_UNIT.PER_M3,
    # per second
    '1/s': QUDT_UNIT.PER_SEC,
    '1 s-1': QUDT_UNIT.PER_SEC,
    '1*s-1': QUDT_UNIT.PER_SEC,
    '1*s^-1': QUDT_UNIT.PER_SEC,
    '1*s**-1': QUDT_UNIT.PER_SEC,
    's-1': QUDT_UNIT.PER_SEC,
    's^-1': QUDT_UNIT.PER_SEC,
    's**-1': QUDT_UNIT.PER_SEC,
    # per second squared
    '1/s**2': QUDT_UNIT.PER_SEC2,
    '1/s^2': QUDT_UNIT.PER_SEC2,
    's^-2': QUDT_UNIT.PER_SEC2,
    's-2': QUDT_UNIT.PER_SEC2,
    's**-2': QUDT_UNIT.PER_SEC2,
    # frequency
    'Hz': QUDT_UNIT.HZ,
    # energy
    'joule': QUDT_UNIT.J,
    'Joule': QUDT_UNIT.J,
    'J': QUDT_UNIT.J,
    # power
    'W': QUDT_UNIT.W,
    'watt': QUDT_UNIT.W,
    'Watt': QUDT_UNIT.W,
    # pressure
    'Pa': QUDT_UNIT.PA,
    'pascal': QUDT_UNIT.PA,
    'Pascal': QUDT_UNIT.PA,
    'kg/m/s**2': QUDT_UNIT.PA,
    # mass
    'kg': QUDT_UNIT.KiloGM,
    'kilogram': QUDT_UNIT.KiloGM,
    'kilograms': QUDT_UNIT.KiloGM,
    'Kilogram': QUDT_UNIT.KiloGM,
    'Kilograms': QUDT_UNIT.KiloGM,
    # mass flow rate
    'kg/s': QUDT_UNIT.KiloGM_PER_SEC,
    'kg s-1': QUDT_UNIT.KiloGM_PER_SEC,
    'kg*s-1': QUDT_UNIT.KiloGM_PER_SEC,
    # temperature
    'K': QUDT_UNIT.K,
    'kelvin': QUDT_UNIT.K,
    'Kelvin': QUDT_UNIT.K,
    'degree_C': QUDT_UNIT.DEG_C,
    'degree_Celsius': QUDT_UNIT.DEG_C,
    # torque
    'N m': QUDT_UNIT.N_M,
    'N*m': QUDT_UNIT.N_M,
    'kg*m**2/s**2': QUDT_UNIT.N_M,
    # radian
    'rad': QUDT_UNIT.RAD,
    # force
    'N': QUDT_UNIT.N,
    # dimensionless
    'dimensionless': QUDT_UNIT.UNITLESS,
    '': QUDT_UNIT.UNITLESS,
    ' ': QUDT_UNIT.UNITLESS,
    'None': QUDT_UNIT.UNITLESS,
    # other:
    'Pa m-1': QUDT_UNIT.PA_PER_M,
    'degree': QUDT_UNIT.DEG,
    'kg m-2': QUDT_UNIT.KiloGM_PER_M2,
    'kg m-2 s-1': QUDT_UNIT.KiloGM_PER_M2_SEC,
    'm-1 sr-1': QUDT_UNIT.PER_M_SR,
    'm-1 s': QUDT_UNIT.PER_M_SEC,
    'K m-1': QUDT_UNIT.K_PER_M,
    'year': QUDT_UNIT.YR,
    'day': QUDT_UNIT.DAY,
    'mol kg-1': QUDT_UNIT.MOL_PER_KiloGM,
    'mol m-3': QUDT_UNIT.MOL_PER_M3,
    'J kg-1': QUDT_UNIT.J_PER_KiloGM,
    'J m-2': QUDT_UNIT.J_PER_M2,
    'mol': QUDT_UNIT.MOL,
    'mol s-1': QUDT_UNIT.MOL_PER_SEC,
    'mol m-2': QUDT_UNIT.MOL_PER_M2,
    'g kg-1': QUDT_UNIT.GM_PER_KiloGM,
    'Pa m': QUDT_UNIT.PA_M,
    'K m s-1': QUDT_UNIT.K_M_PER_SEC,
    's-1 m-3': QUDT_UNIT.PER_M3_SEC,
    'dBZ': QUDT_UNIT.DeciB_Z,
    'K m2 kg-1 s-1': QUDT_UNIT.K_M2_PER_KiloGM_SEC,
    'mol m-3 s-1': QUDT_UNIT.MOL_PER_M3_SEC,
    'kg m-3 s-1': QUDT_UNIT.KiloGM_PER_M3_SEC,
    'kg degree_C m-2': QUDT_UNIT.DEG_C_KiloGM_PER_M2,
    'K m': QUDT_UNIT.K_M,
    'mol m-2 s-1': QUDT_UNIT.MOL_PER_M2_SEC,
    'mol m-2 s-1 m-1': QUDT_UNIT.MOL_PER_M2_SEC_M,
    'mol m-2 s-1 sr-1': QUDT_UNIT.MOL_PER_M2_SEC_SR,
    'W m-2 m-1': QUDT_UNIT.W_PER_M2_M,
    'W m-1': QUDT_UNIT.W_PER_M,
    'W m-2': QUDT_UNIT.W_PER_M2,
    'W m-3': QUDT_UNIT.W_PER_M3,
    'W m-2 sr-1': QUDT_UNIT.W_PER_M2_SR,
    'W m-2 m-1 sr-1': QUDT_UNIT.W_PER_M2_M_SR,
    'm3 s-2': QUDT_UNIT.M3_PER_SEC2,
    'm^3 s-2': QUDT_UNIT.M3_PER_SEC2,
    'degree m-1': QUDT_UNIT.DEG_PER_M,
    'W m-1 K-1': QUDT_UNIT.W_PER_M_K,
    'K s-1': QUDT_UNIT.K_PER_SEC,
    'Bq m-2': QUDT_UNIT.BQ_PER_M2,
    'Bq m-3': QUDT_UNIT.BQ_PER_M3,
    'Bq s m-3': QUDT_UNIT.BQ_SEC_PER_M3,
    'Pa s-1': QUDT_UNIT.PA_PER_SEC,
    'N m-2': QUDT_UNIT.N_PER_M2,
    'm s': QUDT_UNIT.M_SEC,
    'm2 s': QUDT_UNIT.M_SEC2,
    'kg s-1 m-1': QUDT_UNIT.KiloGM_PER_M_SEC,
    'dB': QUDT_UNIT.DeciB,
    'W kg-1': QUDT_UNIT.W_PER_KiloGM,
    'Pa2 s-2': QUDT_UNIT.PA2_PER_SEC2,
    'kg2 s-2': QUDT_UNIT.KiloGM2_PER_SEC2,
    'W m-2 sr-1 m-1': QUDT_UNIT.W_PER_M2_M_SR,
    # image pixel ("both, the smallest unit of a digital raster graphic as well as the display on a screen with raster control")
    'px': QUDT_UNIT.PIXEL,
    'pixel': QUDT_UNIT.PIXEL,
    '1/pixel': "https://matthiasprobst.github.io/pivmeta#PER-PIXEL",  # TODO: define this!!!
    'mm/pixel': "https://matthiasprobst.github.io/pivmeta#MilliM-PER-PIXEL",  # TODO: define this!!!
    'deg': QUDT_UNIT.DEG,
    'degC': QUDT_UNIT.DEG_C,
    'W s m-2': QUDT_UNIT.W_SEC_PER_M2,
    'N m-1': QUDT_UNIT.N_PER_M,
    'mol mol-1': QUDT_UNIT.MOL_PER_MOL,
    'm4 s-1': QUDT_UNIT.M4_PER_SEC,
    'degree s-1': QUDT_UNIT.DEG_PER_SEC,
    'K Pa s-1': QUDT_UNIT.K_PA_PER_SEC,
    'W/m2': QUDT_UNIT.W_PER_M2,
    'm2 s rad-1': QUDT_UNIT.M2_SEC_PER_RAD,
    'K s': QUDT_UNIT.K_SEC,
    'radian': QUDT_UNIT.RAD,
    'sr': QUDT_UNIT.SR,
    'sr-1': QUDT_UNIT.PER_SR,
    'dbar': QUDT_UNIT.DeciBAR,
    'mol m-2 s-1 m-1 sr-1': QUDT_UNIT.MOL_PER_M2_SEC_M_SR,
    'm year-1': QUDT_UNIT.M_PER_YR,
    'Pa m s-1': QUDT_UNIT.PA_M_PER_SEC,
    'Pa m s-2': QUDT_UNIT.PA_M_PER_SEC2
}


def parse_unit(unit_str: str) -> Optional[rdflib.URIRef]:
    """Return IRI for a unit str. E.g. 'm/s' returns QUDT_UNIT.M_PER_SEC.

    Parameters
    ----------
    unit_str: str
        Input unit string, e.g. 'm/s'

    Returns
    -------
    rdflib.URIRef
        IRI for the unit string

    Raises
    ------
    KeyError
        If the unit string is not in the lookup table
    """
    return qudt_lookup[unit_str]
