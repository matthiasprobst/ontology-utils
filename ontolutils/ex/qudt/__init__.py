from typing import Union, List

from pydantic import Field, field_validator

from ontolutils import Thing, namespaces, urirefs
from ...typing import ResourceType


@namespaces(qudt="http://qudt.org/schema/qudt/")
@urirefs(Unit='qudt:Unit',
         exactMatch='qudt:exactMatch',
         hasQuantityKind='qudt:hasQuantityKind',
         scalingOf='qudt:scalingOf')
class Unit(Thing):
    """Implementation of qudt:Unit"""
    exactMatch: Union["Unit", ResourceType, List[Union["Unit", ResourceType]]] = Field(default=None,
                                                                                       alias="exact_match")
    scalingOf: Union[ResourceType, "Unit", List[Union[ResourceType, "Unit"]]] = Field(default=None, alias="scaling_of")
    hasQuantityKind: Union[ResourceType, "QuantityKind"] = Field(default=None, alias="has_quantity_kind")

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
