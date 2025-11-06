import unittest

import pydantic

from ontolutils.ex.hdf5 import File, Dataset, Group


class TestHDF5(unittest.TestCase):

    def testHDF5File(self):
        root_group = Group(name="/")
        self.assertEqual(root_group.name, "/")
        file = File(rootGroup=root_group)
        self.assertEqual(file.rootGroup.name, "/")

        group = Group(name="/grp")
        with self.assertRaises(pydantic.ValidationError):
            File(rootGroup=group)

    def testDataset(self):
        with self.assertRaises(pydantic.ValidationError):
            Dataset(name='Dataset1')
        ds1 = Dataset(name='/Dataset1')
        self.assertEqual(ds1.name, '/Dataset1')

        ds2 = Dataset(name='/Group1/Dataset2')
        self.assertEqual(ds2.name, '/Group1/Dataset2')
        self.assertEqual(ds2.serialize("ttl"), """@prefix hdf5: <http://purl.allotrope.org/ontologies/hdf5/1.8#> .

[] a hdf5:Dataset ;
    hdf5:name "/Group1/Dataset2" .

""")

    def testGroup(self):
        with self.assertRaises(pydantic.ValidationError):
            Group(name='Group1')
        grp1 = Group(name='/Group1')
        self.assertEqual(grp1.serialize("ttl"), """@prefix hdf5: <http://purl.allotrope.org/ontologies/hdf5/1.8#> .

[] a hdf5:Group ;
    hdf5:name "/Group1" .

""")
