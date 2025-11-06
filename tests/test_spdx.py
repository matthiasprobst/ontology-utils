import pathlib
import unittest

__this_dir__ = pathlib.Path(__file__).parent

from ontolutils.ex.spdx import Checksum
from ontolutils.namespacelib.spdx import SPDX


class TestSpdx(unittest.TestCase):

    def test_checksum(self):
        checksum = Checksum(
            algorithm=SPDX.checksumAlgorithm_sha256,
            value='d2d2d2d2d2d2d2d2d2d2'
        )
        self.assertEqual(checksum.algorithm, str(SPDX.checksumAlgorithm_sha256))
        self.assertEqual(checksum.value, 'd2d2d2d2d2d2d2d2d2d2')

        checksum = Checksum(
            algorithm="md5",
            value='a1a1a1a1a1a1a1a1a1a1'
        )
        self.assertEqual(checksum.algorithm, str(SPDX.checksumAlgorithm_md5))
        self.assertEqual(checksum.value, 'a1a1a1a1a1a1a1a1a1a1')
