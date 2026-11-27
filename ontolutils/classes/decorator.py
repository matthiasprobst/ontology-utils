import pydantic
from pydantic import HttpUrl
from typing import Dict
from . import utils
from .utils import split_uri

URIRefManager = utils.UNManager()
NamespaceManager = utils.UNManager()


def _is_http_url(url: str) -> bool:
    """Check if a string is a valid http url.

    Parameters
    ----------
    url : str
        The string to check.

    Returns
    -------
    bool
        True if the string is a valid http url, False otherwise.
    """
    if not str(url).startswith("http"):
        return False
    # now, check for pattern
    try:
        HttpUrl(url)
    except pydantic.ValidationError:
        return False
    return True


def _add_namesapces(cls, namespace_definitions: Dict):
    """Register namespace definitions for a model class."""
    for k, v in namespace_definitions.items():
        NamespaceManager[cls][k] = str(HttpUrl(v))

def namespaces(**kwargs):
    """Define namespace-prefix mappings for a Thing subclass.

    Place this decorator above ``@urirefs``. For example,
    ``@namespaces(ex="https://example.org/vocab/")`` makes the ``ex`` prefix
    available to mappings such as ``Measurement="ex:Measurement"``.
    Prefixes and mappings are inherited by subclasses.
    """

    def _decorator(cls):
        """The actual decorator function. It assigns the namespaces to the class."""
        _add_namesapces(cls, kwargs)
        return cls

    return _decorator


_prefix_dict = {
    'http://xmlns.com/foaf/0.1/': 'foaf',
    'https://www.w3.org/ns/prov#': 'prov',
    'https://www.w3.org/1999/02/22-rdf-syntax-ns#': 'rdf',
    'https://schema.org/': 'schema',
    'http://w3id.org/nfdi4ing/metadata4ing#': 'm4i'
}

def _decorate_urirefs(cls, **kwargs):
    fields = list(cls.model_fields.keys())
    fields.append(cls.__name__)

    # add fields to the class
    for k, v in kwargs.items():
        if not isinstance(v, str):
            raise TypeError(f"{v} must be a string, not {type(v)}")
        if _is_http_url(v):
            ns, key = split_uri(v)
            prefix = _prefix_dict.get(ns, None)
            if prefix is None:
                URIRefManager[cls][k] = str(v)
            else:
                NamespaceManager[cls][prefix] = str(ns)
                if k not in fields:
                    raise KeyError(f"Field '{k}' not found in {cls.__name__}")
                URIRefManager[cls][k] = f"{prefix}:{key}"
        else:
            if k not in fields:
                raise KeyError(f"Field '{k}' not found in {cls.__name__}")
            URIRefManager[cls][k] = v

def urirefs(**kwargs):
    """Map a Thing subclass and its fields to RDF IRIs.

    Use the Python class name as the key for its RDF type and Python field
    names as keys for predicates. Values can be compact IRIs, such as
    ``value="ex:value"``, or full HTTP(S) IRIs. Pair compact mappings with
    ``@namespaces`` and define typed model fields for validation.
    """

    def _decorator(cls):
        """The actual decorator function. It assigns the URIRefs to the fields of the class."""
        _decorate_urirefs(cls, **kwargs)
        return cls

    return _decorator


def _get_predicate_fields(cls):
    """Resolve each registered field predicate to its complete RDF IRI."""
    fields = {}
    namespace_definitions = NamespaceManager[cls]
    for field, predicate in URIRefManager[cls].items():
        if field not in cls.model_fields:
            continue
        prefix, separator, local = predicate.partition(':')
        if separator and prefix in namespace_definitions:
            predicate = str(namespace_definitions[prefix]) + local
        if predicate in fields and fields[predicate] != field:
            raise ValueError(f'Multiple model fields map to predicate {predicate}')
        fields[predicate] = field
    return fields
