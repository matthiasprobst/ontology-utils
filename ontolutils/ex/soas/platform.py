from typing import Union, List

from pydantic import Field

from ontolutils import Thing, urirefs, namespaces
from ontolutils.typing import ResourceType


@namespaces(soas="http://example.org/soas#")
@urirefs(Actuator='soas:Actuator')
class Actuator(Thing):
    """Actuator - A device that is used by, or implements, an (Actuation) Procedure that changes the state of the world."""
    pass


@namespaces(soas="http://example.org/soas#")
@urirefs(Sensor='soas:Sensor')
class Sensor(Thing):
    """Sensor -  Device, agent (including humans), or software (simulation) involved in, or implementing, a Procedure.
    Sensors respond to a Stimulus, e.g., a change in the environment, or Input data composed from the Results of prior
    Observations, and generate a Result. Sensors can be hosted by Platforms."""
    pass


@namespaces(soas="http://example.org/soas#")
@urirefs(Sampler='soas:Sampler')
class Sampler(Thing):
    """Sampler - A device that is used by, or implements, an (Actuation) Procedure that changes the state of the world."""


@namespaces(soas="http://example.org/soas#")
@urirefs(Platform='soas:Platform',
         hosts='soas:hosts')
class Platform(Thing):
    """Platform - A Platform is an entity that hosts other entities, particularly Sensors, Actuators, Samplers, and other Platforms."""
    hosts: Union[ResourceType, List[ResourceType]] = Field(
        default=None,
        alias="hosts",
        description="Relation between a Platform and a Sensor, Actuator, Sampler, or Platform, hosted or mounted on it."
    )
