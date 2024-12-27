import json
import logging
import pathlib
from typing import Union, List, Dict

import rdflib
import requests

logger = logging.getLogger(__package__)
logger.setLevel('DEBUG')


class UNManager:
    """Manager class for URIRef and Namespace."""

    def __init__(self):
        self.data = {}

    def get(self, cls, other=None) -> Dict:
        """Get the Namespace for the class."""
        ret = self.data.get(cls, other)
        if ret is None:
            return other
        return ret

    def __repr__(self):
        names = ', '.join([f'{c.__name__}' for c in self.data])
        return f'{self.__class__.__name__}({names})'

    def __getitem__(self, cls):
        if cls not in self.data:
            self.data[cls] = {}
        # there might be subclass to this cls. get those data as well
        for k, v in self.data.items():
            if k != cls:
                if issubclass(cls, k):
                    self.data[cls].update(v)
        return self.data[cls]


def split_URIRef(uri: rdflib.URIRef) -> List[Union[str, None]]:
    """Split a URIRef into namespace and key."""
    _uri = str(uri)
    if _uri.startswith('http'):
        if '#' in _uri:
            _split = _uri.rsplit('#', 1)
            return [f'{_split[0]}#', _split[1]]
        _split = _uri.rsplit('/', 1)
        return [f'{_split[0]}/', _split[1]]
    if ':' in _uri:
        return _uri.rsplit(':', 1)
    return [None, uri]


def merge_jsonld(jsonld_strings: List[str]) -> str:
    """Merge multiple json-ld strings into one json-ld string."""
    jsonld_dicts = [json.loads(jlds) for jlds in jsonld_strings]

    contexts = []
    for jlds in jsonld_dicts:
        if jlds['@context'] not in contexts:
            contexts.append(jlds['@context'])

    out = {'@context': contexts,
           '@graph': []}

    for jlds in jsonld_dicts:
        if '@graph' in jlds:
            out['@graph'].append(jlds['@graph'])
        else:
            data = dict(jlds.items())
            data.pop('@context')
            out['@graph'].append(data)

    return json.dumps(out, indent=2)


def download_file(url,
                  dest_filename=None,
                  known_hash=None,
                  overwrite_existing: bool = False) -> pathlib.Path:
    """Download a file from a URL and check its hash
    
    Parameter
    ---------
    url: str
        The URL of the file to download
    dest_filename: str or pathlib.Path =None
        The destination filename. If None, the filename is taken from the URL
    known_hash: str
        The expected hash of the file
    overwrite_existing: bool
        Whether to overwrite an existing file
    
    Returns
    -------
    pathlib.Path
        The path to the downloaded file

    Raises
    ------
    HTTPError if the request is not successful
    ValueError if the hash of the downloaded file does not match the expected hash
    """
    from ..cache import get_cache_dir

    logger.debug(f'Performing request to {url}')
    response = requests.get(url, stream=True)
    if not response.ok:
        response.raise_for_status()

    content = response.content

    # Calculate the hash of the downloaded content
    if known_hash:
        import hashlib
        calculated_hash = hashlib.sha256(content).hexdigest()
        if not calculated_hash == known_hash:
            raise ValueError('File does not match the expected has')

    total_size = int(response.headers.get("content-length", 0))
    # block_size = 1024

    # Save the content to a file
    if dest_filename is None:
        filename = response.url.rsplit('/', 1)[1]
        dest_parent = get_cache_dir() / f'{total_size}'
        dest_filename = dest_parent / filename
        if dest_filename.exists():
            logger.debug(f'Taking existing file {dest_filename} and returning it.')
            return dest_filename
    else:
        dest_filename = pathlib.Path(dest_filename)
    dest_parent = dest_filename.parent
    if not dest_parent.exists():
        dest_parent.mkdir(parents=True)

    if dest_filename.exists():
        if overwrite_existing:
            logger.debug(f'Destination filename found: {dest_filename}. Deleting it, as overwrite_existing is True.')
            dest_filename.unlink()
        else:
            logger.debug(f'Destination filename found: {dest_filename}. Returning it')
            return dest_filename

    with open(dest_filename, "wb") as f:
        f.write(content)

    return dest_filename


def as_id(obj, field_name):
    if isinstance(obj, dict):
        return as_id_before(obj, field_name)
    raise ValueError(f"You must use mode='before' for as_id")


def as_id_before(obj: Dict, field_name: str):
    current_id = obj.get("id", None)
    if current_id is not None:
        return obj
    field_value = obj.get(field_name, None)
    if field_value is not None:
        if not str(field_value).startswith(("_:", "http")):
            logger.info(f"Field {field_name} is not a URIRef or BNode: {obj[field_name]}. "
                        f"You can only set an id for URIRefs or BNodes.")
        else:
            obj["id"] = field_value
    return obj
