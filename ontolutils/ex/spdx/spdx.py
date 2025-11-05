from typing import Union, Optional

import rdflib
from pydantic import Field, field_validator

from ontolutils import Thing, urirefs, namespaces
from ontolutils.namespacelib.spdx import SPDX
from ontolutils.typing import ResourceType


@namespaces(spdx="http://spdx.org/rdf/terms#")
@urirefs(Checksum='spdx:Checksum',
         algorithm='spdx:algorithm',
         checksumValue='spdx:checksumValue')
class Checksum(Thing):
    """Pydantic implementation of dcat:Checksum

    Parameters
    ----------
    algorithm: str
        The algorithm used to compute the checksum (e.g. "MD5", "SHA-1", "SHA-256")
    checksumValue: str
        The checksum value
    """
    algorithm: Optional[ResourceType] = Field(default="None")  # dcat:algorithm
    checksumValue: str = Field(alias="value")  # dcat:value

    @field_validator("algorithm", mode="before")
    @classmethod
    def validate_algorithm(cls, algorithm_value: Union[str, ResourceType]) -> Union[str, ResourceType]:
        if isinstance(algorithm_value, rdflib.URIRef):
            return str(algorithm_value)
        if isinstance(algorithm_value, str) and str(algorithm_value).startswith("http"):
            return str(algorithm_value)
        if isinstance(algorithm_value, str):
            guess_name = f"checksumAlgorithm_{algorithm_value.lower()}"
            return str(SPDX[guess_name])
        return str(algorithm_value)
