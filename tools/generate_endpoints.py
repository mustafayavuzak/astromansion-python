"""Generate the client method table from the published OpenAPI schema.

Every endpoint the SDK exposes is derived here, never typed by hand. Writing
the published operations out manually would guarantee that one is missed and
that the list drifts the first time the API changes.

Run after an API change::

    python tools/generate_endpoints.py

It rewrites ``src/astromansion/_endpoints.py``. Nothing else imports the
schema, so the generated table is the single description of the surface.
"""

from __future__ import annotations

import json
import pathlib
import re
import sys
import urllib.request
from pathlib import Path

SCHEMA_URL = "https://api.astromansion.com/openapi.json"
TARGET = Path(__file__).resolve().parent.parent / "src/astromansion/_endpoints.py"

#: Names that the path alone cannot produce well. Keyed by verb and path so
#: one entry can never be applied to the wrong operation.
RENAMES = {
    ("get", "/v1/custom-body/list"): "custom_bodies",
    ("post", "/v1/custom-body/save"): "save_custom_body",
    ("post", "/v1/custom-body/{name}"): "chart_with_custom_body",
    ("delete", "/v1/custom-body/{name}"): "delete_custom_body",
    ("get", "/v1/jobs"): "list_jobs",
    ("post", "/v1/jobs"): "submit_job",
    ("get", "/v1/jobs/{job_id}"): "job",
    ("post", "/v1/jobs/batch"): "submit_batch_job",
    ("get", "/v1/geo/search"): "search_places",
    ("post", "/v1/moon-phases/query"): "moon_phases_for",
    ("get", "/v1/moon-phases"): "moon_phases",
}

#: Endpoints returning a document rather than JSON.
#: Endpoints the client implements by hand. A generated twin would shadow or
#: be shadowed by the real one depending on import order, and mypy would flag
#: the pair as an incompatible override. ``render_sharecard`` is written out
#: because its two charts stay positional while ``partner`` is optional, a
#: shape the generator has no rule for.
HAND_WRITTEN = {
    "/v1/render/sharecard",
    "/v1/render/astrocartography",
}

BINARY = {
    "/v1/export/pdf",
    "/v1/export/csv",
    "/v1/render/png",
    "/v1/render/svg",
    "/v1/render/biwheel",
    "/v1/render/sharecard",
    "/v1/render/astrocartography",
}


def python_name(path: str, verb: str, shared: bool = False) -> str:
    """Turn a path and verb into a method name.

    The explicit table wins. Otherwise the path segments become the name, and
    a placeholder or a shared path adds only what is needed to keep the name
    unique: applying every rule at once produced ``delete_delete_custom_body``.
    """
    override = RENAMES.get((verb, path))
    if override:
        return override
    segments = path.split("/")[2:]
    parts = [p for p in segments if not p.startswith("{")]
    holders = [p.strip("{}") for p in segments if p.startswith("{")]
    name = "_".join(parts).replace("-", "_")
    if verb == "delete":
        return f"delete_{name}"
    if holders:
        name = f"{name}_by_{holders[0]}"
    elif shared:
        name = f"{'list' if verb == 'get' else verb}_{name}"
    return name


def classify(path: str, verb: str, op: dict, schemas: dict) -> tuple[str, list[str]]:
    """Return the request shape and the top-level body fields."""
    if verb in {"get", "delete"}:
        return verb, [p["name"] for p in op.get("parameters", [])]
    body = op.get("requestBody")
    if not body:
        return "empty", []
    ref = body["content"]["application/json"]["schema"].get("$ref", "")
    declared = schemas.get(ref.split("/")[-1], {})
    fields = list(declared.get("properties", {}))
    required = set(declared.get("required") or ())
    # Only a schema that demands a partner gets the two-person signature.
    # ``/v1/query`` merely allows one, and forcing it there would make the
    # second chart mandatory for a call that does not need it.
    if "partner" in required:
        return "pair", fields
    if fields[:1] == ["birth"] and set(fields) <= {"birth", "options"}:
        return "chart", fields
    if "birth" in fields:
        return "birth_extra", fields
    return "body", fields


def enveloped(op: dict, schemas: dict) -> bool | None:
    """Return whether a success is wrapped in ``{technique, result}``.

    Read from the published response schema, not guessed from a body: an
    endpoint whose own data owned a ``result`` field would otherwise be
    unwrapped and its real payload thrown away. ``None`` means the schema is
    free-form and the shape has to be recognised at runtime.
    """
    try:
        schema = op["responses"]["200"]["content"]["application/json"]["schema"]
    except KeyError:
        return None
    ref = schema.get("$ref", "")
    declared = schemas.get(ref.split("/")[-1], {}) if ref else schema
    fields = set(declared.get("properties") or ())
    if not fields:
        return None
    return {"technique", "result"} <= fields


def summary(op: dict, limit: int = 58) -> str:
    """One line describing the endpoint, taken from the schema.

    Trimmed so the generated docstring fits the line length the project
    lints for; the full text stays in the API reference.
    """
    text = (op.get("summary") or op.get("description") or "").strip()
    line = text.splitlines()[0] if text else ""
    line = re.sub(r"\s+", " ", line).strip().rstrip(".")
    line = line or "Call the endpoint"
    if len(line) > limit:
        line = line[:limit].rsplit(" ", 1)[0] + "…"
    return line


def build() -> str:
    source = sys.argv[1] if len(sys.argv) > 1 else SCHEMA_URL
    if source.startswith("http"):
        # The API rejects the default urllib agent, so identify the tool.
        request = urllib.request.Request(
            source,
            headers={"User-Agent": "astromansion-sdk-generator"},
        )
        with urllib.request.urlopen(request) as stream:
            schema = json.load(stream)
    else:
        schema = json.loads(pathlib.Path(source).read_text(encoding="utf-8"))
    schemas = schema["components"]["schemas"]

    rows: list[str] = []
    seen: set[str] = set()
    for path, operations in sorted(schema["paths"].items()):
        shared = len(operations) > 1
        for verb, op in operations.items():
            name = python_name(path, verb, shared)
            if name in seen:
                raise SystemExit(f"duplicate method name {name!r} for {path}")
            seen.add(name)
            kind, fields = classify(path, verb, op, schemas)
            rows.append(
                f"    Endpoint(\n"
                f"        name={name!r},\n"
                f"        method={verb.upper()!r},\n"
                f"        path={path!r},\n"
                f"        kind={kind!r},\n"
                f"        fields={tuple(fields)!r},\n"
                f"        binary={path in BINARY!r},\n"
                f"        enveloped={enveloped(op, schemas)!r},\n"
                f"        summary={summary(op)!r},\n"
                f"    ),"
            )

    body = "\n".join(rows)
    return f'''"""Every endpoint the AstroMansion API publishes.

Generated by ``tools/generate_endpoints.py`` from the live OpenAPI schema. Do
not edit: rerun the generator after an API change so the SDK and the server
cannot describe different surfaces.

Endpoints: {len(rows)}
"""

from __future__ import annotations

from typing import NamedTuple


class Endpoint(NamedTuple):
    """One operation the API publishes.

    :param name: Method name exposed on the clients.
    :param method: HTTP verb.
    :param path: Path template, possibly containing one placeholder.
    :param kind: Request shape: ``chart``, ``pair``, ``birth_extra``,
        ``body``, ``get``, ``delete`` or ``empty``.
    :param fields: Top-level body fields the schema declares.
    :param binary: Whether a success returns a document rather than JSON.
    :param enveloped: Whether a success is wrapped in ``{{technique, result}}``.
        ``None`` when the schema is free-form and the body decides.
    :param summary: One-line description taken from the schema.
    """

    name: str
    method: str
    path: str
    kind: str
    fields: tuple[str, ...]
    binary: bool
    enveloped: bool | None
    summary: str


ENDPOINTS: tuple[Endpoint, ...] = (
{body}
)

BY_NAME: dict[str, Endpoint] = {{endpoint.name: endpoint for endpoint in ENDPOINTS}}
'''


CHART_SIGNATURE = """    {aw}def {name}(
        self, payload: dict[str, Any] | None = None, *,
        date: str | None = None, lat: float | None = None,
        lon: float | None = None, time: str | None = None,
        timezone: float | str | None = None, houses: str | None = None,
        options: dict[str, Any] | None = None,{outarg}
    ) -> {ret}:
        \"\"\"{summary}.

        Wraps ``{method} {path}``.
        \"\"\"
        return {outopen}{aa}self._chart(
            {path!r}, payload, options, date=date, lat=lat, lon=lon,
            time=time, timezone=timezone, houses=houses, binary={binary!r},
            technique={name!r}, enveloped={enveloped!r},
        ){outclose}
"""

PAIR_SIGNATURE = """    {aw}def {name}(
        self, birth: dict[str, Any], partner: dict[str, Any], *,
        options: dict[str, Any] | None = None,{outarg} **extra: Any,
    ) -> {ret}:
        \"\"\"{summary}. Wraps ``{method} {path}``.

        Both people are mappings of the fields ``natal`` accepts.
        \"\"\"
        return {outopen}{aa}self._pair(
            {path!r}, birth, partner, options, binary={binary!r},
            technique={name!r}, enveloped={enveloped!r}, **extra,
        ){outclose}
"""

BODY_SIGNATURE = """    {aw}def {name}(self{argspec}, body: dict[str, Any] | None = None,{outarg} **fields: Any) -> {ret}:
        \"\"\"{summary}. Wraps ``{method} {path}``.

        Body fields: {fieldlist}.
        \"\"\"
        return {outopen}{aa}self.request(
            {method!r}, {pathexpr}, json=_core.Arguments.merge(body, fields),
            binary={binary!r}, technique={name!r}, enveloped={enveloped!r},
        ){outclose}
"""

GET_SIGNATURE = """    {aw}def {name}(self{argspec}, **params: Any) -> {ret}:
        \"\"\"{summary}.

        Wraps ``{method} {path}``.
        \"\"\"
        return {aa}self.request(
            {method!r}, {pathexpr}, params={{k: v for k, v in params.items() if v is not None}},
            binary={binary!r}, technique={name!r}, enveloped={enveloped!r},
        )
"""


def path_arguments(path: str) -> dict[str, str]:
    """Turn a path template's placeholders into method arguments.

    Every ``{placeholder}`` the schema declares becomes a required argument
    and is quoted into the URL, so a name carrying a slash or a space cannot
    reshape the path it is written into.

    :param path: Path template from the schema.
    :returns: The ``argspec`` and ``pathexpr`` the signature templates want.
    """
    holders = [part.strip("{}") for part in path.split("/") if part.startswith("{")]
    if not holders:
        return {"argspec": "", "pathexpr": repr(path)}
    quoted = path
    for holder in holders:
        quoted = quoted.replace(
            "{" + holder + "}",
            "{quote(str(" + holder + "), safe='')}",
        )
    return {
        "argspec": "".join(f", {holder}: str" for holder in holders),
        "pathexpr": "f" + repr(quoted),
    }


def emit_methods(endpoints, is_async: bool) -> str:
    """Render every endpoint as a method on one client."""
    aw = "async def " if is_async else "def "
    aw = aw[:-4] if False else ("async " if is_async else "")
    aa = "await " if is_async else ""
    out = []
    for e in endpoints:
        ret = "bytes | Path" if e.binary else "Result"
        common = dict(
            aw=aw,
            aa=aa,
            name=e.name,
            ret=ret,
            summary=e.summary,
            method=e.method,
            path=e.path,
            binary=e.binary,
            enveloped=e.enveloped,
        )
        # A binary endpoint answers with a document, so it accepts a path to
        # write it to. Every one of them, rather than whichever was asked for
        # first: a caller should not have to remember which can save itself.
        common["outarg"] = " output: str | Path | None = None," if e.binary else ""
        common["outopen"] = "self._document(" if e.binary else ""
        common["outclose"] = ", output)" if e.binary else ""
        if e.kind == "chart":
            out.append(CHART_SIGNATURE.format(**common))
        elif e.kind == "pair":
            out.append(PAIR_SIGNATURE.format(**common))
        elif e.kind in {"body", "birth_extra"}:
            out.append(
                BODY_SIGNATURE.format(
                    fieldlist=", ".join(f"``{f}``" for f in e.fields)
                    or "see the API docs",
                    **path_arguments(e.path),
                    **common,
                )
            )
        else:
            out.append(GET_SIGNATURE.format(**path_arguments(e.path), **common))
    return "\n".join(out)


def format_generated() -> None:
    """Run the formatter over the files just written.

    Without this the generated modules drift out of the project's format the
    moment anyone runs ``ruff format``, and the next regeneration undoes it.
    """
    import subprocess

    paths = [
        str(TARGET.parent / name)
        for name in (
            "_methods.py",
            "_methods_async.py",
            "_shortcuts.py",
            "_endpoints.py",
        )
    ]
    for argv in (
        [sys.executable, "-m", "ruff", "check", "--fix", "--quiet", *paths],
        [sys.executable, "-m", "ruff", "format", "--quiet", *paths],
    ):
        result = subprocess.run(
            argv,
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode:
            print(result.stderr, file=sys.stderr)


def write_mixins(endpoints) -> None:
    """Write the generated method mixins for both clients."""
    header = '''"""Generated client methods, one per published endpoint.

Produced by ``tools/generate_endpoints.py``. Do not edit: rerun the generator
so the SDK cannot describe a surface the API does not serve.

Endpoints: {count}
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any, Literal, overload
from urllib.parse import quote

from . import _core
from .response import Result


class {cls}:
    """Every endpoint, mixed into the {word} client.

    The transport lives on the client this is mixed into. Declaring the three
    hooks here is what lets a type checker see the mixin as complete instead
    of reporting every method as calling something that does not exist.
    """

    if TYPE_CHECKING:
        @overload
        {aw}def request(
            self, method: str, path: str, *, binary: Literal[False] = ...,
            technique: str | None = ..., enveloped: bool | None = ..., **kwargs: Any,
        ) -> Result: ...

        @overload
        {aw}def request(
            self, method: str, path: str, *, binary: Literal[True],
            technique: str | None = ..., enveloped: bool | None = ..., **kwargs: Any,
        ) -> bytes: ...

        {aw}def request(
            self, method: str, path: str, *, binary: bool = ...,
            technique: str | None = ..., enveloped: bool | None = ..., **kwargs: Any,
        ) -> Result | bytes: ...

        @overload
        {aw}def _chart(
            self, path: str, payload: dict[str, Any] | None,
            options: dict[str, Any] | None, *, binary: Literal[False] = ...,
            technique: str | None = ..., enveloped: bool | None = ..., **fields: Any,
        ) -> Result: ...

        @overload
        {aw}def _chart(
            self, path: str, payload: dict[str, Any] | None,
            options: dict[str, Any] | None, *, binary: Literal[True],
            technique: str | None = ..., enveloped: bool | None = ..., **fields: Any,
        ) -> bytes: ...

        {aw}def _chart(
            self, path: str, payload: dict[str, Any] | None,
            options: dict[str, Any] | None, *, binary: bool = ...,
            technique: str | None = ..., enveloped: bool | None = ..., **fields: Any,
        ) -> Result | bytes: ...

        @overload
        {aw}def _pair(
            self, path: str, birth: dict[str, Any], partner: dict[str, Any],
            options: dict[str, Any] | None, *, binary: Literal[False] = ...,
            technique: str | None = ..., enveloped: bool | None = ..., **extra: Any,
        ) -> Result: ...

        @overload
        {aw}def _pair(
            self, path: str, birth: dict[str, Any], partner: dict[str, Any],
            options: dict[str, Any] | None, *, binary: Literal[True],
            technique: str | None = ..., enveloped: bool | None = ..., **extra: Any,
        ) -> bytes: ...

        {aw}def _pair(
            self, path: str, birth: dict[str, Any], partner: dict[str, Any],
            options: dict[str, Any] | None, *, binary: bool = ...,
            technique: str | None = ..., enveloped: bool | None = ..., **extra: Any,
        ) -> Result | bytes: ...

        @staticmethod
        def _document(content: bytes, output: str | Path | None) -> bytes | Path: ...

'''
    root = TARGET.parent
    (root / "_methods.py").write_text(
        header.format(
            count=len(endpoints), cls="SyncEndpoints", word="synchronous", aw=""
        )
        + emit_methods(endpoints, False),
        encoding="utf-8",
    )
    (root / "_methods_async.py").write_text(
        header.format(
            count=len(endpoints), cls="AsyncEndpoints", word="asynchronous", aw="async "
        )
        + emit_methods(endpoints, True),
        encoding="utf-8",
    )


SHORTCUT_CHART = '''def {name}(
    payload: dict[str, Any] | None = None, **fields: Any
) -> {ret}:
    """{summary}.

    Forwards to :meth:`AstroMansion.{name}` on the shared client.
    """
    return default_client().{name}(payload, **fields)
'''

SHORTCUT_PAIR = '''def {name}(
    birth: dict[str, Any], partner: dict[str, Any], **kwargs: Any
) -> {ret}:
    """{summary}.

    Forwards to :meth:`AstroMansion.{name}` on the shared client.
    """
    return default_client().{name}(birth, partner, **kwargs)
'''

SHORTCUT_PLAIN = '''def {name}(*args: Any, **kwargs: Any) -> {ret}:
    """{summary}.

    Forwards to :meth:`AstroMansion.{name}` on the shared client.
    """
    return default_client().{name}(*args, **kwargs)
'''


def write_shortcuts(endpoints) -> None:
    """Write a module-level shortcut for every endpoint.

    Generated from the same table as the methods. A convenience surface that
    covered only some endpoints would read as the whole package while hiding
    most of it, so it covers all of them or it would not be offered.
    """
    blocks = []
    for endpoint in endpoints:
        common = {
            "name": endpoint.name,
            "ret": "bytes | Path" if endpoint.binary else "Result",
            "summary": endpoint.summary,
        }
        if endpoint.kind == "chart":
            blocks.append(SHORTCUT_CHART.format(**common))
        elif endpoint.kind == "pair":
            blocks.append(SHORTCUT_PAIR.format(**common))
        else:
            blocks.append(SHORTCUT_PLAIN.format(**common))

    listing = "\n".join(f'    "{name}",' for name in sorted(e.name for e in endpoints))
    header = f'''"""Module-level shortcut for every endpoint.

Generated by ``tools/generate_endpoints.py``. Do not edit.

Endpoints: {len(endpoints)}
"""

from __future__ import annotations

from typing import Any

from pathlib import Path

from .response import Result
from .shortcuts import default_client

__all__ = [
{listing}
]


'''
    (TARGET.parent / "_shortcuts.py").write_text(
        header + "\n".join(blocks),
        encoding="utf-8",
    )


if __name__ == "__main__":
    TARGET.write_text(build(), encoding="utf-8")
    import importlib.util

    spec = importlib.util.spec_from_file_location("_endpoints", TARGET)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    write_mixins(module.ENDPOINTS)
    write_shortcuts(module.ENDPOINTS)
    format_generated()
    print(f"wrote {len(module.ENDPOINTS)} endpoints", file=sys.stderr)
