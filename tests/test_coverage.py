"""Every published endpoint is reachable, by method and by shortcut.

Coverage is not counted by hand. The endpoint table is generated from the
API's own schema, and these tests check that both clients and the module-level
surface answer for all of it: an endpoint added without rerunning the
generator, or a method that goes missing, shows up here.
"""

from __future__ import annotations

import pytest

import astromansion
from astromansion import AstroMansion, AsyncAstroMansion
from astromansion._endpoints import BY_NAME, ENDPOINTS


def test_the_table_covers_every_published_operation() -> None:
    assert len(ENDPOINTS) == 67, f"tabloda {len(ENDPOINTS)} uc var"
    assert len(BY_NAME) == len(ENDPOINTS), "ayni ada iki uc dusmus"


@pytest.mark.parametrize("endpoint", ENDPOINTS, ids=lambda e: e.name)
def test_both_clients_expose_every_endpoint(endpoint) -> None:
    for client in (AstroMansion, AsyncAstroMansion):
        method = getattr(client, endpoint.name, None)
        assert callable(method), f"{client.__name__}.{endpoint.name} yok"


@pytest.mark.parametrize("endpoint", ENDPOINTS, ids=lambda e: e.name)
def test_every_method_documents_the_endpoint_it_wraps(endpoint) -> None:
    """A docstring must name the API path it reaches."""
    text = getattr(AstroMansion, endpoint.name).__doc__ or ""
    assert endpoint.path in text, f"{endpoint.name} yolunu belgelemiyor"
    assert endpoint.method in text


@pytest.mark.parametrize("endpoint", ENDPOINTS, ids=lambda e: e.name)
def test_every_endpoint_has_a_module_level_shortcut(endpoint) -> None:
    """The shortcut surface covers the whole API, not a chosen few.

    A handful of hand-picked shortcuts read as the whole package while hiding
    most of it.
    """
    shortcut = getattr(astromansion, endpoint.name, None)
    assert callable(shortcut), f"astromansion.{endpoint.name} yok"
    assert endpoint.name in astromansion.__all__


def test_importing_the_package_opens_no_connection() -> None:
    """`import astromansion` makes no network call; the client is lazy."""
    astromansion.reset()
    assert astromansion.shortcuts._Default._client is None
