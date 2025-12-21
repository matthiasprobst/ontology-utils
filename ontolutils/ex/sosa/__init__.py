import warnings

from ..ssn import ObservableProperty, Actuator, Sensor, Sampler, Platform

# everything moved to ../ssn

warnings.warn("The ontolutils.ex.sosa module is deprecated and will be removed in future versions."
              " Please use ontolutils.ex.ssn instead.", DeprecationWarning, stacklevel=2)

__all__ = [
    "ObservableProperty",
    "Actuator",
    "Sensor",
    "Sampler",
    "Platform"
]
