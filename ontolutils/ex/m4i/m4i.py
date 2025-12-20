import warnings
from datetime import datetime
from typing import Any, Dict
from typing import List, Union
from typing import Optional

from pydantic import HttpUrl, field_validator, Field

from ontolutils import Thing, namespaces, urirefs
from ontolutils import parse_unit, LangString
from ontolutils.ex.pimsii import Variable
from ..prov import Activity
from ..prov import Organization
from ..qudt import Unit
from ..qudt.conversion import to_pint_unit
from ..schema import ResearchProject
from ..sis import MeasurementUncertainty
from ...typing import ResourceType

_UNIT_REGISTRY = None


def get_unit_registry():
    try:
        import pint
    except ImportError as e:
        raise ImportError("pint is required to use unit registry") from e
    if _UNIT_REGISTRY is None:
        return pint.UnitRegistry()
    else:
        return _UNIT_REGISTRY


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
         hasMaximumValue='m4i:hasMaximumValue',
         hasMinimumValue='m4i:hasMinimumValue',
         hasStepSize='m4i:hasStepSize',
         hasUncertaintyDeclaration='m4i:hasUncertaintyDeclaration')
class NumericalVariable(Variable):
    hasUnit: Optional[Union[ResourceType, Unit]] = Field(alias="units", default=None)
    hasNumericalValue: Optional[Union[Union[int, float], List[Union[int, float]]]] = Field(alias="has_numerical_value",
                                                                                           default=None)
    hasMaximumValue: Optional[Union[int, float]] = Field(alias="has_maximum_value", default=None)
    hasMinimumValue: Optional[Union[int, float]] = Field(alias="has_minimum_value", default=None)
    hasUncertaintyDeclaration: Optional[Union[MeasurementUncertainty, ResourceType]] = Field(
        alias="has_uncertainty_declaration", default=None
    )
    hasStepSize: Optional[Union[int, float]] = Field(alias="has_step_size", default=None)

    @field_validator("hasUnit", mode='before')
    @classmethod
    def _parse_unit(cls, unit):
        if isinstance(unit, str):
            if unit.startswith("http"):
                return str(unit)
            try:
                return parse_unit(unit)
            except KeyError as e:
                warnings.warn(f"Unit '{unit}' could not be parsed to QUDT IRI. This is a process based on a dictionary "
                              f"lookup. Either the unit is wrong or it is not yet included in the dictionary. ")
            return str(unit)
        return unit

    def to_pint(self, ureg=None):
        """Convert numerical value (not the min/max value!) to pint Quantity"""
        if self.hasNumericalValue is None or self.hasUnit is None:
            raise ValueError("Both hasNumericalValue and hasUnit must be set to convert to pint Quantity")

        from ..qudt.conversion import to_pint_unit
        new_unit = to_pint_unit(self.hasUnit, ureg=ureg)

        return self.hasNumericalValue * new_unit

    def to_xarray(self, language: str = "en"):
        """Convert numerical value to xarray DataArray"""
        try:
            import xarray as xr
        except ImportError as e:
            raise ImportError("xarray is required to use to_xarray method") from e

        if self.hasNumericalValue is None:
            raise ValueError("hasNumericalValue must be set to convert to xarray DataArray")

        model = self.model_dump(exclude_none=True, by_alias=True)
        data = model.pop("has_numerical_value")
        if "has_variable_description" in model:
            desc = model.pop("has_variable_description")
            desc_with_lang = _xarray_lang_string_to_str("has_variable_description", desc, language)
            model.update(desc_with_lang)
        if "units" in model:
            pint_unit = to_pint_unit(self.hasUnit)
            model["units"] = f"{pint_unit:~f}".replace(" ", "")
        if "label" in model:
            labels = model.pop("label")
            labels_with_lang = _xarray_lang_string_to_str("label", labels, language, "long_name")

            model.update(labels_with_lang)

        return xr.DataArray(data=data, attrs=model)

    @classmethod
    def from_pint(cls, quantity: "pint.Quantity", lookup: Dict = None, **kwargs) -> "NumericalVariable":
        """Create NumericalVariable from pint Quantity.

        The unit of the quantity is formatted to a string using the compact format (e.g. 'm/s^2') and
        then mapped to a QUDT IRI using a lookup dictionary.
        An internal lookup dictionary is used by default, which can be extended or overridden
        by providing an additional lookup dictionary.

        Parameters
        ----------
        quantity: pint.Quantity
            Pint Quantity to convert
        lookup: Dict, optional
            Optional additional lookup dictionary to map units to QUDT IRIs
        kwargs: additional keyword arguments for NumericalVariable

        Returns
        -------
        NumericalVariable
            NumericalVariable instance
        """
        from ontolutils.utils.qudt_units import qudt_lookup
        _qudt_lookup = qudt_lookup.copy()
        if lookup:
            _qudt_lookup.update(lookup)
        try:
            unit = _qudt_lookup[f"{quantity.units:~f}".replace(" ", "")]
        except KeyError as e:
            raise KeyError(f"Unit '{quantity.units}' could not be mapped to QUDT IRI") from e
        return cls(hasNumericalValue=quantity.magnitude, hasUnit=unit, **kwargs)

    @classmethod
    def from_xarray(cls, data_array: "xarray.DataArray", **kwargs) -> "NumericalVariable":
        """Create NumericalVariable from xarray DataArray."""
        fields = data_array.attrs.copy()
        fields.update(kwargs)
        # loop over the fields. if a key ends with @xx (language tag), remove it and convert the value to LangString
        _language_data = {}
        for key, values in fields.copy().items():
            if "@" in key:
                base_key, lang = key.split("@", 1)
                if base_key not in _language_data:
                    _language_data[base_key] = [f"{values}@{lang}", ]
                else:
                    _language_data[base_key].append(f"{values}@{lang}")
                fields.pop(key)
        for key, value in _language_data.items():
            if key in fields:
                if isinstance(value, list):
                    fields[key] = [fields[key], *value]
                else:
                    fields[key] = [fields[key], value]
            else:
                if len(value) == 1:
                    fields[key] = value[0]
                else:
                    fields[key] = value
        if "units" in fields:
            ureg = get_unit_registry()
            unit_str = f'{ureg(fields["units"]).units:~f}'.replace(" ", "")
            fields["units"] = unit_str
        return cls(hasNumericalValue=data_array.data, **fields)


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


OneOrMultiEntities = Union[Thing, ResourceType, HttpUrl, str, List[Union[Thing, ResourceType, HttpUrl, str]]]


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
    investigates: Optional[Union[ResourceType, Thing, List[Union[ResourceType, Thing]]]] = None
    usageInstruction: str = Field(default=None, alias="usage_instruction")
    hasEmployedTool: Tool = Field(default=None, alias="has_employed_tool")
    realizesMethod: Union[Method, List[Method]] = Field(default=None, alias="realizes_method")
    hasInput: Optional[Union[ResourceType, Thing, List[Union[ResourceType, Thing]]]] = Field(default=None,
                                                                                             alias="has_input")
    hasOutput: OneOrMultiEntities = Field(default=None, alias="has_output")
    partOf: Union[ResearchProject, "ProcessingStep", List[Union[ResearchProject, "ProcessingStep"]]] = Field(
        default=None, alias="part_of")
    precedes: Union["ProcessingStep", List[Union["ProcessingStep"]]] = None

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

ProcessingStep.model_rebuild()


def _xarray_lang_string_to_str(name: str, data: Union[str, Dict], language: str, use_name: str = None):
    out = {}
    if use_name is None:
        use_name = name
    if isinstance(data, list):
        use_label = None
        for datum in data:
            if "lang" in datum:
                _lang = datum['lang']
                out[f"{name}@{_lang}"] = datum['value']
                if _lang == language:
                    use_label = datum['value']
            else:
                out[name] = datum["value"]
        if use_label is None and len(data) > 0:
            use_label = data[0]['value']
    else:
        use_label = data["value"]
    out[use_name] = use_label
    return out
