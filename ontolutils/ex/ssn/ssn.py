from typing import Union, List, Optional, Tuple

from pydantic import Field

from ontolutils import Thing, urirefs, namespaces
from ontolutils.typing import AnyIriOf, AnyThing
from .. import qudt
from ..m4i import NumericalVariable
from ..qudt import Unit

__version__ = "2017.10.19"


@namespaces(ssn="http://www.w3.org/ns/ssn/",
            schema="https://schema.org/")
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

    unitCode: Optional[AnyIriOf[Unit]] = Field(
        default=None,
        alias="unit_code",
        description="The unit of measurement for the property value."
    )


@namespaces(ssn_system="http://www.w3.org/ns/ssn/systems/")
@urirefs(SystemProperty="ssn_system:SystemProperty")
class SystemProperty(Property):
    """The closeness of agreement between the Result of an Observation"""


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
        AnyThing, SystemProperty, List[Union[AnyThing, SystemProperty]]] = Field(
        default=None,
        alias="has_system_property",
        description="Relation between a System Capability and an Observable Property that it can observe."
    )
    inCondition: Union[
        AnyThing, Condition, List[Union[AnyThing, Condition]]] = Field(
        default=None,
        alias="in_condition",
        description="Relation between a System Capability and Conditions that apply to it."
        # example: Used for example to say that a Sensor has a particular accuracy in particular Conditions.
    )
    forProperty: Union[
        AnyThing, "ObservableProperty", List[Union[AnyThing, "ObservableProperty"]]] = Field(
        default=None,
        alias="for_property",
        description="Relation between a System Capability and an Observable Property that it can observe."
    )


@namespaces(ssn="http://www.w3.org/ns/ssn/",
            ssn_system="http://www.w3.org/ns/ssn/systems/")
@urirefs(System="ssn:System",
         hasSystemCapability="ssn_system:hasSystemCapability")
class System(Thing):
    """ System is a unit of abstraction for pieces of infrastructure that implement Procedures. A System may have components, its subsystems, which are other Systems."""
    hasSystemCapability: Union[AnyThing, SystemCapability, List[Union[AnyThing, SystemCapability]]] = Field(
        default=None,
        alias="has_system_capability",
        description="Relation between an Observable Property and a System Capability that can observe it."
    )


@namespaces(sosa="http://www.w3.org/ns/sosa/",
            ssn_system="http://www.w3.org/ns/ssn/systems/")
@urirefs(ObservableProperty="sosa:ObservableProperty",
         isObservedBy="sosa:isObservedBy")
class ObservableProperty(Property):
    """Observable Property - An observable quality (property, characteristic) of a FeatureOfInterest."""
    isObservedBy: Union[AnyThing, "Sensor", List[Union[AnyThing, "Sensor"]]] = Field(default=None,
                                                                                     alias="is_observed_by")


@namespaces(sosa="http://www.w3.org/ns/sosa/")
@urirefs(Actuator="sosa:Actuator")
class Actuator(Thing):
    """Actuator - A device that is used by, or implements, an (Actuation) Procedure that changes the state of the world."""


@namespaces(sosa="http://www.w3.org/ns/sosa/")
@urirefs(Sensor="sosa:Sensor",
         observes="sosa:observes",
         isHostedBy="sosa:isHostedBy",
         madeObservation="sosa:madeObservation"
         )
class Sensor(System):
    """Sensor -  Device, agent (including humans), or software (simulation) involved in, or implementing, a Procedure.
    Sensors respond to a Stimulus, e.g., a change in the environment, or Input data composed from the Results of prior
    Observations, and generate a Result. Sensors can be hosted by Platforms."""
    observes: Union[ObservableProperty, AnyThing, List[Union[ObservableProperty, AnyThing]]]
    isHostedBy: Union[AnyThing, "Platform", List[Union[AnyThing, "Platform"]]] = Field(
        default=None,
        alias="is_hosted_by",
        description="Relation between a Sensor and a Platform that hosts or mounts it."
    )
    madeObservation: Union["Observation", AnyThing, List[Union["Observation", AnyThing]]] = Field(
        default=None,
        alias="made_observation",
        description="The observations made by this sensor."
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


@namespaces(sosa="http://www.w3.org/ns/sosa/",
            ssn="http://www.w3.org/ns/ssn/", )
@urirefs(FeatureOfInterest="sosa:FeatureOfInterest",
         hasProperty="ssn:hasProperty"
         )
class FeatureOfInterest(Thing):
    """Feature Of Interest - The thing whose property is being estimated or calculated in the course of an Observation to arrive at a Result, or whose property is being manipulated by an Actuator, or which is being sampled or transformed in an act of Sampling."""
    hasProperty: Union[AnyThing, Property, List[Union[AnyThing, Property]]] = Field(
        default=None,
        alias="has_property",
        description="The property associated with this feature of interest."
    )




@namespaces(sosa="http://www.w3.org/ns/sosa/")
@urirefs(Observation="sosa:Observation",
         madeBySensor="sosa:madeBySensor",
         observedProperty="sosa:observedProperty",
         hasResult="sosa:hasResult",
         hasFeatureOfInterest="sosa:hasFeatureOfInterest",
         )
class Observation(Thing):
    madeBySensor: Union[AnyThing, Sensor] = Field(
        default=None,
        alias="made_by_sensor",
        description="The sensor that made the observation."
    )
    observedProperty: Union[AnyThing, ObservableProperty] = Field(
        default=None,
        alias="observed_property",
        description="The property that was observed."
    )
    hasResult: Union[AnyThing, "Result", List[Union[AnyThing, "Result"]]] = Field(
        default=None,
        alias="has_result",
        description="The result of the observation."
    )
    hasFeatureOfInterest: Union[AnyThing, FeatureOfInterest] = Field(
        default=None,
        alias="has_feature_of_interest",
        description=" A relation between an Observation and the entity whose quality was observed, or between an Actuation and the entity whose property was modified, or between an act of Sampling and the entity that was sampled."
    )

    def get_numerical_variable_by_kind_of_quantity(
            self,
            qkind: Union[str, qudt.QuantityKind]
    ) -> Tuple[NumericalVariable]:
        """Get all numerical variables in the observation by their quantity kind."""
        result = []
        for res in self.hasResult:
            nv = res.hasNumericalVariable
            if nv is not None and nv.is_kind_of_quantity(qkind):
                result.append(nv)
        return tuple(result)


@namespaces(ssn_system="http://www.w3.org/ns/ssn/systems/")
@urirefs(MeasurementRange="ssn_system:MeasurementRange")
class MeasurementRange(SystemProperty):
    """Accuracy - The closeness of agreement between the Result of an Observation (resp. the command of an Actuation) and the true value of the observed ObservableProperty (resp. of the acted on ActuatableProperty) under the defined Conditions."""


@namespaces(ssn_system="http://www.w3.org/ns/ssn/systems/")
@urirefs(Accuracy="ssn_system:Accuracy")
class Accuracy(SystemProperty):
    """The closeness of agreement between the Result of an Observation (resp. the command of an Actuation)
    and the true value of the observed ObservableProperty (resp. of the acted on ActuatableProperty) under the defined Conditions."""


@namespaces(
    sosa="http://www.w3.org/ns/sosa/",
    m4i="http://w3id.org/nfdi4ing/metadata4ing#"
)
@urirefs(Result="sosa:Result",
         hasNumericalVariable="m4i:hasNumericalVariable")
class Result(Thing):
    """Result - The output of an Observation."""
    hasNumericalVariable: Optional[AnyIriOf[NumericalVariable]] = Field(
        default=None,
        alias="has_numerical_variable"
    )

ObservableProperty.model_rebuild()
Platform.model_rebuild()
Sensor.model_rebuild()
SystemCapability.model_rebuild()
Observation.model_rebuild()
Result.model_rebuild()
