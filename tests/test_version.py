import json
import pathlib
import unittest

import yaml

from ontolutils import __version__


def get_package_meta():
    """Reads codemeta.json and returns it as dict"""
    with open(__this_dir__ / "../codemeta.json", "r") as f:
        codemeta = json.loads(f.read())
    return codemeta


__this_dir__ = pathlib.Path(__file__).parent


class TestVersion(unittest.TestCase):
    def test_version(self):
        this_version = "x.x.x"
        pyproject_filename = __this_dir__ / "../pyproject.toml"
        with open(pyproject_filename, "r") as f:
            lines = f.readlines()
            for line in lines:
                if "version" in line and line.strip().startswith("version"):
                    this_version = line.split(" = ")[-1].strip().strip('"')
        self.assertEqual(__version__.replace("rc", "-rc"), this_version)

    def test_codemeta(self):
        """checking if the version in codemeta.json is the same as the one of the toolbox"""

        codemeta = get_package_meta()

        assert codemeta["version"] == __version__.replace("rc", "-rc")

    def test_citation_cff(self):
        if "rc" not in __version__:
            citation_cff = __this_dir__ / "../CITATION.cff"
            with open(citation_cff, "r") as f:
                cff = yaml.safe_load(f)
            self.assertTrue(
                "todo" not in cff["doi"].lower(),
                "Please replace 'todo' in CITATION.cff",
            )
