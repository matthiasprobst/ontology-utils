from typing import Union, List, Optional

from pydantic import Field, field_validator

from ontolutils import Thing, namespaces, urirefs
from ...typing import ResourceType


@namespaces(qudt="http://qudt.org/schema/qudt/")
@urirefs(Unit='qudt:Unit',
         symbol='qudt:symbol',
         ucumCode='qudt:ucumCode',
         udunitsCode='qudt:udunitsCode',
         uneceCommonCode='qudt:uneceCommonCode',
         wikidataMatch='qudt:wikidataMatch',
         applicableSystem='qudt:applicableSystem',
         conversionMultiplier='qudt:conversionMultiplier',
         dbpediaMatch='qudt:dbpediaMatch',
         hasDimensionVector='qudt:hasDimensionVector',
         siExactMatch='qudt:siExactMatch',
         informativeReference='qudt:informativeReference',
         iec61360Code='qudt:iec61360Code',
         omUnit='qudt:omUnit',
         exactMatch='qudt:exactMatch',
         hasQuantityKind='qudt:hasQuantityKind',
         hasReciprocalUnit='qudt:hasReciprocalUnit',
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
    dbpediaMatch: Union[ResourceType] = Field(default=None, alias="dbpedia_match")
    hasDimensionVector: Union[ResourceType] = Field(default=None, alias="has_dimension_vector")
    informativeReference: Union[ResourceType] = Field(default=None, alias="informative_reference")
    iec61360Code: Union[str] = Field(default=None, alias="iec61360_code")
    omUnit: Union[ResourceType] = Field(default=None, alias="om_unit")
    exactMatch: Union["Unit", ResourceType, List[Union["Unit", ResourceType]]] = Field(default=None,
                                                                                       alias="exact_match")
    siExactMatch: Union[ResourceType] = Field(default=None, alias="si_exact_match")
    scalingOf: Union[ResourceType, "Unit", List[Union[ResourceType, "Unit"]]] = Field(default=None, alias="scaling_of")
    hasQuantityKind: Union[ResourceType, "QuantityKind", List[Union[ResourceType, "QuantityKind"]]] = Field(default=None, alias="has_quantity_kind")
    hasReciprocalUnit: Union[ResourceType, "Unit"] = Field(default=None, alias="has_reciprocal_unit")

    @field_validator("hasQuantityKind", mode='before')
    @classmethod
    def _parse_unit(cls, qkind):
        if str(qkind).startswith("http"):
            return str(qkind)
        if isinstance(qkind, str):
            # assumes that the string is a quantity kind is short form of the QUDT IRI
            return "https://https://qudt.org/vocab/quantitykind/" + qkind
        return qkind


@namespaces(qudt="http://qudt.org/schema/qudt/")
@urirefs(QuantityValue='qudt:QuantityValue')
class QuantityValue(Thing):
    """Implementation of qudt:QuantityValue"""


@namespaces(qudt="http://qudt.org/schema/qudt/")
@urirefs(QuantityKind='qudt:QuantityKind',
         applicableUnit='qudt:applicableUnit',
         quantityValue='qudt:quantityValue')
class QuantityKind(Thing):
    """Implementation of qudt:QuantityKind"""
    applicableUnit: Union[ResourceType, Unit] = Field(default=None, alias="applicable_unit")
    quantityValue: Union[ResourceType, QuantityValue] = Field(default=None, alias="quantity_value")


Unit.model_rebuild()
