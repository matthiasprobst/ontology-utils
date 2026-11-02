"""Download behavior uses fixed responses and an isolated cache."""
from hashlib import sha256

import pytest
import requests

from ontolutils.classes import utils


@pytest.fixture
def download_response(monkeypatch, tmp_path):
    response = requests.Response()
    response.status_code = 200
    response.url = "https://example.org/data.csv"
    response._content = b"name,value\nvelocity,1\n"
    response.headers["content-length"] = str(len(response.content))

    def request(method, url, **kwargs):
        assert method == "GET"
        assert url == response.url
        return response

    monkeypatch.setattr(utils, "request_with_backoff", request)
    monkeypatch.setattr("ontolutils.cache.get_cache_dir", lambda: tmp_path / "cache")
    return response


def test_download_uses_isolated_cache(download_response, tmp_path):
    response = download_response
    path = utils.download_file(response.url, known_hash=sha256(response.content).hexdigest())
    assert path == tmp_path / "cache" / str(len(response.content)) / "data.csv"
    assert path.read_bytes() == response.content
    assert utils.download_file(response.url) == path


@pytest.mark.parametrize("options,expected", [({}, b"existing"),
                                              ({"exist_ok": False}, b"existing"),
                                              ({"exist_ok": True}, None),
                                              ({"overwrite_existing": False}, b"existing"),
                                              ({"overwrite_existing": True}, None)])
def test_download_respects_existing_file(download_response, tmp_path, options, expected):
    destination = tmp_path / "nested" / "data.csv"
    path = utils.download_file(download_response.url, dest_filename=destination)
    assert path == destination
    path.write_bytes(b"existing")
    assert utils.download_file(download_response.url, dest_filename=destination, **options) == path
    assert path.read_bytes() == (download_response.content if expected is None else expected)


def test_download_rejects_wrong_hash_without_writing(download_response, tmp_path):
    destination = tmp_path / "data.csv"
    with pytest.raises(ValueError, match="expected"):
        utils.download_file(download_response.url, dest_filename=destination, known_hash="invalid")
    assert not destination.exists()


def test_download_propagates_http_errors(download_response, tmp_path):
    download_response.status_code = 404
    destination = tmp_path / "data.csv"
    with pytest.raises(requests.HTTPError):
        utils.download_file(download_response.url, dest_filename=destination)
    assert not destination.exists()
