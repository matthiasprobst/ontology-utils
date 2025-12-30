from typing import Union, List, Optional

import rdflib
from pydantic import Field, field_validator

from ontolutils import Thing, namespaces, urirefs
from ...typing import AnyThing, AnyIri, AnyThingOrList, AnyIriOrListOf

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
    wikidataMatch: Optional[AnyIri] = Field(default=None, alias="wikidata_match ")
    applicableSystem: Optional[AnyThingOrList] = Field(default=None, alias="applicable_system")
    conversionMultiplier: Optional[float] = Field(default=None, alias="conversion_multiplier")
    conversionMultiplierSN: Optional[float] = Field(default=None, alias="conversion_multiplier_sn")
    dbpediaMatch: Union[AnyThing] = Field(default=None, alias="dbpedia_match")
    hasDimensionVector: Union[AnyThing] = Field(default=None, alias="has_dimension_vector")
    informativeReference: Union[AnyThing] = Field(default=None, alias="informative_reference")
    iec61360Code: Union[str] = Field(default=None, alias="iec61360_code")
    omUnit: Union[AnyThing] = Field(default=None, alias="om_unit")
    exactMatch: Union["Unit", AnyThing, List[Union["Unit", AnyThing]]] = Field(default=None,
                                                                               alias="exact_match")
    siExactMatch: Union[AnyThing] = Field(default=None, alias="si_exact_match")
    conversionOffset: Union[float] = Field(default=None, alias="conversion_offset")
    conversionOffsetSN: Union[float] = Field(default=None, alias="conversion_offset_sn")
    scalingOf: Union[AnyThing, "Unit", List[Union[AnyThing, "Unit"]]] = Field(default=None, alias="scaling_of")
    hasQuantityKind: Union[AnyThing, "QuantityKind", List[Union[AnyThing, "QuantityKind"]]] = Field(
        default=None, alias="has_quantity_kind")
    hasReciprocalUnit: Union[AnyThing, "Unit"] = Field(default=None, alias="has_reciprocal_unit")
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

    @classmethod
    def get(cls, uri: Union[str, rdflib.URIRef]):
        from .utils import get_unit
        return get_unit(uri)

    def expand(self):
        from .utils import get_unit
        return get_unit(self.id)


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
         quantityValue='qudt:quantityValue'
         )
class QuantityKind(Thing):
    """Implementation of qudt:QuantityKind"""
    applicableUnit: Union[AnyIriOrListOf[Unit]] = Field(default=None,
                                                        alias="applicable_unit")
    quantityValue: Union[AnyThing, QuantityValue] = Field(default=None, alias="quantity_value")
    latexDefinition: Optional[Union[str, List[str]]] = Field(default=None, alias="latex_definition")
    latexSymbol: Optional[Union[str, List[str]]] = Field(default=None, alias="latex_symbol")
    hasDimensionVector: Optional[Union[AnyThing, List[AnyThing]]] = Field(default=None,
                                                                          alias="has_dimension_vector")
    informativeReference: Optional[Union[AnyThing, List[AnyThing]]] = Field(default=None,
                                                                            alias="informative_reference")
    symbol: Optional[Union[str, List[str]]] = Field(default=None, alias="symbol")
    iec61360Code: Optional[Union[str, List[str]]] = Field(default=None, alias="iec61360_code")
    wikidataMatch: Optional[Union[AnyThing, List[AnyThing]]] = Field(default=None, alias="wikidata_match")
    plainTextDescription: Optional[Union[str, List[str]]] = Field(default=None, alias="plain_text_description")

    def expand(self):
        from .utils import get_quantity_kind
        return get_quantity_kind(self.id)


Unit.model_rebuild()
