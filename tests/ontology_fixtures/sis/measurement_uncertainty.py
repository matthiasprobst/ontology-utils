from typing import Optional

from ontolutils import Thing, namespaces, urirefs
from pydantic import Field

__version__ = "0.2.1"
_NS = "https://ptb.de/sis/"


@namespaces(sis=_NS)
@urirefs(MeasurementUncertainty="sis:MeasurementUncertainty",
         hasDistribution="sis:hasDistribution"
         )
class MeasurementUncertainty(Thing):
    """A class to represent measurement uncertainty metadata."""
    hasDistribution: Optional[str] = Field(default=None, alias="has_distribution")


@namespaces(sis=_NS)
@urirefs(MeasurementUncertaintyUnivariate="sis:MeasurementUncertaintyUnivariate")
class MeasurementUncertaintyUnivariate(MeasurementUncertainty):
    """Definition of standard measurement uncertainty data."""


@namespaces(sis=_NS)
@urirefs(StandardMU="sis:StandardMU",
         hasValueStandardMU="sis:hasValueStandardMU")
class StandardMU(MeasurementUncertaintyUnivariate):
    """Definition of standard measurement uncertainty data."""
    hasValueStandardMU: Optional[float] = Field(default=None, alias="has_standard_uncertainty")


@namespaces(sis=_NS)
@urirefs(CoverageIntervalMU="sis:CoverageIntervalMU",
         hasCoverageProbability="sis:hasCoverageProbability",
         hasIntervalMax="sis:hasIntervalMax",
         hasIntervalMin="sis:hasIntervalMin",
         hasValueStandardMU="sis:hasValueStandardMU",
         )
class CoverageIntervalMU(StandardMU):
    """Coverage interval measurement uncertainty data."""
    hasCoverageProbability: Optional[float] = Field(default=None, alias="has_coverage_probability")
    hasIntervalMax: Optional[float] = Field(default=None, alias="has_interval_maximum")
    hasIntervalMin: Optional[float] = Field(default=None, alias="has_interval_minimum")
    hasValueStandardMU: Optional[float] = Field(default=None, alias="has_standard_uncertainty")


@namespaces(sis=_NS)
@urirefs(ExpandedMU="sis:ExpandedMU",
         hasCoverageFactor="sis:hasCoverageFactor",
         hasCoverageProbability="sis:hasCoverageProbability",
         hasValueExpandedMU="sis:hasValueExpandedMU"
         )
class ExpandedMU(StandardMU):
    """Definition of expanded measurement uncertainty data.

    Structure for stating an expanded measurement, model, or simulation uncertainty, e.g., to be applied to a sis:Real quantity value
    """
    hasCoverageFactor: Optional[float] = Field(default=None, alias="has_coverage_factor")
    hasCoverageProbability: Optional[float] = Field(default=None, alias="has_coverage_probability")
    hasValueExpandedMU: Optional[float] = Field(
        default=None, alias="has_expanded_measurement_uncertainty_value"
    )
