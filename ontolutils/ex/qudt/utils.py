from functools import lru_cache
from typing import Union

import rdflib
import requests

from ontolutils import QUDT_UNIT
from ontolutils.ex.qudt import Unit

def term_to_python(t):
    """Convert RDFLib terms to Python-native structures."""
    if isinstance(t, URIRef):
        return str(t)
    if isinstance(t, Literal):
        out = {"value": str(t)}
        if t.language:
            out["lang"] = t.language
        if t.datatype:
            out["datatype"] = str(t.datatype)
        # If it's a plain literal with no lang/datatype, return just the string
        return out if len(out) > 1 else out["value"]
    # BNodes etc.
    return str(t)


def bindings_to_kv(bindings):
    """
    bindings: iterable of dicts like {Variable('property'): URIRef(...), Variable('value'): ...}
    returns: dict[property_uri -> value or [values]]
    """
    grouped = defaultdict(list)

    for b in bindings:
        prop = b.get("property")  # RDFLib lets you access by string key too
        val = b.get("value")
        if prop is None or val is None:
            continue

        prop_key = str(prop)
        grouped[prop_key].append(term_to_python(val))

    # Collapse single-item lists
    result = {}
    for k, vals in grouped.items():
        result[k] = vals[0] if len(vals) == 1 else vals
    return result


iri2str = {str(v): k for k, v in {
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
    # acceleration
    'm/s^2': QUDT_UNIT.M_PER_SEC2,
    # velocity squared
    'm^2/s^2': QUDT_UNIT.M2_PER_SEC2,
    # dynamic viscosity
    'kg m^-1 s^-1': QUDT_UNIT.KiloGM_PER_M_SEC,
    # SI unit of dynamic viscosity
    'Pa s': QUDT_UNIT.PA_SEC,
    # kinematic viscosity
    'm^2/s': QUDT_UNIT.M2_PER_SEC,
    # area
    'm^2': QUDT_UNIT.M2,
    # volume
    'm^3': QUDT_UNIT.M3,
    # volume flow rate
    'm^3/s': QUDT_UNIT.M3_PER_SEC,
    # density
    'kg/m^3': QUDT_UNIT.KiloGM_PER_M3,
    # per length
    '1/m': QUDT_UNIT.PER_M,
    # per length squared
    '1/m^2': QUDT_UNIT.PER_M2,
    # per length cubed
    '1/m^3': QUDT_UNIT.PER_M3,
    # per second
    '1/s': QUDT_UNIT.PER_SEC,
    # per second squared
    '1/s^2': QUDT_UNIT.PER_SEC2,
    # frequency
    'Hz': QUDT_UNIT.HZ,
    # energy
    'J': QUDT_UNIT.J,
    # power
    'W': QUDT_UNIT.W,
    # pressure
    'Pa': QUDT_UNIT.PA,
    # mass
    'kg': QUDT_UNIT.KiloGM,
    # mass flow rate
    'kg/s': QUDT_UNIT.KiloGM_PER_SEC,
    # temperature
    'K': QUDT_UNIT.K,
    # torque
    'N m': QUDT_UNIT.N_M,
    # force
    'N': QUDT_UNIT.N,
    # dimensionless
    '1': QUDT_UNIT.UNITLESS,
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
    'W m-2 m-1': QUDT_UNIT.W_PER_M2_M,
    'W m-1': QUDT_UNIT.W_PER_M,
    'W m-2': QUDT_UNIT.W_PER_M2,
    'W m-3': QUDT_UNIT.W_PER_M3,
    'W m-2 sr-1': QUDT_UNIT.W_PER_M2_SR,
    'W m-2 m-1 sr-1': QUDT_UNIT.W_PER_M2_M_SR,
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
    # image pixel ("both, the smallest unit of a digital raster graphic and the display on a screen with raster control")
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
    'mol m-2 s-1 sr-1': QUDT_UNIT.MOL_PER_M2_SEC_SR,
    'mol m-2 s-1 m-1 sr-1': QUDT_UNIT.MOL_PER_M2_SEC_M_SR,
    'm year-1': QUDT_UNIT.M_PER_YR,
    'Pa m s-1': QUDT_UNIT.PA_M_PER_SEC,
    'Pa m s-2': QUDT_UNIT.PA_M_PER_SEC2,
}.items()}


@lru_cache()
def _get_qudt_unit_graph() -> rdflib.Graph:
    """Retrieve the QUDT unit ontology as an RDFLib Graph."""
    ontology_uri = "https://qudt.org/vocab/unit/"
    res = requests.get(ontology_uri)
    res.raise_for_status()
    g = rdflib.Graph()
    g.parse(data=res.text, format="turtle")
    return g


def _prepare_query(uri: Union[str, rdflib.URIRef]) -> str:
    return f"""
PREFIX qudt: <http://qudt.org/vocab/unit#>

SELECT ?property ?value WHERE {{
    <{uri}> ?property ?value .
}}"""


from collections import defaultdict
from rdflib import URIRef, Literal


def iri_to_field_name(iri: str) -> str:
    # crude but effective: split on # or /
    return iri.rsplit("#", 1)[-1].rsplit("/", 1)[-1]


def bindings_to_kv_compact_keys(bindings):
    grouped = defaultdict(list)
    for b in bindings:
        prop = b.get("property")
        val = b.get("value")
        if prop is None or val is None:
            continue
        value = term_to_python(val)
        if isinstance(val, rdflib.Literal):
            if isinstance(value, dict):
                if "lang" in value:
                    # keep lang info
                    grouped[iri_to_field_name(str(prop))].append(value)
                else:
                    # plain literal
                    if isinstance(value, dict):
                        grouped[iri_to_field_name(str(prop))].append(value["value"])
            else:
                grouped[iri_to_field_name(str(prop))].append(value)
        else:
            grouped[iri_to_field_name(str(prop))].append(value)

    return {k: (v[0] if len(v) == 1 else v) for k, v in grouped.items()}

@lru_cache()
def get_unit_by_uri(uri: Union[str, rdflib.URIRef]) -> Unit:
    """Get the string representation of a unit given its QUDT URI.

    - Downloads the ontology if not already cached.
    - Looks up the unit in a predefined mapping.
    """
    # download the ontology:
    g = _get_qudt_unit_graph()

    # perform sparql query to check if unit exists
    results = g.query(_prepare_query(uri))
    if len(results) == 0:
        raise ValueError(f"Unit URI {uri} not found in QUDT ontology")
    kv = bindings_to_kv_compact_keys(results.bindings)
    return Unit.model_validate(kv)
