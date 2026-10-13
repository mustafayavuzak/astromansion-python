"""src/astromansion/shortcuts.py: The client the module-level shortcuts share.

Convenience only. An application should build an :class:`~astromansion.AstroMansion`
instead: it holds a connection pool, and two of them can carry two different
keys without either depending on process-wide state.

The shared client's lifecycle::

    first shortcut call ──► client built from the shared key or the environment
    set_api_key(key)    ──► key stored, client closed, rebuilt on the next call
    reset()             ──► key forgotten, client closed
"""

from __future__ import annotations

from typing import Any, ClassVar

from ._credentials import Credentials
from .client import AstroMansion


class _Default:
    """Own the client the shortcuts share.

    A class rather than a module variable, so the state has a name and
    replacing the key closes the old pool instead of leaking it. ``_client``
    is the shared client, or ``None`` before the first call and after a drop.
    """

    _client: ClassVar[AstroMansion | None] = None

    @classmethod
    def get(cls) -> AstroMansion:
        """Return the shared client, building it on first use.

        Returns:
            The shared client.

        Raises:
            AuthenticationError: The client is built now and no key was found.
        """
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
    """Set the key the module-level shortcuts use.

    The shared client is dropped, so the new key takes effect on the next call
    rather than the next process.

    Args:
        api_key: The API key. Blank text clears it, as :func:`reset` does.
    """
    Credentials.share(api_key)
    _Default.drop()


def reset() -> None:
    """Return the shortcuts to their starting state.

    Closes the shared client and forgets any key given to :func:`set_api_key`,
    so the next call reads the environment again. Clients built explicitly are
    untouched: each carries its own key and its own pool.
    """
    Credentials.share(None)
    _Default.drop()


def default_client() -> AstroMansion:
    """Return the client the shortcuts share.

    An extension point rather than an everyday call: reach for it to inspect
    or configure the client the module-level functions use. Most callers want
    :func:`set_api_key`, a shortcut, or their own :class:`AstroMansion`.

    Returns:
        The shared client, built on first use.

    Raises:
        AuthenticationError: The client is built now and no key was found.
    """
    return _Default.get()


def request(method: str, path: str, **kwargs: Any) -> Any:
    """Call any endpoint with the shared client.

    Not generated from the endpoint table because it is not an endpoint: it is
    how a caller reaches a path this release does not yet name.

    Args:
        method: HTTP verb.
        path: A path beginning with ``/v1/``.
        **kwargs: Passed to :meth:`AstroMansion.request`.

    Returns:
        What :meth:`AstroMansion.request` returns.

    Raises:
        AstroMansionError: The path was refused, no key was found, the API
            refused the call, or no answer arrived.
    """
    return default_client().request(method, path, **kwargs)


def bodies(*categories: str, **kwargs: Any) -> dict[str, list[Any]]:
    """Read whole catalog categories with the shared client.

    Not generated from the endpoint table because it is not an endpoint: it is
    one call over as many ``/v1/chart`` pages as the categories need.

    Args:
        *categories: Category keys, such as ``fixed_stars``.
        **kwargs: Passed to :meth:`AstroMansion.bodies`.

    Returns:
        Each category asked for, mapped to all of its rows.

    Raises:
        AstroMansionError: The walk was refused or could not finish.
    """
    return default_client().bodies(*categories, **kwargs)
