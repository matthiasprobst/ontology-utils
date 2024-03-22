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
                NamespaceManager[cls][k] = str(ns)
            if k not in fields:
                raise KeyError(f"Field '{k}' not found in {cls.__name__}")
            URIRefManager[cls][k] = str(v)
        return cls

    return _decorator

