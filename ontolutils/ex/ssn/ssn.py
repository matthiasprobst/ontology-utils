from datetime import datetime, date
from typing import Union, List, Optional, Tuple

from pydantic import Field, field_validator

from ontolutils import Thing, urirefs, namespaces
from ontolutils.typing import AnyIriOf, AnyThing, AnyIriOrListOf
from .. import qudt
from ..m4i import NumericalVariable
from ..prov import Entity, Activity, Agent, Plan
from ..qudt import Unit

__version__ = "2017.10.19"

from ..time import TemporalEntity, Instant, Interval


@namespaces(ssn="http://www.w3.org/ns/ssn/")
@urirefs(Input="ssn:Input")
class Input(Thing):
    """Input - Any information that is provided to a Procedure for its use."""


@namespaces(ssn="http://www.w3.org/ns/ssn/")
@urirefs(Output="ssn:Output")
class Output(Thing):
    """has Output - Relation between a Procedure and an Output of it."""


@namespaces(sosa="http://www.w3.org/ns/sosa/",
            ssn="http://www.w3.org/ns/ssn/")
@urirefs(Procedure="sosa:Procedure",
         hasInput="ssn:hasInput",
         hasOutput="ssn:hasOutput",
         implementedBy="ssn:implementedBy"
         )
class Procedure(Plan):
    hasInput: Optional[AnyIriOrListOf[Input]] = Field(default=None, alias="has_input")
    hasOutput: Optional[AnyIriOrListOf[Output]] = Field(default=None, alias="has_output")
    implementedBy: Optional[AnyThing] = Field(default=None, alias="implemented_by")


@namespaces(
    sosa="http://www.w3.org/ns/sosa/",
)
@urirefs(Result="sosa:Result")
class Result(Entity):
    """Result - The output of an Observation."""


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
class ObservableProperty(Property, Entity):
    """Observable Property - An observable quality (property, characteristic) of a FeatureOfInterest."""
    isObservedBy: Union[AnyThing, "Sensor", List[Union[AnyThing, "Sensor"]]] = Field(default=None,
                                                                                     alias="is_observed_by")


@namespaces(sosa="http://www.w3.org/ns/sosa/")
@urirefs(Actuator="sosa:Actuator")
class Actuator(Agent, Entity):
    """Actuator - A device that is used by, or implements, an (Actuation) Procedure that changes the state of the world."""


@namespaces(sosa="http://www.w3.org/ns/sosa/")
@urirefs(Sensor="sosa:Sensor",
         observes="sosa:observes",
         isHostedBy="sosa:isHostedBy",
         madeObservation="sosa:madeObservation"
         )
class Sensor(System, Agent, Entity):
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
class Sampler(Agent, Entity):
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
class FeatureOfInterest(Entity):
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
         resultTime="sosa:resultTime",
         phenomenonTime="sosa:phenomenonTime",
         usedProcedure="sosa:usedProcedure",
         )
class Observation(Activity):
    usedProcedure: AnyIriOrListOf[Procedure] = Field(
        default=None,
        alias="used_procedure",
        description="A relation to link to a re-usable Procedure used in making an Observation, typically through a Sensor, Actuator or Sampler."
    )
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
    hasResult: Union[AnyThing, Result, List[Union[AnyThing, Result]]] = Field(
        default=None,
        alias="has_result",
        description="The result of the observation."
    )
    hasFeatureOfInterest: Union[AnyThing, FeatureOfInterest] = Field(
        default=None,
        alias="has_feature_of_interest",
        description=" A relation between an Observation and the entity whose quality was observed, or between an Actuation and the entity whose property was modified, or between an act of Sampling and the entity that was sampled."
    )
    resultTime: Optional[datetime] = Field(
        default=None,
        alias="result_time",
        description="the instant of time when the observation act was completed (e.g. when the acquisition software finished computing and storing the operating‑point values)"
    )
    phenomenonTime: Union[AnyThing, str, datetime, TemporalEntity] = Field(
        default=None,
        alias="phenomenon_time",
        description="the time that the result applies to the feature of interest"
    )

    @field_validator('phenomenonTime')
    @classmethod
    def _validate_phenomenon_time(cls, value):
        if isinstance(value, str):
            try:
                return Instant(datetime=datetime.fromisoformat(value))
            except ValueError:
                return value  # keep as string if not ISO format
        if isinstance(value, datetime):
            return Instant(datetime=value)
        if isinstance(value, date):
            return Instant(date=value)
        if isinstance(value, tuple):
            if len(value) == 2:
                start, end = value
                if isinstance(start, str):
                    try:
                        start = datetime.fromisoformat(start)
                    except ValueError:
                        pass
                if isinstance(end, str):
                    try:
                        end = datetime.fromisoformat(end)
                    except ValueError:
                        pass
                return Interval(has_beginning=start, has_end=end)
        return value

    def get_numerical_variable_by_kind_of_quantity(
            self,
            qkind: Union[str, qudt.QuantityKind]
    ) -> Tuple[NumericalVariable]:
        """Get all numerical variables in the observation by their quantity kind."""
        results = []
        for result in self.hasResult:
            if result is not None and result.is_kind_of_quantity(qkind):
                results.append(result)
        return tuple(results)

    def to_xarray(self, pref_lang: Optional[str] = "en", dimensions: Optional[List[str]] = "result"):
        """Returns an xarray DataArray"""
        import xarray as xr

        dataset_attrs = self.model_dump(exclude_none=True, exclude={"hasResult"}, by_alias=True)
        name = self.get_label(pref_lang=pref_lang) or self.get_alt_label(pref_lang=pref_lang)
        if name is not None:
            dataset_attrs['name'] = name
        dataset_attrs["type"] = "Observation"
        data = []
        if not isinstance(self.hasResult, list):
            has_results = [self.hasResult]
        else:
            has_results = self.hasResult
        for result in has_results:
            if result is not None:
                data.append(result.to_numpy())
            else:
                data.append(None)
        da = xr.DataArray(
            data=data,
            dims=dimensions,
            attrs=dataset_attrs
        )
        return da

    # def to_xarray(self, coord_label: Optional[str] = None, pref_lang: Optional[str] = "en"):
    #     import xarray as xr
    #     data_vars = {}
    #
    #     coord_key = None
    #     for result in self.hasResult:
    #         nv = result.hasNumericalVariable
    #         if nv is not None:
    #             var_name = nv.get_label(pref_lang=pref_lang)
    #             if isinstance(var_name, LangString):
    #                 var_name = var_name.get_preferred_string(pref_lang=pref_lang)
    #             if var_name is None:
    #                 var_name = nv.id
    #             # initialize container
    #             if var_name not in data_vars:
    #                 data_vars[var_name] = []
    #             data_vars[var_name].append(nv.to_numpy())
    #     xr_data = {}
    #     for var_name, values in data_vars.items():
    #         # skip the chosen coordinate variable as a data_var (it will be set as coord)
    #         if var_name == coord_key:
    #             continue
    #         xr_data[var_name] = (("observation",), values)
    #     coords = None
    #     if coord_key is not None:
    #         coords = {coord_label: (("observation",), data_vars[coord_key])}
    #     ds = xr.Dataset(data_vars=xr_data, coords=coords)
    #     return ds


@namespaces(ssn_system="http://www.w3.org/ns/ssn/systems/")
@urirefs(MeasurementRange="ssn_system:MeasurementRange")
class MeasurementRange(SystemProperty):
    """Accuracy - The closeness of agreement between the Result of an Observation (resp. the command of an Actuation) and the true value of the observed ObservableProperty (resp. of the acted on ActuatableProperty) under the defined Conditions."""


@namespaces(ssn_system="http://www.w3.org/ns/ssn/systems/")
@urirefs(Accuracy="ssn_system:Accuracy")
class Accuracy(SystemProperty):
    """The closeness of agreement between the Result of an Observation (resp. the command of an Actuation)
    and the true value of the observed ObservableProperty (resp. of the acted on ActuatableProperty) under the defined Conditions."""


@namespaces(ssn="http://www.w3.org/ns/ssn/")
@urirefs(Stimulus="ssn:Stimulus")
class Stimulus(Thing):
    """Stimulus - An event in the real world that 'triggers' the Sensor. The properties associated to the Stimulus may be different to the eventual observed ObservableProperty. It is the event, not the object, that triggers the Sensor."""


@namespaces(sosa="http://www.w3.org/ns/sosa/",
            ssn="http://www.w3.org/ns/ssn/")
@urirefs(ObservationCollection="sosa:ObservationCollection",
         madeBySensor="sosa:madeBySensor",
         observedProperty="sosa:observedProperty",
         hasFeatureOfInterest="sosa:hasFeatureOfInterest",
         hasUltimateFeatureOfInterest="sosa:hasUltimateFeatureOfInterest",
         usedProcedure="sosa:usedProcedure",
         wasOriginatedBy="ssn:wasOriginatedBy",
         phenomenonTime="sosa:phenomenonTime",
         resultTime="sosa:resultTime",
         hasMember="sosa:hasMember",
         )
class ObservationCollection(Thing):
    # maxCardinality 1 -> single-valued (optional)
    madeBySensor: Union[AnyIriOf[Sensor]] = Field(
        default=None,
        alias="made_by_sensor",
        description="The sensor that made the observations (max 1)."
    )

    observedProperty: Union[AnyIriOf[ObservableProperty]] = Field(
        default=None,
        alias="observed_property",
        description="The property that was observed for the collection (max 1)."
    )

    usedProcedure: Union[AnyIriOf[Procedure]] = Field(
        default=None,
        alias="used_procedure",
        description="Procedure used for the observations in the collection (max 1)."
    )

    wasOriginatedBy: Union[AnyIriOf[Stimulus]] = Field(
        default=None,
        alias="was_originated_by",
        description="Stimulus that originated the observations (ssn:wasOriginatedBy)."
    )

    phenomenonTime: Union[AnyThing, str] = Field(
        default=None,
        alias="phenomenon_time",
        description="Time when the phenomenon was (single value)."
    )

    resultTime: Union[AnyThing, str] = Field(
        default=None,
        alias="result_time",
        description="Time when the result was generated (single value)."
    )

    # hasFeatureOfInterest / hasUltimateFeatureOfInterest are single-valued (max 1)
    hasFeatureOfInterest: Union[AnyIriOf[FeatureOfInterest]] = Field(
        default=None,
        alias="has_feature_of_interest",
        description="Relation to the feature of interest (max 1)."
    )

    hasUltimateFeatureOfInterest: Union[AnyIriOf[FeatureOfInterest]] = Field(
        default=None,
        alias="has_ultimate_feature_of_interest",
        description="Ultimate feature of interest for the collection (max 1)."
    )

    # minCardinality 1 -> required (non-empty) list of members
    hasMember: AnyIriOrListOf[Union[Observation, "ObservationCollection"]] = Field(
        default=None,
        alias="has_member",
        description="Members of the collection (min 1)."
    )


ObservableProperty.model_rebuild()
Platform.model_rebuild()
Sensor.model_rebuild()
SystemCapability.model_rebuild()
Observation.model_rebuild()
