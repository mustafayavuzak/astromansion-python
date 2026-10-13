"""src/astromansion/_responses.py: Read what the API sent back.

Both clients hand every response here, so a status means the same thing in
each. A response becomes one of four things::

    status >= 400                      ──► the exception naming its cause
    JSON body                          ──► Result, envelope opened
    text/plain body                    ──► str, as the server rendered it
    any other body (PDF, PNG, SVG...)  ──► bytes, or the path they were saved to
"""

from __future__ import annotations

from collections.abc import Mapping
from http import HTTPStatus
from pathlib import Path
from typing import Any

import httpx

from ._backoff import Backoff
from .errors import ErrorPolicy
from .models.constants.api import ApiConstants
from .models.constants.envelope import EnvelopeConstants
from .response import Result


class Responses:
    """Turn a response into an exception, a result, text, or a document."""

    @staticmethod
    def error_parts(payload: Any) -> tuple[str | None, str | None, Any]:
        """Pull ``code``, ``message``, and ``detail`` out of an error body.

        A body that is not the documented envelope still yields what it can:
        a bare ``detail``, or nothing.

        Args:
            payload: The decoded body, of any shape.

        Returns:
            The code, the message, and the detail, each ``None`` when absent.

        Examples:
            >>> Responses.error_parts({"error": {"code": "quota", "message": "spent"}})
            ('quota', 'spent', None)
            >>> Responses.error_parts({"detail": "bad field"})
            (None, None, 'bad field')
            >>> Responses.error_parts("not json")
            (None, None, None)
        """
        if isinstance(payload, dict):
            error = payload.get(EnvelopeConstants.ERROR_KEY)
            if isinstance(error, dict):
                return (
                    error.get(EnvelopeConstants.CODE_KEY),
                    error.get(EnvelopeConstants.MESSAGE_KEY),
                    error.get(EnvelopeConstants.DETAIL_KEY),
                )
            if EnvelopeConstants.DETAIL_KEY in payload:
                return None, None, payload[EnvelopeConstants.DETAIL_KEY]
        return None, None, None

    @classmethod
    def error_code(cls, response: httpx.Response) -> str | None:
        """Read the machine code a refusal carries, if it carries one.

        Used to decide whether repeating the request could help, which has to
        happen before the body is decoded for the caller.

        Args:
            response: The HTTP response as it arrived.

        Returns:
            The error code, or ``None`` when the body names none or is not JSON.
        """
        try:
            payload = response.json()
        except Exception:
            return None
        return cls.error_parts(payload)[0]

    @classmethod
    def raise_for_status(
        cls,
        status: int,
        payload: Any,
        headers: Mapping[str, str],
        request_id: str | None,
    ) -> None:
        """Turn a failed response into the exception that names its cause.

        A body that is not the documented envelope must not crash the client:
        the status alone still says something useful, and a caller handling
        errors should not meet a second, different error from the client.

        Args:
            status: The HTTP status.
            payload: The decoded body, or ``None`` when it was not JSON.
            headers: The response headers, read for ``Retry-After``.
            request_id: The server's request identifier, if it sent one.

        Raises:
            AstroMansionError: The subclass :class:`ErrorPolicy` chooses, for
                any status of 400 or above.
        """
        if status < HTTPStatus.BAD_REQUEST:
            return
        code, message, details = cls.error_parts(payload)
        raise ErrorPolicy.for_response(status, code)(
            message or f"AstroMansion API returned HTTP {status}",
            status_code=status,
            error_code=code,
            details=details,
            request_id=request_id,
            retry_after=Backoff.retry_after(headers),
        )

    @staticmethod
    def is_text(content_type: str | None) -> bool:
        """Return whether a body should be decoded to text.

        Only ``text/plain`` qualifies. A CSV export and an SVG wheel are
        documents the caller writes to disk, and turning those into ``str``
        would break every ``open(path, "wb")`` already written against them.

        Args:
            content_type: The response's ``Content-Type``, if it sent one.

        Returns:
            True when the body is prose or a rendered table.

        Examples:
            >>> Responses.is_text("text/plain; charset=utf-8")
            True
            >>> Responses.is_text("text/csv")
            False
            >>> Responses.is_text(None)
            False
        """
        if not content_type:
            return False
        return (
            content_type.split(";")[0].strip().lower() == ApiConstants.TEXT_MEDIA_TYPE
        )

    @classmethod
    def decode(
        cls,
        response: httpx.Response,
        binary: bool = False,
        technique: str | None = None,
        enveloped: bool | None = None,
    ) -> Any:
        """Raise on failure, otherwise return the decoded body.

        Args:
            response: The HTTP response as it arrived.
            binary: Whether a success is a document rather than JSON. A failed
                document request still answers with the JSON error envelope.
            technique: The endpoint's name, used when the body names none.
            enveloped: What the schema says about the success wrapper: True,
                False, or ``None`` when the body has to be recognised.

        Returns:
            A :class:`Result` for JSON, ``str`` for ``text/plain``, and
            ``bytes`` for any other document.

        Raises:
            AstroMansionError: The status is 400 or above.

        Examples:
            >>> answer = httpx.Response(
            ...     200, json={"technique": "natal", "result": {"Sun": "Leo"}}
            ... )
            >>> Responses.decode(answer).Sun
            'Leo'
            >>> table = httpx.Response(
            ...     200, text="ok", headers={"Content-Type": "text/plain"}
            ... )
            >>> Responses.decode(table)
            'ok'
            >>> refused = httpx.Response(404, json={"error": {"code": "not_found"}})
            >>> Responses.decode(refused)  # doctest: +ELLIPSIS
            Traceback (most recent call last):
                ...
            astromansion.errors.NotFoundError: ...
        """
        payload: Any = None
        if not binary or response.status_code >= HTTPStatus.BAD_REQUEST:
            try:
                payload = response.json()
            except ValueError:
                payload = None
        cls.raise_for_status(
            response.status_code,
            payload,
            response.headers,
            response.headers.get(ApiConstants.REQUEST_ID_HEADER),
        )
        if payload is None:
            if cls.is_text(response.headers.get("Content-Type")):
                # A rendered table is meant to be printed. Bytes would print
                # their repr, escapes and all, and the box drawing the server
                # sent would be unreadable.
                return response.text
            return response.content
        return Result.build(payload, technique=technique, enveloped=enveloped)

    @staticmethod
    def save_document(content: bytes, output: str | Path | None) -> bytes | Path:
        """Return a document, or the path it was written to.

        Bytes come back unless a path is named, so a call cannot overwrite a
        file the caller did not choose.

        Args:
            content: The document the API sent.
            output: Path to write it to, or ``None`` to keep the bytes.

        Returns:
            The bytes, or the path written.

        Raises:
            OSError: The path cannot be written.
        """
        if output is None:
            return content
        destination = Path(output)
        destination.write_bytes(content)
        return destination
