"""Classes for working with ontology data"""
from .decorator import namespaces, urirefs
from .query_util import query, dquery
from .thing import Thing, get_urirefs, get_namespaces, build, Property, LangString
from .urivalue import URIValue
from .utils import as_id

__all__ = ['namespaces', 'urirefs', 'Thing', 'LangString', 'query', 'dquery', 'get_urirefs', 'get_namespaces', 'as_id',
           'build',
           'Property', 'URIValue']
