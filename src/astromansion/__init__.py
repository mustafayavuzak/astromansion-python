"""Official Python client for the AstroMansion API.

Nothing is computed here. Every call reaches ``https://api.astromansion.com``,
which owns the ephemeris, the plan, the quota and the rate limit. The key
identifies the caller and determines which features they may access; this
package never enables a feature the server has not granted.

Two surfaces, one behaviour:

    >>> from astromansion import AstroMansion
    >>> with AstroMansion() as client:   # reads ASTROMANSION_API_KEY
    ...     chart = client.natal(date="2000-01-01", time="12:00",
    ...                          lat=51.4779, lon=0.0,
    ...                          timezone="Europe/London")

and, for a notebook or a short script:

    >>> import astromansion as am
    >>> am.set_api_key("...")
    >>> chart = am.natal(date="2000-01-01", lat=51.4779, lon=0.0)

The client object is the one to use in an application: it holds a connection
pool, and two of them can carry two different keys.

This module only names what is public. The behaviour lives in the modules it
imports from.
"""

from __future__ import annotations

from ._shortcuts import *  # noqa: F403
from ._shortcuts import __all__ as _endpoint_names
from .async_client import AsyncAstroMansion
from .client import AstroMansion
from .constants import Package
from .errors import (
    AstroMansionConnectionError,
    AstroMansionError,
    AuthenticationError,
    ConflictError,
    ErrorPolicy,
    NotFoundError,
    PermissionDeniedError,
    QuotaExceededError,
    RateLimitError,
    ServerError,
    ValidationError,
)
from .response import Result
from .shortcuts import bodies, request, reset, set_api_key
from .shortcuts import (
    default_client as default_client,  # extension point, not in __all__
)

__version__ = Package.VERSION

# Names this package exports: the classes and key handling above, plus one
# shortcut per endpoint, listed by the generated module so the two cannot
# disagree about what exists.
__all__ = [
    "AstroMansion",
    "AstroMansionConnectionError",
    "AstroMansionError",
    "AsyncAstroMansion",
    "AuthenticationError",
    "ConflictError",
    "ErrorPolicy",
    "NotFoundError",
    "PermissionDeniedError",
    "QuotaExceededError",
    "RateLimitError",
    "Result",
    "ServerError",
    "ValidationError",
    "__version__",
    "bodies",
    "request",
    "reset",
    "set_api_key",
    *_endpoint_names,
]
