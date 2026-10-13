"""src/astromansion/settings.py: The configuration the environment gives a client.

Two variables configure a client that is not told otherwise::

    ASTROMANSION_API_KEY    the key to send
    ASTROMANSION_BASE_URL   the API root, for a staging or a local server

This is the one module that reads them. Which source wins over which is
decided by ``Credentials``, not here.
"""

from __future__ import annotations

import os

from .models.constants.api import ApiConstants


class Settings:
    """Read the client's configuration from the environment.

    Each read happens when a client is built, never once at import, so a
    variable set after ``import astromansion`` still counts.
    """

    @staticmethod
    def api_key() -> str | None:
        """Return the key the environment holds.

        Returns:
            ``ASTROMANSION_API_KEY`` stripped, or ``None`` when it is unset or
            blank.
        """
        return (os.environ.get(ApiConstants.KEY_ENV) or "").strip() or None

    @staticmethod
    def base_url() -> str | None:
        """Return the API root the environment names.

        Returns:
            ``ASTROMANSION_BASE_URL``, or ``None`` when it is unset or empty.
        """
        return os.environ.get(ApiConstants.BASE_URL_ENV) or None
