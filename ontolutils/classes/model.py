import abc

from pydantic import BaseModel


class ThingModel(abc.ABC, BaseModel):
    """Abstract class to be used by model classes used within PIVMetalib"""

    class Config:
        validate_assignment = True
        # extra = Extra.forbid
        extra = 'allow'

    @abc.abstractmethod
    def _repr_html_(self) -> str:
        """Returns the HTML representation of the class"""
