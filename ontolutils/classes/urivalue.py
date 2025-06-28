from dataclasses import dataclass

from pydantic import HttpUrl


@dataclass
class URIValue:
    """A class to represent a value with an associated URI."""
    value: str  # the value of the URI
    namespace: str  # the URI that identifies the predicate of the value
    prefix: str  # TODO: this might be None and figured out automatically based on known namespaces, for now it's a required field

    def __post_init__(self):
        # verify that the URI is a valid URL
        try:
            HttpUrl(self.namespace)
        except ValueError as e:
            raise ValueError(f"Invalid namespace URI: {self.namespace}. Error: {e}")


if __name__ == "__main__":
    # Example usage
    uri_value = URIValue(value="Example Value", namespace="http://example.com/resource", prefix="ex")
    print(uri_value)
