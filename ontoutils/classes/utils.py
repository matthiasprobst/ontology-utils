import appdirs
import json
import logging
import pathlib
import rdflib
import requests
from typing import List
from typing import Union

logger = logging.getLogger(__package__)
logger.setLevel('DEBUG')


class UNManager:
    """Manager class for URIRef and Namespace."""

    def __init__(self):
        self.data = {}

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
            return _uri.rsplit('#', 1)
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


def is_zip_file(mediaType: Union[str, rdflib.URIRef]):
    """checks the media type"""
    return str(mediaType) in (
        'https://www.iana.org/assignments/media-types/application/zip',
        'zip',
    )


def get_cache_dir() -> pathlib.Path:
    """Get the cache directory and create it if it does not exist"""
    cache_dir = pathlib.Path(appdirs.user_cache_dir('pivmetalib'))
    if not cache_dir.exists():
        cache_dir.mkdir(parents=True)
    return cache_dir


def download_file(url,
                  dest_filename=None,
                  known_hash=None,
                  overwrite_existing: bool = False,
                  show_pbar: bool = False) -> pathlib.Path:
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
    show_pbar: bool
        Whether to show a progress bar
    
    Returns
    -------
    pathlib.Path
        The path to the downloaded file

    Raises
    ------
    HTTPError if the request is not successful
    ValueError if the hash of the downloaded file does not match the expected hash
    """
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
    block_size = 1024

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

    if show_pbar:
        try:
            from tqdm import tqdm
        except ImportError:
            raise ImportError('tqdm is required to show progress bar. Please install it or set show_pbar to False.')
        with tqdm(total=total_size, unit="B", unit_scale=True) as progress_bar:
            with open(dest_filename, "wb") as f:
                for data in response.iter_content(block_size):
                    progress_bar.update(len(data))
                    f.write(data)
    else:
        with open(dest_filename, "wb") as f:
            f.write(content)

    return dest_filename

