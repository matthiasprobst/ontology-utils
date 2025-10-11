import abc

from pydantic import BaseModel, ConfigDict

from ..config import PYDANTIC_EXTRA


class ThingModel(BaseModel, abc.ABC, validate_assignment=True):
    """Abstract base model class to be used by model classes used within ontolutils"""

    model_config = ConfigDict(extra=PYDANTIC_EXTRA, populate_by_name=True)

    def __getattr__(self, item):
        for field, meta in self.__class__.model_fields.items():
            if meta.alias == item:
                return getattr(self, field)
        return super().__getattr__(item)

    @abc.abstractmethod
    def _repr_html_(self) -> str:
        """Returns the HTML representation of the class"""
