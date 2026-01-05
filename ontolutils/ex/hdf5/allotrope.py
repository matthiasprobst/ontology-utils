from typing import Optional, List, Tuple, Any, Union

from pydantic import Field, field_validator
from pydantic.functional_validators import WrapValidator
from typing_extensions import Annotated

from ontolutils import Thing, namespaces, urirefs
from ontolutils.typing import AnyIriOf


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
@urirefs(NamedObject='hdf5:NamedObject')
class NamedObject(Thing):
    """NamedObject"""


@namespaces(hdf5=_NS)
@urirefs(Dataspace='hdf5:Dataspace',
         dimension='hdf5:dimension',
         rank='hdf5:rank',
         )
class Dataspace(Thing):
    """A dataset dataspace describes the dimensionality of the dataset. The dimensions of a dataset can be fixed (unchanging), or they may be unlimited, which means that they are extendible (i.e. they can grow larger). [Allotrope]"""
    dimension: Optional[Union[int, List[int]]] = Field(default=None)
    rank: Optional[int] = Field(default=None, ge=0, le=32)


@namespaces(hdf5=_NS)
@urirefs(StorageLayout='hdf5:StorageLayout')
class StorageLayout(Thing):
    """StorageLayout"""


@namespaces(hdf5=_NS)
@urirefs(Dataset='hdf5:Dataset',
         name='hdf5:name',
         dataspace='hdf5:dataspace',
         layout='hdf5:layout',
         rank='hdf5:rank',
         )
class Dataset(Thing):
    """A multi-dimensional array of data elements, together with supporting metadata. [Allotrope]"""
    name: HDF5Path
    dataspace: Optional[AnyIriOf[Dataspace]] = Field(
        default=None)  # owl:qualifiedCardinality "1"^^xsd:nonNegativeInteger
    layout: Optional[AnyIriOf[StorageLayout]] = Field(
        default=None)  # owl:qualifiedCardinality "1"^^xsd:nonNegativeInteger
    rank: Optional[int] = Field(default=None, ge=0, le=32)  # owl:qualifiedCardinality "1"^^xsd:nonNegativeInteger

    @field_validator("name", mode="before")
    @classmethod
    def _validate_name(cls, name):
        if not name.startswith('/'):
            raise ValueError("Dataset name must start with '/'")
        return name


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
