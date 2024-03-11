# https://www.iana.org/assignments/media-types/text.csv
from typing import Dict

from ontolutils.cache import get_cache_dir
from ontolutils.classes.utils import download_file

iana_cache = get_cache_dir() / 'iana'
iana_cache.mkdir(exist_ok=True)


def read_csv_file(filename, prefix: str) -> Dict[str, str]:
    with open(filename) as f:
        lines = f.read().split('\n')
    # header = lines[0].split(',')
    names = []
    url = []
    for line in lines[1:]:
        if line:
            n, t, r = line.split(',', 2)
            names.append(n)
            url.append(prefix + t)
    return {n: u for n, u in zip(names, url)}


def get_media_type(category: str) -> dict:
    """Return a dictionary of media types for the given category."""
    csv_fname = iana_cache / f'{category}.csv'
    if not csv_fname.exists():
        download_link = f'https://www.iana.org/assignments/media-types/{category}.csv'
        csv_fname = download_file(download_link,
                                  dest_filename=iana_cache / f'{category}.csv')
    return read_csv_file(csv_fname, 'https://www.iana.org/assignments/media-types/')


class IANACLS:

    def __init__(self):
        self._application = None
        self._audio = None
        self._font = None
        self._image = None
        self._message = None
        self._model = None
        self._multipart = None
        self._text = None
        self._video = None

    @property
    def application(self):
        """Return a dictionary of application media types."""
        if self._application is None:
            self._application = get_media_type('application')
        return self._application

    @property
    def audio(self):
        """Return a dictionary of audio media types."""
        if self._audio is None:
            self._audio = get_media_type('audio')
        return self._audio

    @property
    def font(self):
        """Return a dictionary of font media types."""
        if self._font is None:
            self._font = get_media_type('font')
        return self._font

    @property
    def image(self):
        """Return a dictionary of image media types."""
        if self._image is None:
            self._image = get_media_type('image')
        return self._image

    @property
    def message(self):
        """Return a dictionary of message media types."""
        if self._message is None:
            self._message = get_media_type('message')
        return self._message

    @property
    def model(self):
        """Return a dictionary of model media types."""
        if self._model is None:
            self._model = get_media_type('model')
        return self._model

    @property
    def multipart(self):
        """Return a dictionary of multipart media types."""
        if self._multipart is None:
            self._multipart = get_media_type('multipart')
        return self._multipart

    @property
    def text(self):
        """Return a dictionary of text media types."""
        if self._text is None:
            self._text = get_media_type('text')
        return self._text

    @property
    def video(self):
        """Return a dictionary of video media types."""
        if self._video is None:
            self._video = get_media_type('video')
        return self._video


IANA = IANACLS()
