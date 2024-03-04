import json
import pathlib
import unittest

from ontoutils import __version__


def get_package_meta():
    """Reads codemeta.json and returns it as dict"""
    with open(__this_dir__ / '../codemeta.json', 'r') as f:
        codemeta = json.loads(f.read())
    return codemeta


__this_dir__ = pathlib.Path(__file__).parent


class TestVersion(unittest.TestCase):

    def test_version(self):
        this_version = 'x.x.x'
        setupcfg_filename = __this_dir__ / '../setup.cfg'
        with open(setupcfg_filename, 'r') as f:
            lines = f.readlines()
            for line in lines:
                if 'version' in line:
                    this_version = line.split(' = ')[-1].strip()
        self.assertEqual(__version__, this_version)

    def test_codemeta(self):
        """checking if the version in codemeta.json is the same as the one of the toolbox"""

        codemeta = get_package_meta()

        assert codemeta['version'] == __version__
