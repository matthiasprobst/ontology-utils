import pydantic
from pydantic import HttpUrl

from . import utils
from .utils import split_URIRef

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


def namespaces(**kwargs):
    """Decorator for model classes. It assigns the namespaces used in the uri fields of the class.

    Example:
    --------
    @namespaces(ex="http://example.com/")
    @urirefs(name="ex:name")
    class ExampleModel(ThingModel):
        name: str

    em = ExampleModel(name="test")
    print(em.dump_jsonld())
    # {
    #     "@context": {
    #         "ex": "http://example.com/"
    #     },
    #     "@graph": [
    #         {
    #             "@id": "ex:test",
    #             "ex:name": "test"
    #         }
    #     ]
    # }
    """

    def _decorator(cls):
        """The actual decorator function. It assigns the namespaces to the class."""
        for k, v in kwargs.items():
            NamespaceManager[cls][k] = str(HttpUrl(v))
        return cls

    return _decorator


_prefix_dict = {
    'http://xmlns.com/foaf/0.1/': 'foaf',
    'http://www.w3.org/ns/prov#': 'prov',
    'http://www.w3.org/1999/02/22-rdf-syntax-ns#': 'rdf',
    'http://schema.org/': 'schema',
    'http://w3id.org/nfdi4ing/metadata4ing#': 'm4i'
}


def urirefs(**kwargs):
    """decorator for model classes. It assigns the URIRefs to the fields of the class.

    Example:
    --------
    @urirefs(name=URIRef("http://example.com/name"))
    class ExampleModel(ThingModel):
        name: str


    """

    def _decorator(cls):
        """The actual decorator function. It assigns the URIRefs to the fields of the class."""
        fields = list(cls.model_fields.keys())
        fields.append(cls.__name__)

        # add fields to the class
        for k, v in kwargs.items():
            if not isinstance(v, str):
                raise TypeError(f"{v} must be a string, not {type(v)}")
            if _is_http_url(v):
                ns, key = split_URIRef(v)
                prefix = _prefix_dict.get(ns, None)
                if prefix is None:
                    raise ValueError(f"Cannot determine the prefix for {ns}")
                NamespaceManager[cls][prefix] = str(ns)
                if k not in fields:
                    raise KeyError(f"Field '{k}' not found in {cls.__name__}")
                URIRefManager[cls][k] = f"{prefix}:{key}"
            else:
                if k not in fields:
                    raise KeyError(f"Field '{k}' not found in {cls.__name__}")
                URIRefManager[cls][k] = v
        return cls

    return _decorator
