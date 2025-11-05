import pathlib
import unittest

from ontolutils import cache
from ontolutils.ex import prov

__this_dir__ = pathlib.Path(__file__).parent
CACHE_DIR = cache.get_cache_dir()


class TestPROV(unittest.TestCase):

    def test_agent_with_extra_fields(self):
        agent = prov.Agent(
            id='_:b1',
            name='Agent name',
            mbox='a@email.com')
        self.assertEqual(agent.id, '_:b1')

        agent = prov.Agent(
            id='_:b1',
            name='Agent name')
        self.assertEqual(agent.id, '_:b1')
