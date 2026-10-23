"""src/astromansion/models/constants/package.py: The package's own identity.

The build reads ``VERSION`` from this file (``[tool.hatch.version]`` in
``pyproject.toml``) and the release workflow checks the tag against it, so the
version is written here and nowhere else.
"""

from __future__ import annotations

from typing import Final


class PackageConstants:
    """The name and version this package presents to PyPI and to the API.

    ``NAME`` matches the distribution on PyPI, so a server log names what to
    install. ``USER_AGENT`` is the only identification a request carries: the
    package and its version, and nothing about the machine or the caller.
    """

    VERSION: Final[str] = "0.3.2"
    NAME: Final[str] = "astromansion"
    USER_AGENT: Final[str] = f"{NAME}/{VERSION}"
