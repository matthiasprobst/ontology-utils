import abc

from pydantic import BaseModel, ConfigDict


class ThingModel(abc.ABC, BaseModel):
    """Abstract class to be used by model classes"""
    model_config = ConfigDict(extra='allow')  # or 'forbid' or 'ignore'

    @abc.abstractmethod
    def _repr_html_(self) -> str:
        """Returns the HTML representation of the class"""
