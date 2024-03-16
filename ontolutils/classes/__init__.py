"""Classes for working with ontology data"""
from .decorator import namespaces, urirefs
from .query_util import query, dquery
from .thing import Thing

__all__ = ['namespaces', 'urirefs', 'Thing', 'query', 'dquery']
