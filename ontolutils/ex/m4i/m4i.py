import warnings
from datetime import datetime
from typing import Any, Dict, List, Union, Optional

from pydantic import HttpUrl, field_validator, Field, ConfigDict, field_serializer, AnyUrl, AliasChoices

from ontolutils import Thing, namespaces, urirefs, parse_unit, LangString
from ontolutils.ex.pimsii import Variable
from ..prov import Activity, Organization
from ..qudt import Unit, QuantityKind
from ..qudt.utils import get_unit, get_quantity_kind
from ..schema import ResearchProject
from ..sis import MeasurementUncertainty
from ...typing import AnyIriOf, AnyIri, AnyThingOrList, AnyIriOrListOf

try:
    import numpy as np
except ImportError as e:
    raise ImportError("numpy is required in m4i") from e

from functools import lru_cache


@lru_cache(maxsize=1)
def _get_xarray():
    try:
        import xarray as xr
        return xr
    except ImportError as e:
        raise ImportError(
            "xarray is required but not installed"
        ) from e


__version__ = "1.4.0"
_NS = "http://w3id.org/nfdi4ing/metadata4ing#"
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


@namespaces(m4i=_NS)
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


@namespaces(m4i=_NS)
@urirefs(NumericalVariable='m4i:NumericalVariable',
         hasUnit='m4i:hasUnit',
         hasKindOfQuantity='m4i:hasKindOfQuantity',
         hasNumericalValue='m4i:hasNumericalValue',
         hasMaximumValue='m4i:hasMaximumValue',
         hasMinimumValue='m4i:hasMinimumValue',
         hasStepSize='m4i:hasStepSize',
         hasUncertaintyDeclaration='m4i:hasUncertaintyDeclaration')
class NumericalVariable(Variable):
    """Pydantic Model for m4i:NumericalVariable

    **Note**, that hasNumericalValue can be a single numerical value (int or float), a list of numerical values,
    or a numpy ndarray. The ontology definition does not explicitly support multiple values, but this implementation
    allows it for convenience. However, when serializing to RDF, multiple values will be split into multiple
    NumericalVariable instances, while the IDs will be suffixed with an index (e.g., /0, /1, ...).
    """
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        serialize_numpy_as_list=True,
    )

    hasUnit: Optional[AnyIriOf[Unit]] = Field(
        alias="has_unit",
        validation_alias=AliasChoices(
            "hasUnit",  # camelCase
            "has_unit",  # snake_case
            "units"  # alternative name
        ),
        serialization_alias="units",  # optional, controls output name
        default=None)
    hasKindOfQuantity: Optional[AnyIriOrListOf[QuantityKind]] = Field(
        alias="has_kind_of_quantity", default=None
    )
    hasNumericalValue: Optional[Union[Union[int, float], List[Union[int, float]], np.ndarray]] = Field(
        alias="has_numerical_value",
        default=None)
    hasMaximumValue: Optional[Union[int, float]] = Field(alias="has_maximum_value", default=None)
    hasMinimumValue: Optional[Union[int, float]] = Field(alias="has_minimum_value", default=None)
    hasUncertaintyDeclaration: Optional[AnyIriOf[MeasurementUncertainty]] = Field(
        alias="has_uncertainty_declaration", default=None
    )
    hasStepSize: Optional[Union[int, float]] = Field(alias="has_step_size", default=None)

    def __getitem__(self, item):
        hasNumericalValue = self.hasNumericalValue
        if isinstance(hasNumericalValue, list):
            selected_values = np.asarray(hasNumericalValue).__getitem__(item)
            self_copy = self.model_copy()
            self_copy.hasNumericalValue = selected_values
            return self_copy
        if isinstance(hasNumericalValue, (float, int)):
            if item == 0 or item == -1:
                return self
            else:
                raise IndexError("NumericalVariable with single numerical value can only be indexed with 0 or -1")
        selected_values = hasNumericalValue.__getitem__(item)
        self_copy = self.model_copy()
        self_copy.hasNumericalValue = selected_values
        return self_copy

    def __len__(self):
        return self.size

    @field_validator("hasNumericalValue", mode='before')
    @classmethod
    def _parse_numerical_data(cls, data):
        if isinstance(data, np.ndarray):
            if data.ndim > 1:
                raise ValueError("Only 1D numpy arrays are supported for hasNumericalValue")
            return data
        return data

    @field_serializer("hasNumericalValue")
    def _serialize_has_numerical_value(self, data, info):
        if isinstance(data, np.ndarray):
            as_list = self.model_config.get("serialize_numpy_as_list")
            return data.tolist() if as_list else data
        return data

    @property
    def size(self) -> Optional[int]:
        data = self.hasNumericalValue
        if isinstance(data, list):
            return len(data)
        if isinstance(data, np.ndarray):
            return data.size
        if isinstance(data, (int, float)):
            return 1
        return None

    @property
    def ndim(self):
        data = self.hasNumericalValue
        if isinstance(data, np.ndarray):
            return data.ndim
        if isinstance(data, list):
            return 1
        if isinstance(data, (int, float)):
            return 0
        return None

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

        xr = _get_xarray()

        if self.hasNumericalValue is None:
            raise ValueError("hasNumericalValue must be set to convert to xarray DataArray")

        model = self.model_dump(exclude_none=True, by_alias=True)
        data = model.pop("has_numerical_value")
        if "has_variable_description" in model:
            desc = model.pop("has_variable_description")
            desc_with_lang = _xarray_lang_string_to_str("has_variable_description", desc, language)
            model.update(desc_with_lang)
        if "units" in model:
            # lazy import to avoid heavy top-level import cost
            from ..qudt.conversion import to_pint_unit
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

    def serialize(self,
                  format: str,
                  context: Optional[Dict] = None,
                  exclude_none: bool = True,
                  resolve_keys: bool = True,
                  base_uri: Optional[Union[str, AnyUrl]] = None,
                  **kwargs) -> str:
        """Serialize NumericalVariable to RDF format."""
        # if hasNumericalValue is not a float or int, we need to unpack it to n variables
        if self.hasNumericalValue is None:
            return super().serialize(
                format=format,
                context=context,
                exclude_none=exclude_none,
                resolve_keys=resolve_keys,
                base_uri=base_uri,
                **kwargs
            )
        if isinstance(self.hasNumericalValue, (int, float)):
            return super().serialize(
                format=format,
                context=context,
                exclude_none=exclude_none,
                resolve_keys=resolve_keys,
                base_uri=base_uri,
                **kwargs
            )
        if self.hasNumericalValue is not None:
            entities = [self.__class__(
                **{
                    **self.model_dump(
                        exclude={'has_numerical_value', 'id'}
                    ),
                    "has_numerical_value": v,
                    "id": f"{self.id}/{i}"
                }
            ) for i, v in enumerate(self.hasNumericalValue)]
        from ... import serialize
        return serialize(entities,
                         format=format,
                         context=context,
                         exclude_none=exclude_none,
                         resolve_keys=resolve_keys,
                         base_uri=base_uri, **kwargs)

    def is_kind_of_quantity(self, kind_of_quantity: Union[str, AnyUrl, QuantityKind]) -> bool:
        """Check if the NumericalVariable has the given quantity kind.

        Parameters
        ----------
        kind_of_quantity: Union[str, AnyUrl]
            Quantity kind URI to check against

        Returns
        -------
        bool
            True if the NumericalVariable has the given quantity kind, False otherwise
        """
        this_qkind = self.hasKindOfQuantity
        if this_qkind is None:
            if self.hasUnit is None:
                return False
            else:
                # get unit
                this_unit = self.hasUnit
                if isinstance(this_unit, str):
                    this_unit = get_unit(this_unit)
                if this_unit.hasQuantityKind is None:
                    this_unit = this_unit.expand()
                this_qkind = this_unit.hasQuantityKind
        else:
            if isinstance(this_qkind, str):
                this_qkind = get_quantity_kind(this_qkind)
            else:
                this_qkind = self.hasKindOfQuantity

        if isinstance(this_qkind, list):

            for qk in this_qkind:
                if isinstance(qk, QuantityKind):
                    if str(qk.id) == str(kind_of_quantity):
                        return True
                else:
                    if qk == str(kind_of_quantity):
                        return True
            return False
        if isinstance(this_qkind, QuantityKind):
            return this_qkind.id == kind_of_quantity.id
        elif isinstance(this_qkind, str):
            return str(this_qkind) == str(kind_of_quantity)
        raise TypeError("kind_of_quantity must be of type str, AnyUrl, or QuantityKind")


@namespaces(m4i=_NS,
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
    parameter: Union[AnyIri, Variable, NumericalVariable, List[Union[Variable, NumericalVariable, AnyIri]]] = None

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


@namespaces(m4i=_NS,
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
    hasParameter: Union[AnyIri, "TextVariable", "NumericalVariable",
    List[Union[AnyIri, "TextVariable", "NumericalVariable"]]] = Field(default=None, alias="parameter")
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


@namespaces(m4i=_NS,
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
    investigates: AnyThingOrList = None
    usageInstruction: str = Field(default=None, alias="usage_instruction")
    hasEmployedTool: Tool = Field(default=None, alias="has_employed_tool")
    realizesMethod: Union[Method, List[Method]] = Field(default=None, alias="realizes_method")
    hasInput: AnyThingOrList = Field(default=None,
                                     alias="has_input")
    hasOutput: AnyThingOrList = Field(default=None, alias="has_output")
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
