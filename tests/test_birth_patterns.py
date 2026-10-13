"""tests/test_birth_patterns.py: The birth patterns do what their docstrings say.

Each pattern in ``BirthConstants`` documents the inputs it accepts and refuses
and draws itself part by part. No doctest runner reads a class attribute's
docstring, so this test reads those lines from the source and checks them:
every accepted input matches, every refused one does not, and the drawing,
spaces removed, still spells the pattern.
"""

from __future__ import annotations

import ast
import re
from pathlib import Path
from typing import Final

import pytest

from astromansion.models.constants.birth import BirthConstants

SOURCE: Final[Path] = (
    Path(__file__).resolve().parents[1] / "src/astromansion/models/constants/birth.py"
)
ITEM: Final[re.Pattern[str]] = re.compile(r"``([^`]+)``")


def _docstrings() -> dict[str, str]:
    """Read the docstring written under each pattern of ``BirthConstants``.

    Returns:
        Each pattern's name mapped to the docstring that follows it.
    """
    tree = ast.parse(SOURCE.read_text(encoding="utf-8"))
    holder = next(
        node
        for node in tree.body
        if isinstance(node, ast.ClassDef) and node.name == "BirthConstants"
    )
    found: dict[str, str] = {}
    for statement, following in zip(holder.body, holder.body[1:], strict=False):
        if (
            isinstance(statement, ast.AnnAssign)
            and isinstance(statement.target, ast.Name)
            and isinstance(following, ast.Expr)
            and isinstance(following.value, ast.Constant)
            and isinstance(following.value.value, str)
        ):
            found[statement.target.id] = following.value.value
    return found


def _listed(docstring: str, label: str) -> list[str]:
    """Return the inputs a docstring lists after a label.

    Args:
        docstring: The pattern's docstring.
        label: ``Accepts:`` or ``Refuses:``.

    Returns:
        The inputs written between double backquotes on that line.
    """
    line = next(row for row in docstring.splitlines() if row.strip().startswith(label))
    return ITEM.findall(line)


def _drawing(docstring: str) -> str:
    """Return the drawing's first line with its spaces removed.

    Args:
        docstring: The pattern's docstring.

    Returns:
        The pattern as the drawing spells it.
    """
    rows = docstring.splitlines()
    start = next(index for index, row in enumerate(rows) if row.strip() == "Drawing::")
    first = next(row for row in rows[start + 1 :] if row.strip())
    return first.replace(" ", "")


@pytest.mark.parametrize("name", ["DATE", "TIME"])
def test_each_pattern_matches_its_documented_examples(name: str) -> None:
    """Accepted inputs match and refused inputs do not.

    Args:
        name: The pattern's attribute name.
    """
    pattern: re.Pattern[str] = getattr(BirthConstants, name)
    docstring = _docstrings()[name]
    accepted = _listed(docstring, "Accepts:")
    refused = _listed(docstring, "Refuses:")
    assert accepted and refused
    assert all(pattern.match(text) for text in accepted)
    assert not any(pattern.match(text) for text in refused)


@pytest.mark.parametrize("name", ["DATE", "TIME"])
def test_each_drawing_still_spells_its_pattern(name: str) -> None:
    """The drawing changes when the pattern does.

    Args:
        name: The pattern's attribute name.
    """
    pattern: re.Pattern[str] = getattr(BirthConstants, name)
    assert _drawing(_docstrings()[name]) == pattern.pattern
