"""Testing code used in the README.md file"""
import pathlib

from pydantic import EmailStr, Field
from rdflib import FOAF

from ontolutils import Thing, namespaces, urirefs


@namespaces(prov="http://www.w3.org/ns/prov#",
            foaf="http://xmlns.com/foaf/0.1/")
@urirefs(Person='prov:Person',
         firstName='foaf:firstName',
         last_name='foaf:lastName',
         mbox='foaf:mbox')
class Person(Thing):
    firstName: str
    last_name: str = Field(default=None, alias="lastName")
    mbox: EmailStr = None


agent = Person(mbox='e@mail.com', firstName='John', lastName='Doe')
print(agent.model_dump_jsonld())
agent = Person(mbox='e@mail.com', firstName='John', last_name='Doe')

print(agent.model_dump_jsonld())

# print(agent)
#
# with open("agent.json", "w") as f:
#     f.write(agent.model_dump_jsonld())
#
# # with open("agent.json", "r") as f:
# #     found_agents = Person.from_jsonld(data=f.read())
#
# found_agents = Person.from_jsonld(source="agent.json")
# found_agent = found_agents[0]
# print(found_agent.mbox)
#
# pathlib.Path("agent.json").unlink(missing_ok=True)
#
#
# @namespaces(prov='http://www.w3.org/ns/prov#',
#
#             foaf='http://xmlns.com/foaf/0.1/')
# @urirefs(Person='prov:Person', first_name='foaf:firstName')
# class Person(Thing):
#     first_name: str = None
#     last_name: str = None
#
#
# p = Person(first_name='John', last_name='Doe', age=30)
# print(p.model_dump_jsonld())
#
# # Person(first_name=1)
