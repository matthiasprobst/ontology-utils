from typing import Optional

from pydantic import Field

from ontolutils import Thing, namespaces, urirefs


@namespaces(sis="https://ptb.de/sis/")
@urirefs(MeasurementUncertainty="sis:MeasurementUncertainty"
         )
class MeasurementUncertainty(Thing):
    """A class to represent measurement uncertainty metadata."""
    hasStatisticalDistribution: Optional[str] = Field(default=None, alias="has_statistical_distribution")


@namespaces(sis="https://ptb.de/sis/")
@urirefs(StandardMU="sis:StandardMU")
class StandardMU(MeasurementUncertainty):
    """Definition of standard measurement uncertainty data."""


@namespaces(sis="https://ptb.de/sis/")
@urirefs(StandardMU="sis:StandardMU",
         hasValueStandardMU="sis:hasValueStandardMU")
class StandardMU(StandardMU):
    """Definition of standard measurement uncertainty data."""
    hasValueStandardMU: Optional[float] = Field(default=None, alias="has_standard_uncertainty")


@namespaces(sis="https://ptb.de/sis/")
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


@namespaces(sis="https://ptb.de/sis/")
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
