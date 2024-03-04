import json
from typing import List
from uuid import uuid4

import rdflib

from .thing import Thing, serialize_fields


def dump_jsonld(things: List[Thing], context: str, exclude_none=True):
    model_dicts = []
    g = rdflib.Graph()
    for thing in things:
        _model_dict = serialize_fields(thing, exclude_none=exclude_none)
        _model_dict['@id'] = f'_:{uuid4()}'
        model_dicts.append(_model_dict)

    if id is None:
        _id = '_:'
    else:
        _id = id
    jsonld = {
        "@context": {"@import": context},
        "@graph": model_dicts
    }

    g.parse(data=json.dumps(jsonld), format='json-ld')
    if context:
        return g.serialize(format='json-ld',
                           context={"@import": context},
                           indent=4)
    return g.serialize(format='json-ld', indent=4)
