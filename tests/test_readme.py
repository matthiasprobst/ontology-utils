"""Testing code used in the README.md file"""

from pydantic import EmailStr

from ontolutils import Thing, namespaces, urirefs


@namespaces(prov="http://www.w3.org/ns/prov#",
            foaf="http://xmlns.com/foaf/0.1/")
@urirefs(Agent='prov:Agent',
         mbox='foaf:mbox')
class Agent(Thing):
    """Implementation of http://www.w3.org/ns/prov#Agent

    Parameters
    ----------
    mbox: EmailStr = None
        Email address (foaf:mbox)
    """
    mbox: EmailStr = None  # foaf:mbox


agent = Agent(mbox='e@mail.com')

print(agent.model_dump_jsonld())

print(agent)

with open("agent.json", "w") as f:
    f.write(agent.model_dump_jsonld())

# with open("agent.json", "r") as f:
#     found_agents = Agent.from_jsonld(data=f.read())

found_agents = Agent.from_jsonld(source="agent.json")
found_agent = found_agents[0]
print(found_agent.mbox)
