"""Small bounded JSON transport; no redirect, automatic retry or environment proxy."""

import json
from contextlib import AbstractContextManager
from http.client import HTTPException
from typing import Any, Protocol
from urllib.error import HTTPError, URLError
from urllib.request import HTTPRedirectHandler, ProxyHandler, Request, build_opener

from .base import ProviderError


class _Response(Protocol):
    def read(self, n: int, /) -> bytes: ...


class _Opener(Protocol):
    """Superficie mínima que ejercitan tanto urllib como el doble de test_m2.py."""

    def open(self, request: Request, *, timeout: float) -> AbstractContextManager[_Response]: ...
    def close(self) -> None: ...


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, *args: object, **kwargs: object) -> None:
        return None


class JsonTransport:
    def __init__(self, opener: _Opener | None = None) -> None:
        self.opener: _Opener = opener or build_opener(ProxyHandler({}), NoRedirect())

    def post(self, url: str, payload: dict[str, object], headers: dict[str, str],
              timeout: float) -> dict[str, Any]:
        # Respuesta externa no confiable, validada campo a campo por cada adaptador
        # consumidor (gemini_adapter.py/ollama_adapter.py); dict[str, object] obligaría
        # a narrowing redundante donde el propio cuerpo ya hace isinstance/try-except.
        # Opener has no proxy handler and blocks redirects; url is a configured provider endpoint, not user input.
        request = Request(url, data=json.dumps(payload, allow_nan=False).encode(), method="POST",  # noqa: S310
                          headers={"Content-Type": "application/json", **headers})
        try:
            with self.opener.open(request, timeout=timeout) as response:
                raw = response.read(2_000_001)
        except HTTPError as error:
            code = error.code
            error.close()
            raise ProviderError(f"http_{code}", recoverable=code in {408, 409, 429} or code >= 500) from None
        except TimeoutError:
            raise ProviderError("timeout", recoverable=True) from None
        except URLError as error:
            reason = "timeout" if isinstance(error.reason, TimeoutError) else "connection_error"
            raise ProviderError(reason, recoverable=True) from None
        except (OSError, HTTPException):
            raise ProviderError("connection_error", recoverable=True) from None
        try:
            if len(raw) > 2_000_000:
                raise ValueError("Oversized response")
            data = json.loads(raw)
            if not isinstance(data, dict):
                raise ValueError("Invalid response shape")
            return data
        except (ValueError, RecursionError):
            raise ProviderError("malformed_response") from None

    def close(self) -> None:
        self.opener.close()
