"""Print a full natal chart from the AstroMansion API.

Run it::

    export ASTROMANSION_API_KEY="your key"
    python examples/natal_chart.py

Edit ``BIRTH`` below for a different chart. The place is looked up through the
API rather than typed by hand, so the coordinates come from the same source
the calculation uses.
"""

from __future__ import annotations

import sys

from astromansion import (
    AstroMansion,
    AstroMansionError,
    AuthenticationError,
    PermissionDeniedError,
)

#: Change these for another chart.
BIRTH = {
    "date": "2000-01-01",  # YYYY-MM-DD
    "time": "12:00",  # HH:MM, omit the key if the time is unknown
    "lat": 51.4779,  # decimal degrees, north positive
    "lon": 0.0,  # decimal degrees, east positive
    "timezone": 0,  # hours from UTC, or a name like "Europe/London"
}
PLACE = "Royal Observatory, Greenwich"


def rule(title: str) -> None:
    print(f"\n{title}")
    print("-" * 58)


def main() -> int:
    with AstroMansion() as client:
        # The API knows the place better than a guessed coordinate does.
        try:
            found = client.search_places(q="Greenwich", limit=1, lang="en")
            first = found.data["results"][0] if found.data.get("results") else None
            if first:
                print(f"Place: {first['label']}  ({first['lat']}, {first['lon']})")
        except AstroMansionError:
            print(f"Place: {PLACE}")

        chart = client.natal(**BIRTH)

        print(
            f"Date: {BIRTH['date']} {BIRTH.get('time', '')}  UTC{BIRTH['timezone']:+g}"
        )

        rule("SUMMARY")
        for name, point in chart.summary.items():
            print(f"  {name:6}{point['sign']:14}{point['dms']}")

        rule(f"PLANETS ({len(chart.planets)})")
        print(f"  {'':12}{'SIGN':14}{'DEGREE':14}{'HOUSE':6}STATE")
        for planet in chart.planets:
            state = "R" if planet.get("retrograde") else ""
            house = planet.get("house", "")
            print(
                f"  {planet['name']:12}{planet['sign']:14}"
                f"{planet['dms']:14}{house!s:4}{state}"
            )

        aspects = list(chart.aspects)
        rule(f"ASPECTS ({len(aspects)})")
        if not aspects:
            print("  (no aspect within this orb)")
        for aspect in aspects:
            row = dict(aspect)
            left = row.get("a") or row.get("from") or row.get("first") or "?"
            right = row.get("b") or row.get("to") or row.get("second") or "?"
            kind = row.get("aspect") or row.get("type") or "?"
            orb = row.get("orb")
            print(f"  {left:12}{kind:18}{right:12}orb {orb}")

        # Arabic lots come from the query surface rather than a named method.
        try:
            lots = client.query(birth=BIRTH, sql="SELECT * FROM lots")
            rows = lots.data
            rule(f"ARABIC LOTS ({len(rows)})")
            for lot in rows:
                print(
                    f"  {lot['name']:24}{lot['sign']:14}"
                    f"{lot['dms']:14}ev {int(lot['house'])}"
                )
        except PermissionDeniedError:
            rule("ARABIC LOTS")
            print("  Not included in this plan.")

    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except AuthenticationError as error:
        print(f"Key problem: {error.message}", file=sys.stderr)
        sys.exit(1)
    except AstroMansionError as error:
        print(f"API error ({error.status_code}): {error}", file=sys.stderr)
        sys.exit(1)
