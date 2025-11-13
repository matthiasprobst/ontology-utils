import warnings
from datetime import datetime
from typing import Any
from typing import List, Union
from typing import Optional

from pydantic import HttpUrl, field_validator, Field

from ontolutils import Thing, namespaces, urirefs
from ontolutils import parse_unit, LangString
from ontolutils.ex.pimsii import Variable
from ..prov import Activity
from ..prov import Organization
from ..schema import ResearchProject


@namespaces(m4i="http://w3id.org/nfdi4ing/metadata4ing#")
@urirefs(TextVariable='m4i:TextVariable',
         hasStringValue='m4i:hasStringValue')
class TextVariable(Variable):
    """Pydantic Model for http://www.w3.org/ns/prov#Agent

    .. note::

        More than the below parameters are possible but not explicitly defined here.


    Parameters
    ----------
    hasStringValue: str
        String value
    """
    hasStringValue: Optional[LangString] = Field(alias="has_string_value", default=None)


@namespaces(m4i="http://w3id.org/nfdi4ing/metadata4ing#")
@urirefs(NumericalVariable='m4i:NumericalVariable',
         hasUnit='m4i:hasUnit',
         hasNumericalValue='m4i:hasNumericalValue',
         hasMaximumValue='m4i:hasMaximumValue')
class NumericalVariable(Variable):
    hasUnit: Optional[str] = Field(alias="has_unit", default=None)
    hasNumericalValue: Optional[Union[float, List[float]]] = Field(alias="has_numerical_value", default=None)
    hasMaximumValue: Optional[float] = Field(alias="has_maximum_value", default=None)

    @field_validator("hasUnit", mode='before')
    @classmethod
    def _parse_unit(cls, unit):
        if unit.startswith("http"):
            return str(unit)
        try:
            return parse_unit(unit)
        except KeyError as e:
            warnings.warn(f"Unit '{unit}' could not be parsed to QUDT IRI. This is a process based on a dictionary "
                          f"lookup. Either the unit is wrong or it is not yet included in the dictionary. ")
        return str(unit)


@namespaces(m4i="http://w3id.org/nfdi4ing/metadata4ing#",
            schema="https://schema.org/")
@urirefs(Method='m4i:Method',
         description='schema:description',
         parameter='m4i:hasParameter')
class Method(Thing):
    """Pydantic Model for m4i:Method

    .. note::

        More than the below parameters are possible but not explicitly defined here.


    Parameters
    ----------
    description: str
        Description
    parameter: Variable
        Variable(s) used in the method
    """
    description: str = None
    parameter: Union[Variable, List[Variable], NumericalVariable, List[NumericalVariable]] = None

    def add_numerical_variable(self, numerical_variable: Union[dict, "NumericalVariable"]):
        """add numerical variable to tool"""
        if isinstance(numerical_variable, dict):
            # lokaler Import vermeidet zirkulären Import beim Modul-Import
            from ontolutils.ex.m4i import NumericalVariable
            numerical_variable = NumericalVariable(**numerical_variable)
        if self.parameter is None:
            self.parameter = [numerical_variable]
        elif isinstance(self.parameter, list):
            self.parameter.append(numerical_variable)
        else:
            self.parameter = [self.parameter, numerical_variable]


@namespaces(m4i="http://w3id.org/nfdi4ing/metadata4ing#",
            pivmeta="https://matthiasprobst.github.io/pivmeta#",
            obo="http://purl.obolibrary.org/obo/")
@urirefs(Tool='m4i:Tool',
         manufacturer='pivmeta:manufacturer',
         hasParameter='m4i:hasParameter',
         BFO_0000051='obo:BFO_0000051')
class Tool(Thing):
    """Pydantic Model for m4i:Tool

    .. note::

        More than the below parameters are possible but not explicitly defined here.


    Parameters
    ----------
    hasParameter: TextVariable or NumericalVariable or list of them
        Text or numerical variable
    """
    hasParameter: Union["TextVariable", "NumericalVariable",
    List[Union["TextVariable", "NumericalVariable"]]] = Field(default=None, alias="parameter")
    manufacturer: Organization = Field(default=None)
    BFO_0000051: Optional[Union[Thing, List[Thing]]] = Field(alias="has_part", default=None)

    @property
    def hasPart(self):
        return self.BFO_0000051

    @hasPart.setter
    def hasPart(self, value):
        self.BFO_0000051 = value

    @field_validator('manufacturer', mode="before")
    @classmethod
    def _validate_manufacturer(cls, value):
        if isinstance(value, str) and value.startswith("http"):
            return Organization(id=value)
        return value

    def add_numerical_variable(self, numerical_variable: Union[dict, NumericalVariable]):
        """add numerical variable to tool"""
        if isinstance(numerical_variable, dict):
            numerical_variable = NumericalVariable(**numerical_variable)
        if self.parameter is None:
            self.hasParameter = [numerical_variable, ]
        elif isinstance(self.hasParameter, list):
            self.hasParameter.append(numerical_variable)
        else:
            self.hasParameter = [self.hasParameter,
                                 numerical_variable]


@namespaces(pimsii="http://www.molmod.info/semantics/pims-ii.ttl#", )
class Assignment(Thing):
    """not yet implemented"""


OneOrMultiThings = Union[Thing, HttpUrl, str, List[Union[Thing, HttpUrl, str]]]


@namespaces(m4i="http://w3id.org/nfdi4ing/metadata4ing#",
            schema="https://schema.org/",
            obo="http://purl.obolibrary.org/obo/")
@urirefs(ProcessingStep='m4i:ProcessingStep',
         startTime='schema:startTime',
         endTime='schema:endTime',
         RO_0002224='obo:RO_0002224',
         RO_0002230='obo:RO_0002230',
         hasRuntimeAssignment='m4i:hasRuntimeAssignment',
         investigates='m4i:investigates',
         usageInstruction='m4i:usageInstruction',
         hasEmployedTool='m4i:hasEmployedTool',
         realizesMethod='m4i:realizesMethod',
         hasInput='m4i:hasInput',
         hasOutput='m4i:hasOutput',
         partOf='m4i:partOf',
         precedes='m4i:precedes')
class ProcessingStep(Activity):
    """Pydantic Model for m4i:ProcessingStep

    .. note::

        More than the below parameters are possible but not explicitly defined here.


    Parameters
    ----------
    tbd
    """
    startTime: datetime = Field(default=None, alias="start_time")
    endTime: datetime = Field(default=None, alias="end_time")
    RO_0002224: Any = Field(default=None, alias="starts_with")
    RO_0002230: Any = Field(default=None, alias="ends_with")
    hasRuntimeAssignment: Assignment = Field(default=None, alias="runtime_assignment")
    investigates: Thing = None
    usageInstruction: str = Field(default=None, alias="usage_instruction")
    hasEmployedTool: Tool = Field(default=None, alias="has_employed_tool")
    realizesMethod: Union[Method, List[Method]] = Field(default=None, alias="realizes_method")
    hasInput: Thing = Field(default=None, alias="has_input")
    hasOutput: OneOrMultiThings = Field(default=None, alias="has_output")
    partOf: Union[ResearchProject, "ProcessingStep"] = Field(default=None, alias="part_of")
    precedes: "ProcessingStep" = None

    @field_validator('hasOutput', 'hasInput', mode='before')
    @classmethod
    def _one_or_multiple_things(cls, value):
        if isinstance(value, list):
            ret_value = []
            for v in value:
                if isinstance(v, Thing):
                    ret_value.append(v)
                else:
                    if v.startswith("_:"):
                        ret_value.append(v)
                    else:
                        ret_value.append(str(HttpUrl(v)))
            return ret_value
        if isinstance(value, Thing):
            return value
        if str(value).startswith("_:"):
            return value
        return str(HttpUrl(value))

    @field_validator('RO_0002224', mode='before')
    @classmethod
    def _starts_with(cls, starts_with):
        return _validate_processing_step(starts_with)

    @field_validator('RO_0002230', mode='before')
    @classmethod
    def _ends_with(cls, ends_with):
        return _validate_processing_step(ends_with)

    @property
    def starts_with(self):
        return self.RO_0002224

    @starts_with.setter
    def starts_with(self, starts_with):
        self.RO_0002224 = _validate_processing_step(starts_with)

    @property
    def ends_with(self):
        return self.RO_0002230

    @ends_with.setter
    def ends_with(self, ends_with):
        self.RO_0002230 = _validate_processing_step(ends_with)


def _validate_processing_step(ps) -> ProcessingStep:
    if isinstance(ps, ProcessingStep):
        return ps
    if isinstance(ps, dict):
        return ProcessingStep(**ps)
    raise TypeError("starts_with must be of type ProcessingStep or a dictionary")


from ..dcat.resource import Distribution

# add new field to Distribution wasGeneratedBy: ProcessingStep = Field(default=None, alias='was_generated_by'):

Distribution.wasGeneratedBy: ProcessingStep = Field(default=None, alias='was_generated_by')
