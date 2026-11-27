import json
import pathlib
import tomllib
import unittest

import yaml
from packaging.version import Version

from ontolutils import __version__


def get_package_meta():
    """Reads codemeta.json and returns it as dict"""
    with open(__this_dir__ / "../codemeta.json", "r") as f:
        codemeta = json.loads(f.read())
    return codemeta


__this_dir__ = pathlib.Path(__file__).parent


class TestVersion(unittest.TestCase):
    def test_version(self):
        with (__this_dir__ / "../pyproject.toml").open("rb") as f:
            project = tomllib.load(f)["project"]
        self.assertEqual(Version(__version__), Version(project["version"]))

    def test_codemeta(self):
        """checking if the version in codemeta.json is the same as the one of the toolbox"""

        codemeta = get_package_meta()

        self.assertEqual(Version(__version__), Version(codemeta["version"]))

    def test_citation_cff(self):
        citation_cff = __this_dir__ / "../CITATION.cff"
        with citation_cff.open(encoding="utf-8") as f:
            cff = yaml.safe_load(f)
        with (__this_dir__ / "../pyproject.toml").open("rb") as f:
            project = tomllib.load(f)["project"]

        self.assertEqual(Version(__version__), Version(cff["version"]))
        self.assertRegex(cff["doi"], r"^10\.\d{4,9}/\S+$")
        doi_url = f'https://doi.org/{cff["doi"]}'
        self.assertEqual(doi_url, project["urls"]["DOI"])
        self.assertEqual(doi_url, get_package_meta()["identifier"])
