from typing import Union, List, Optional

from pydantic import Field, field_validator

from ontolutils import Thing, namespaces, urirefs
from ...typing import ResourceType

__version__ = "3.1.9"
_NS = "http://qudt.org/schema/qudt/"


@namespaces(qudt=_NS)
@urirefs(Unit='qudt:Unit',
         symbol='qudt:symbol',
         ucumCode='qudt:ucumCode',
         udunitsCode='qudt:udunitsCode',
         uneceCommonCode='qudt:uneceCommonCode',
         wikidataMatch='qudt:wikidataMatch',
         applicableSystem='qudt:applicableSystem',
         conversionMultiplier='qudt:conversionMultiplier',
         conversionMultiplierSN='qudt:conversionMultiplierSN',
         dbpediaMatch='qudt:dbpediaMatch',
         hasDimensionVector='qudt:hasDimensionVector',
         siExactMatch='qudt:siExactMatch',
         informativeReference='qudt:informativeReference',
         iec61360Code='qudt:iec61360Code',
         omUnit='qudt:omUnit',
         latexSymbol='qudt:latexSymbol',
         exactMatch='qudt:exactMatch',
         hasQuantityKind='qudt:hasQuantityKind',
         hasReciprocalUnit='qudt:hasReciprocalUnit',
         conversionOffset='qudt:conversionOffset',
         conversionOffsetSN='qudt:conversionOffsetSN',
         latexDefinition='qudt:latexDefinition',
         expression='qudt:expression',
         scalingOf='qudt:scalingOf')
class Unit(Thing):
    """Implementation of qudt:Unit"""
    symbol: Optional[str] = Field(default=None, alias="symbol")
    ucumCode: Optional[str] = Field(default=None, alias="ucum_code")
    udunitsCode: Optional[str] = Field(default=None, alias="udunits_code")
    uneceCommonCode: Optional[str] = Field(default=None, alias="unece_common_code")
    wikidataMatch: Optional[ResourceType] = Field(default=None, alias="wikidata_match ")
    applicableSystem: Optional[Union[ResourceType, List[ResourceType]]] = Field(default=None, alias="applicable_system")
    conversionMultiplier: Optional[float] = Field(default=None, alias="conversion_multiplier")
    conversionMultiplierSN: Optional[float] = Field(default=None, alias="conversion_multiplier_sn")
    dbpediaMatch: Union[ResourceType] = Field(default=None, alias="dbpedia_match")
    hasDimensionVector: Union[ResourceType] = Field(default=None, alias="has_dimension_vector")
    informativeReference: Union[ResourceType] = Field(default=None, alias="informative_reference")
    iec61360Code: Union[str] = Field(default=None, alias="iec61360_code")
    omUnit: Union[ResourceType] = Field(default=None, alias="om_unit")
    exactMatch: Union["Unit", ResourceType, List[Union["Unit", ResourceType]]] = Field(default=None,
                                                                                       alias="exact_match")
    siExactMatch: Union[ResourceType] = Field(default=None, alias="si_exact_match")
    conversionOffset: Union[float] = Field(default=None, alias="conversion_offset")
    conversionOffsetSN: Union[float] = Field(default=None, alias="conversion_offset_sn")
    scalingOf: Union[ResourceType, "Unit", List[Union[ResourceType, "Unit"]]] = Field(default=None, alias="scaling_of")
    hasQuantityKind: Union[ResourceType, "QuantityKind", List[Union[ResourceType, "QuantityKind"]]] = Field(
        default=None, alias="has_quantity_kind")
    hasReciprocalUnit: Union[ResourceType, "Unit"] = Field(default=None, alias="has_reciprocal_unit")
    latexSymbol: Optional[Union[str, List[str]]] = Field(default=None, alias="latex_symbol")
    latexDefinition: Optional[Union[str, List[str]]] = Field(default=None, alias="latex_definition")
    expression: Optional[Union[str, List[str]]] = Field(default=None, alias="expression")

    @field_validator("hasQuantityKind", mode='before')
    @classmethod
    def _parse_unit(cls, qkind):
        if str(qkind).startswith("http"):
            return str(qkind)
        if isinstance(qkind, str):
            # assumes that the string is a quantity kind is short form of the QUDT IRI
            return "https://https://qudt.org/vocab/quantitykind/" + qkind
        return qkind


@namespaces(qudt=_NS)
@urirefs(QuantityValue='qudt:QuantityValue')
class QuantityValue(Thing):
    """Implementation of qudt:QuantityValue"""


@namespaces(qudt=_NS)
@urirefs(QuantityKind='qudt:QuantityKind',
         applicableUnit='qudt:applicableUnit',
         latexDefinition='qudt:latexDefinition',
         latexSymbol='qudt:latexSymbol',
         hasDimensionVector='qudt:hasDimensionVector',
         informativeReference='qudt:informativeReference',
         symbol='qudt:symbol',
         iec61360Code='qudt:iec61360Code',
         wikidataMatch='qudt:wikidataMatch',
         plainTextDescription='qudt:plainTextDescription',
         quantityValue='qudt:quantityValue')
class QuantityKind(Thing):
    """Implementation of qudt:QuantityKind"""
    applicableUnit: Union[ResourceType, Unit, List[Union[ResourceType, Unit]]] = Field(default=None,
                                                                                       alias="applicable_unit")
    quantityValue: Union[ResourceType, QuantityValue] = Field(default=None, alias="quantity_value")
    latexDefinition: Optional[Union[str, List[str]]] = Field(default=None, alias="latex_definition")
    latexSymbol: Optional[Union[str, List[str]]] = Field(default=None, alias="latex_symbol")
    hasDimensionVector: Optional[Union[ResourceType, List[ResourceType]]] = Field(default=None,
                                                                                  alias="has_dimension_vector")
    informativeReference: Optional[Union[ResourceType, List[ResourceType]]] = Field(default=None,
                                                                                    alias="informative_reference")
    symbol: Optional[Union[str, List[str]]] = Field(default=None, alias="symbol")
    iec61360Code: Optional[Union[str, List[str]]] = Field(default=None, alias="iec61360_code")
    wikidataMatch: Optional[Union[ResourceType, List[ResourceType]]] = Field(default=None, alias="wikidata_match")
    plainTextDescription: Optional[Union[str, List[str]]] = Field(default=None, alias="plain_text_description")


Unit.model_rebuild()
