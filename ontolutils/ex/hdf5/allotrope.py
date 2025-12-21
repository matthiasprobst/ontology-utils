from typing import Optional, List, Tuple, Any

from pydantic import Field, field_validator
from pydantic.functional_validators import WrapValidator
from typing_extensions import Annotated

from ontolutils import Thing, namespaces, urirefs


def is_internal_hdf5_path(path: str, handler):
    if not path.startswith('/'):
        raise ValueError("HDF5 path must start with '/'")
    return path


def is_hdf5_root_path(path: str, handler):
    if path != '/':
        raise ValueError("HDF5 root path must be '/'")
    return path


HDF5Path = Annotated[str, WrapValidator(is_internal_hdf5_path)]
HDF5RootPath = Annotated[str, WrapValidator(is_internal_hdf5_path)]

__version__ = "REC/2024/12"
_NS = "http://purl.allotrope.org/ontologies/hdf5/1.8#"


@namespaces(hdf5=_NS)
@urirefs(Dataset='hdf5:Dataset',
         name='hdf5:name')
class Dataset(Thing):
    """Dataset"""
    name: HDF5Path


@namespaces(hdf5=_NS)
@urirefs(Group='hdf5:Group',
         member='hdf5:member',
         name='hdf5:name')
class Group(Thing):
    """hdf5:Group"""
    name: HDF5Path
    member: Any = Field(default=None)

    @field_validator("member", mode="before")
    @classmethod
    def check_member(cls, group_or_dataset):
        if isinstance(group_or_dataset, (List, Tuple)):
            for item in group_or_dataset:
                if not isinstance(item, (Group, Dataset)):
                    raise ValueError("Group member must be of type GroupOrDataset")
            return group_or_dataset
        if not isinstance(group_or_dataset, (Group, Dataset)):
            raise ValueError("Group member must be of type GroupOrDataset")
        return group_or_dataset


@namespaces(hdf5=_NS)
@urirefs(File='hdf5:File',
         rootGroup='hdf5:rootGroup')
class File(Thing):
    """File"""
    rootGroup: Optional[Group] = Field(default=None, alias="root_group")

    @field_validator("rootGroup", mode="before")
    @classmethod
    def _rootGroup(cls, root_group):
        if root_group.name != '/':
            raise ValueError("rootGroup must be of type Group")
        return root_group
