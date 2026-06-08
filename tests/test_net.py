import os
from types import SimpleNamespace

from loan_agent.config import ssl_http_client


def test_ssl_http_client_none_without_bundle():
    old = os.environ.pop("SSL_CERT_FILE", None)
    try:
        assert ssl_http_client(SimpleNamespace(ca_bundle="")) is None
    finally:
        if old is not None:
            os.environ["SSL_CERT_FILE"] = old


def test_ssl_http_client_builds_with_bundle():
    import certifi

    client = ssl_http_client(SimpleNamespace(ca_bundle=certifi.where()))
    assert client is not None
    client.close()
