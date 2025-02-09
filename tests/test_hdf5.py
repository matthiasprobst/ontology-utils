import logging
import unittest
from typing import List
from typing import Union

from pydantic import Field, HttpUrl

from ontolutils import Property
from ontolutils import Thing, urirefs, namespaces, build
from ontolutils.namespacelib import HDF5
LOG_LEVEL = logging.DEBUG


class TestHDF5(unittest.TestCase):

    def test_dataset(self):
        @namespaces(schema="https://schema.org/",
                    hdf=str(HDF5))
        @urirefs(Dataset='hdf:Dataset',
                 name='hdf:name',
                 datatype='hdf::datatype')
        class Dataset(Thing):
            name: str = Field(..., description="Name of the dataset")
            datatype: HttpUrl = Field(..., description="Datatype of the dataset")

        ds = Dataset(name="test", datatype=HDF5.H5T_INTEGER)
        serialization = ds.serialize(format="ttl")
        expectation = """@prefix hdf: <http://purl.allotrope.org/ontologies/hdf5/1.8#> .
@prefix ns1: <http://purl.allotrope.org/ontologies/hdf5/1.8#:> .

[] a hdf:Dataset ;
    ns1:datatype "http://purl.allotrope.org/ontologies/hdf5/1.8#H5T_INTEGER" ;
    hdf:name "test" .

"""
        self.assertEqual(serialization, expectation)
