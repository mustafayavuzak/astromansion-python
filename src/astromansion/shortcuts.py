"""The client the module-level shortcuts share.

Convenience only. An application should build an :class:`~astromansion.AstroMansion`
instead: the client holds a connection pool, and two of them can carry two
different keys without either depending on process-wide state.

These live here rather than in ``__init__`` so the package entry point stays a
list of what is public, and this file stays the place where the shared client
is built and torn down.
"""

from __future__ import annotations

from typing import Any

from ._core import Credentials
from .client import AstroMansion


class _Default:
    """Owner of the client the helpers below share.

    A class rather than a module variable so the state has a name, and so
    replacing the key closes the old pool instead of leaking it.
    """

    _client: AstroMansion | None = None

    @classmethod
    def get(cls) -> AstroMansion:
        """Return the shared client, building it once."""
        if cls._client is None:
            cls._client = AstroMansion()
        return cls._client

    @classmethod
    def drop(cls) -> None:
        """Close and forget the shared client."""
        if cls._client is not None:
            cls._client.close()
        cls._client = None


def set_api_key(api_key: str) -> None:
    """Set the key the module-level helpers use.

    The shared client is dropped, so the new key takes effect on the next
    call rather than the next process.
    """
    Credentials.share(api_key)
    _Default.drop()


def reset() -> None:
    """Return the shortcuts to their starting state.

    Closes the shared client and forgets any key given to
    :func:`set_api_key`, so the next call reads the environment again.
    Explicitly built clients are untouched: each carries its own key and its
    own pool.
    """
    Credentials.share(None)
    _Default.drop()


def default_client() -> AstroMansion:
    """Return the client the shortcuts share.

    An extension point rather than an everyday call: reach for it to inspect
    or configure the client the module-level functions use. Most callers want
    :func:`set_api_key`, a shortcut, or their own :class:`AstroMansion`.
    """
    return _Default.get()


def request(method: str, path: str, **kwargs: Any) -> Any:
    """Call any endpoint with the shared client.

    Not generated from the endpoint table because it is not an endpoint: it
    is how a caller reaches a path this release does not yet name.
    """
    return default_client().request(method, path, **kwargs)


def bodies(*categories: str, **kwargs: Any) -> dict[str, list[Any]]:
    """Read whole catalog categories with the shared client.

    Not generated from the endpoint table because it is not an endpoint: it
    is one call over as many ``/v1/chart`` pages as the categories need. See
    :meth:`astromansion.AstroMansion.bodies`.
    """
    return default_client().bodies(*categories, **kwargs)
