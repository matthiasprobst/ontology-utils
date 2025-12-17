from typing import Union, List

from pydantic import Field

from ontolutils import Thing, urirefs, namespaces
from ontolutils.typing import ResourceType
from ..qudt import Unit


@namespaces(ssn="http://www.w3.org/ns/ssn/",
            schema="http://schema.org/")
@urirefs(Property="ssn:Property",
         minValue="schema:minValue",
         maxValue="schema:maxValue",
         value="schema:value",
         unitCode="schema:unitCode"
         )
class Property(Thing):
    """A quality of an entity"""
    minValue: Union[float, int] = Field(
        default=None,
        alias="min_value",
        description="The minimum value of the system property.")
    maxValue: Union[float, int] = Field(
        default=None,
        alias="max_value",
        description="The maximum value of the system property.")
    value: Union[float, int] = Field(
        default=None,
        alias="value",
        description="The value of the system property.")

    unitCode: Union[Unit, ResourceType] = Field(
        default=None,
        alias="unit_code",
        description="The unit of measurement for the property value."
    )


@namespaces(ssn_system="http://www.w3.org/ns/ssn/systems/")
@urirefs(SystemProperty="ssn_system:SystemProperty")
class SystemProperty(Property):
    """The closeness of agreement between the Result of an Observation"""


@namespaces(ssn_system="http://www.w3.org/ns/ssn/systems/")
@urirefs(MeasurementRange="ssn_system:MeasurementRange")
class MeasurementRange(SystemProperty):
    """Accuracy - The closeness of agreement between the Result of an Observation (resp. the command of an Actuation) and the true value of the observed ObservableProperty (resp. of the acted on ActuatableProperty) under the defined Conditions."""


@namespaces(ssn_system="http://www.w3.org/ns/ssn/systems/")
@urirefs(Condition="ssn_system:Condition")
class Condition(Property):
    """Condition - Used to specify ranges for qualities that act as Conditions on a Systems' operation."""


@namespaces(ssn_system="http://www.w3.org/ns/ssn/systems/",
            ssn="http://www.w3.org/ns/ssn/")
@urirefs(SystemCapability="ssn_system:SystemCapability",
         hasSystemProperty="ssn_system:hasSystemProperty",
         inCondition="ssn_system:inCondition",
forProperty="ssn:forProperty"
         )
class SystemCapability(Property):
    """Describes normal measurement, actuation, sampling properties such as accuracy, range, precision, etc. of a System under some specified Conditions such as a temperature range.
The capabilities specified here are those that affect the primary purpose of the System, while those in OperatingRange represent the system's normal operating environment, including Conditions that don't affect the Observations or the Actuations."""
    hasSystemProperty: Union[
        ResourceType, SystemProperty, List[Union[ResourceType, SystemProperty]]] = Field(
        default=None,
        alias="has_system_property",
        description="Relation between a System Capability and an Observable Property that it can observe."
    )
    inCondition: Union[
        ResourceType, Condition, List[Union[ResourceType, Condition]]] = Field(
        default=None,
        alias="in_condition",
        description="Relation between a System Capability and Conditions that apply to it."
        # example: Used for example to say that a Sensor has a particular accuracy in particular Conditions.
    )
    forProperty: Union[
        ResourceType, "ObservableProperty", List[Union[ResourceType, "ObservableProperty"]]] = Field(
        default=None,
        alias="for_property",
        description="Relation between a System Capability and an Observable Property that it can observe."
    )


@namespaces(sosa="http://www.w3.org/ns/sosa/",
            ssn_system="http://www.w3.org/ns/ssn/systems/")
@urirefs(ObservableProperty="sosa:ObservableProperty",
         isObservedBy="sosa:isObservedBy")
class ObservableProperty(Property):
    """Observable Property - An observable quality (property, characteristic) of a FeatureOfInterest."""
    isObservedBy: Union[ResourceType, "Sensor", List[Union[ResourceType, "Sensor"]]] = Field(default=None,
                                                                                             alias="is_observed_by")


@namespaces(sosa="http://www.w3.org/ns/sosa/")
@urirefs(Actuator="sosa:Actuator")
class Actuator(Thing):
    """Actuator - A device that is used by, or implements, an (Actuation) Procedure that changes the state of the world."""


@namespaces(ssn="http://www.w3.org/ns/ssn/",
            ssn_system="http://www.w3.org/ns/ssn/systems/")
@urirefs(System="ssn:System",
         hasSystemCapability="ssn_system:hasSystemCapability")
class System(Thing):
    """ System is a unit of abstraction for pieces of infrastructure that implement Procedures. A System may have components, its subsystems, which are other Systems."""
    hasSystemCapability: Union[ResourceType, SystemCapability, List[Union[ResourceType, SystemCapability]]] = Field(
        default=None,
        alias="has_system_capability",
        description="Relation between an Observable Property and a System Capability that can observe it."
    )


@namespaces(sosa="http://www.w3.org/ns/sosa/")
@urirefs(Sensor="sosa:Sensor",
         observes="sosa:observes",
         isHostedBy="sosa:isHostedBy")
class Sensor(System):
    """Sensor -  Device, agent (including humans), or software (simulation) involved in, or implementing, a Procedure.
    Sensors respond to a Stimulus, e.g., a change in the environment, or Input data composed from the Results of prior
    Observations, and generate a Result. Sensors can be hosted by Platforms."""
    observes: Union[ObservableProperty, ResourceType, List[Union[ObservableProperty, ResourceType]]]
    isHostedBy: Union[ResourceType, "Platform", List[Union[ResourceType, "Platform"]]] = Field(
        default=None,
        alias="is_hosted_by",
        description="Relation between a Sensor and a Platform that hosts or mounts it."
    )


@namespaces(sosa="http://www.w3.org/ns/sosa/")
@urirefs(Sampler="sosa:Sampler")
class Sampler(Thing):
    """Sampler - A device that is used by, or implements, an (Actuation) Procedure that changes the state of the world."""


@namespaces(sosa="http://www.w3.org/ns/sosa/")
@urirefs(Platform="sosa:Platform",
         hosts="sosa:hosts")
class Platform(Thing):
    """Platform - A Platform is an entity that hosts other entities, particularly Sensors, Actuators, Samplers, and other Platforms."""
    hosts: Union[Actuator, Sensor, Sampler, "Platform", List[Union[Actuator, Sensor, Sampler, "Platform"]]] = Field(
        default=None,
        alias="hosts",
        description="Relation between a Platform and a Sensor, Actuator, Sampler, or Platform, hosted or mounted on it."
    )


@namespaces(ssn_system="http://www.w3.org/ns/ssn/systems/")
@urirefs(Accuracy="ssn_system:Accuracy")
class Accuracy(SystemProperty):
    """The closeness of agreement between the Result of an Observation (resp. the command of an Actuation)
    and the true value of the observed ObservableProperty (resp. of the acted on ActuatableProperty) under the defined Conditions."""


ObservableProperty.model_rebuild()
Platform.model_rebuild()
