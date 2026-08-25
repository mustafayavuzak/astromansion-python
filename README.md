# AstroMansion

[![PyPI](https://img.shields.io/pypi/v/astromansion)](https://pypi.org/project/astromansion/)
[![Python](https://img.shields.io/pypi/pyversions/astromansion)](https://pypi.org/project/astromansion/)
[![License](https://img.shields.io/pypi/l/astromansion)](LICENSE)

Official Python client for the [AstroMansion](https://astromansion.com) astrology API.

Nothing is computed locally. Every call reaches `https://api.astromansion.com`,
which owns the ephemeris, your plan, your quota and your rate limit. The
package never opens a feature the server did not grant.

## Install

```bash
pip install astromansion
```

Python 3.10 or newer. The only dependency is `httpx`, installed with its SOCKS
support so the client still works behind a corporate proxy, a local SOCKS
proxy or Tor without anything further to install.

## Get an API key

Create an account at [astromansion.com](https://astromansion.com), open your
account page and generate a key. Requests made with it count against that
account, under the plan it already has.

## First chart

Put the key in the environment rather than in your source:

```bash
export ASTROMANSION_API_KEY="your key"
```

```python
from astromansion import AstroMansion

client = AstroMansion()

chart = client.natal(
    date="1990-07-19",
    time="14:30",
    lat=41.0082,
    lon=28.9784,
    timezone=3,
)

print(chart.summary.Sun.sign)  # Cancer
print(chart.planets[0].house)  # 9
```

Birth data is passed flat. The API nests it under `birth`; the client does
that for you.

Fields: `date` as `YYYY-MM-DD`, `time` as `HH:MM` (omit if unknown), `lat` and
`lon` in decimal degrees, `timezone` as an hour offset or an IANA zone name,
`houses` for a house system.

You can pass a mapping instead of keywords, but not both at once:

```python
chart = client.natal({"date": "1990-07-19", "lat": 41.0082, "lon": 28.9784})
```

## Where the key comes from

In order: the `api_key` argument, then `astromansion.set_api_key(...)`, then
`ASTROMANSION_API_KEY`. With none of them the constructor raises
`AuthenticationError`, before a connection is opened and before the proxy
environment is read, so a forgotten key is reported as a forgotten key.

```python
client = AstroMansion(api_key="your key")
```

`astromansion.reset()` drops the module key and the shared client, which is
what a test wants between cases.

## Quick use

For a notebook or a one-file script:

```python
import astromansion as am

am.set_api_key("your key")  # or rely on the environment
chart = am.natal(date="1990-07-19", lat=41.0082, lon=28.9784)
```

Applications should build a client instead: it holds a connection pool, and
two of them can carry two different keys.

## Async

```python
from astromansion import AsyncAstroMansion

async with AsyncAstroMansion() as client:
    chart = await client.natal(
        date="1990-07-19",
        time="14:30",
        lat=41.0082,
        lon=28.9784,
        timezone=3,
    )
```

Same method names, same arguments, same exceptions. Python cannot make one
class serve both, so the bare name is synchronous and `Async` marks the other,
as in `httpx`, `openai` and `anthropic`.

## Reading a response

The response is the server's own JSON, readable either way:

```python
chart.summary.Sun.sign
chart["summary"]["Sun"]["sign"]
chart.to_dict()
```

Nothing is remodelled, so a field the API adds reaches you instead of being
dropped, and no field it did not send is invented.

Some endpoints answer with the data itself and some wrap it as
`{"technique": ..., "result": ...}`. The client opens that wrapper, so every
response reads the same way and you never have to remember which kind you
called:

```python
chart = client.vedic_chart(date="1990-07-19", lat=41.0082, lon=28.9784)

chart.data          # the payload, wrapper removed
chart.technique     # what the server called it, when it said
chart.raw           # the untouched body, wrapper included
```

A body that carries a real `result` field of its own is left alone; the
wrapper is recognised by its exact shape rather than by the presence of a
name that data is allowed to use.

## Arabic lots, fixed stars and the rest of the catalog

`natal` answers with the chart proper. Anything beyond it is named on `chart`,
through `options.categories`:

```python
lots = client.chart(
    date="1990-07-19", time="14:30",
    lat=41.0082, lon=28.9784, timezone=3,
    options={"categories": ["arabic_lots"]},
)

for lot in lots.data["bodies"]["arabic_lots"]:
    print(lot["name"], lot["sign"], lot["dms"], lot["house"])
```

Bodies come back grouped under the category that produced them, so read the
group you asked for. The catalog publishes 38 Arabic lots and 908 fixed stars,
along with `planets`, `dwarfs`, `asteroids`, `centaurs`, `comets`,
`hypotheticals`, `points`, `advanced_points`, `lilith`, `planetary_nodes`,
`exoplanets`, `moons` and `eclipses`.

`chart` answers one page at a time, and a large category is more than one
page. Use `bodies` to read the whole of it and let the client follow the
paging:

```python
found = client.bodies(
    "fixed_stars", "arabic_lots",
    date="1990-07-19", time="14:30",
    lat=41.0082, lon=28.9784, timezone=3,
)

len(found["fixed_stars"])  # 908, in six requests
len(found["arabic_lots"])  # 38
```

Naming several categories reads them in one walk. The return is always a
mapping keyed by the categories you asked for, one or several, so the shape
never depends on how many.

Each page costs a network round trip and the calculation inside it is a
rounding error beside that, so `bodies` asks for the largest page the API
serves. `page_size` lowers it, and lowering it buys nothing: 908 stars are
six requests at 160 and a hundred and eighty-two at five.

Some categories are enormous. `asteroids` holds twenty-eight thousand bodies,
which is a hundred and seventy-seven round trips with nothing printed until
the last one lands, and a program that prints nothing for a minute cannot be
told apart from one that has hung. A walk that large stops after the first
page and tells you the size:

```python
am.bodies("asteroids", date="2000-01-01", lat=51.4779, lon=0.0)
# ValidationError: asteroids holds 28214 bodies, which is 177 requests and
# will print nothing until the last one lands. Pass confirm_large=True ...
```

Read it anyway, or watch it arrive:

```python
found = client.bodies(
    "asteroids", date="2000-01-01", lat=51.4779, lon=0.0,
    confirm_large=True,
    on_page=lambda done, left, rows: print(f"{done} done, {left} to go"),
)
```

For a handful of named bodies there is no walk at all:

```python
page = client.chart(
    date="2000-01-01", lat=51.4779, lon=0.0,
    options={"include": ["Ceres", "Pallas", "Juno", "Vesta"],
             "exclusive": True},
)

for rows in page.data["bodies"].values():
    for body in rows:
        print(body["name"], body["sign"], body["dms"])
```

Read every group rather than the one you expected. Bodies are filed under the
category the catalog puts them in, not the category you were thinking of when
you named them: Ceres was an asteroid in 1801 and has been a dwarf planet
since 2006, so it arrives under `dwarfs` while Pallas, Juno and Vesta arrive
under `asteroids`. A loop over `bodies["asteroids"]` alone finds three of the
four and reports the fourth as missing.

`exclusive` narrows the catalog, not the chart. The angles and the derived
points are calculated either way, so `points` and `advanced_points` are still
in the answer. Filter by name if you want only what you asked for:

```python
wanted = {"Ceres", "Pallas", "Juno", "Vesta"}

for rows in page.data["bodies"].values():
    for body in rows:
        if body["name"] in wanted:
            print(body["name"], body["sign"], body["dms"])
```

Reach for `chart` directly when you want one page rather than the category,
and read the group with `.get`. The chart's own bodies are calculated
alongside the categories you name and the page is a window over that whole
selection, so a small `catalog_limit` can fill the first page with planets
and angles before a single star appears, leaving no `fixed_stars` key at all.
`catalog_page.total` counts the same way, the whole selection rather than the
category.

There is no ceiling on how many you may read this way. `options.all_bodies`
walks every category at once and needs the full-catalog scope that comes with
Pro and Enterprise; naming the categories yourself does not.

## MansionSQL

A chart is a table of bodies, a table of houses and a table of aspects, and
the questions people ask of one are the questions SQL was written for: which
planets are retrograde, which aspects are inside a degree, how the signs are
distributed. `query` sends a `SELECT` and the server calculates the chart and
answers it.

```python
rows = client.query(
    birth={"date": "2000-01-01", "time": "12:00",
           "lat": 51.4779, "lon": 0.0, "timezone": 0},
    sql="SELECT name, sign, dms FROM planets WHERE retrograde = 1",
)

for row in rows.data:
    print(row["name"], row["sign"], row["dms"])
# Saturn Taurus 10°23′44″
```

`query` takes the request body rather than flat birth fields, because a
statement may name two charts and a moment, and each of them needs its own
birth block. It needs the `advanced` scope.

### Tables

Every table but three carries the body columns: `code`, `name`, `longitude`,
`latitude`, `distance`, `speed`, `sign`, `sign_index`, `house`, `retrograde`,
`dms`, `category`.

| Table | One row per |
|---|---|
| `chart`, `bodies` | every body the chart calculated |
| `planets` | the planets |
| `points` | angles and derived points |
| `advanced_points` | the further derived points |
| `dwarfs`, `centaurs`, `comets`, `moons`, `eclipses`, `lilith`, `exoplanets`, `hypotheticals`, `planetary_nodes`, `arabic_lots` | that catalog category |
| `natal_a` | the `birth` chart, named for joins |
| `natal_b` | the `partner` chart |
| `transits` | the `moment` chart |

Three have columns of their own:

| Table | One row per | Columns |
|---|---|---|
| `houses` | each of the twelve | `number`, `cusp`, `sign`, `dms`, `size`, `bodies` |
| `aspects` | each aspect found | `a`, `b`, `aspect`, `angle`, `orb`, `separation`, `a_sign`, `b_sign` |
| `stars` | each point placed against a stellar position, 953 of them | `name`, `longitude`, `latitude`, `sign`, `dms`, `magnitude`, `orb` |
| `lots` | each Arabic lot the engine computes, 38 of them | `name`, `longitude`, `sign`, `dms`, `house` |

`natal_b` needs `partner`, and a statement naming it without one is refused.
`transits` uses `moment`, and without one it is the current instant at the
birth location.

There is no `asteroids` table. One chart holds at most 192 bodies and the
category is twenty-eight thousand, so the query is refused rather than
silently reduced to the first 192:

```python
client.query(birth={...}, sql="SELECT name FROM asteroids")
# ValidationError: The query asks for more bodies than one chart can hold.
# Narrow it with WHERE name = 'Pallas', a minor planet number such as
# WHERE name = '1198', or WHERE name IN (...). Use /v1/catalog to look a
# body up by name.
```

`stars` answers 953 rows while the `fixed_stars` catalog category walks 908,
so the two are different selections and a count taken from one does not
describe the other. The table is every point the engine places against a
stellar position: the 908 fixed stars, 40 exoplanets and the 5 galactic and
deep-sky points filed under `advanced_points`. One row per point, so counting
the rows and counting the names give the same answer.

`lots` and the `arabic_lots` category do not divide that way. Both answer 38:
the table gives the lots computed for one chart, the category gives the names
those lots are looked up by, and they are the same 38 lots.

`SELECT` only. Anything else is refused before it reaches the engine, so a
statement cannot write, drop or reach outside the chart it was given.

```python
client.query(birth={...}, sql="DELETE FROM planets")
# ValidationError: expected SELECT at offset 0
```

### A hundred rows

An answer is capped at a hundred rows, and a statement that would exceed it is
refused rather than truncated, so a partial answer never arrives looking whole:

```python
client.query(birth={...}, sql="SELECT name FROM stars")
# ValidationError: MansionSQL returned 100 rows of 953; add LIMIT or narrow
# the query
```

Add `LIMIT`, or narrow with `WHERE`. `COUNT(*)` is one row, so counting a
large table is always available.

### What the dialect supports

`WHERE`, `GROUP BY`, `HAVING`, `ORDER BY`, `LIMIT`, `OFFSET`, `DISTINCT`,
`JOIN`, `AS`, `IN`, `NOT IN`, `LIKE`, `BETWEEN`, `IS NULL`, `EXISTS`,
`CASE WHEN`, and comparison and arithmetic on any column.

Clauses apply in the SQL order, which is worth stating because it decides what
`HAVING` sees and what the hundred-row cap counts:

```
FROM -> WHERE -> GROUP BY -> HAVING -> SELECT -> ORDER BY -> LIMIT
```

```python
# The tightest aspects first.
"SELECT a, b, aspect, orb FROM aspects WHERE orb < 1 ORDER BY orb LIMIT 20"

# How the chart is distributed.
"SELECT sign, COUNT(*) AS n FROM planets GROUP BY sign ORDER BY n DESC"

# Angles only.
"SELECT number, sign, dms FROM houses WHERE number IN (1, 10)"

# Each planet with the sign on the cusp of the house it occupies.
"SELECT p.name, h.sign FROM planets p JOIN houses h ON p.house = h.number"

# The brightest fixed stars.
"SELECT name, sign, dms, magnitude FROM stars ORDER BY magnitude LIMIT 10"
```

#### Aggregates

| Function | Argument | On an empty set | Notes |
|---|---|---|---|
| `COUNT(*)` | none | `0` | counts rows |
| `COUNT(col)` | any | `0` | counts non-`NULL` values, so it can be smaller |
| `MIN(col)` | number or text | `NULL` | text compares lexically |
| `MAX(col)` | number or text | `NULL` | text compares lexically |
| `AVG(col)` | number | `NULL` | refuses a text column |
| `SUM(col)` | number | `NULL` | refuses a text column |

`AVG` and `SUM` refuse a column that is not numeric rather than skipping the
rows they cannot read. Skipping is the dangerous answer: over a column that is
numeric for some rows and text for others it returns the average of part of the
column with nothing to say the rest was dropped.

```python
client.query(birth={...}, sql="SELECT AVG(sign) AS v FROM planets")
# ValidationError: AVG requires a numeric column; sign is text
```

`HAVING` filters groups after grouping, and its operands may be aggregates. It
requires a `GROUP BY`: some engines allow it without one and read the whole
result as a single group, but in practice a bare `HAVING` is a `WHERE` written
in the wrong place, and saying so is more use than answering it.

```python
# Stellium: three or more bodies in one sign.
"SELECT sign, COUNT(*) AS n FROM planets GROUP BY sign HAVING COUNT(*) >= 3"

# Signs the chart moves slowly through.
"SELECT sign, AVG(speed) AS v FROM planets GROUP BY sign HAVING AVG(speed) < 0"
```

An aggregate collapses rows, so `SELECT COUNT(*) FROM stars` is one row and
never meets the hundred-row cap. The cap counts the final result, after
`HAVING`.

#### Astrological functions

Scalar functions, usable anywhere a column is: in `SELECT`, `WHERE`,
`GROUP BY`, `ORDER BY`, and inside an aggregate. All are lookups or integer
arithmetic; none of them calculates anything further.

| Function | Argument | Returns |
|---|---|---|
| `ELEMENT(sign)` | sign name | `fire`, `earth`, `air`, `water` |
| `MODALITY(sign)` | sign name | `cardinal`, `fixed`, `mutable` |
| `RULER(sign)` | sign name | the traditional ruler's name |
| `DIGNITY(body, sign)` | body and sign names | `domicile`, `exaltation`, `detriment`, `fall`, `peregrine` |
| `DECAN(longitude)` | degrees | `1`, `2` or `3` |
| `ANGULAR(house)` | 1 to 12 | `angular`, `succedent`, `cadent` |
| `ORB(a, b)` | two longitudes | their separation, never over 180 |
| `SEPARATION(a, b)` | two longitudes | the same |
| `ABS`, `ROUND`, `FLOOR`, `CEIL`, `SIGN` | a number | the usual arithmetic |

`RULER` is the traditional rulership and only that: Mars for Scorpio, Saturn
for Aquarius, Jupiter for Pisces. A modern variant would be a second answer to
the same question decided by a setting the statement cannot show, so one query
would mean two things; if it is wanted it will be a second function under its
own name.

`DIGNITY` is the classical seven-planet table. Anything outside the seven is
`peregrine`, including Uranus, Neptune, Pluto and the asteroids: inventing a
domicile for them would be inventing astrology rather than reading it.
Triplicity, term and face are real dignities and are deliberately not reported,
because they need a degree and a day-night distinction and this function is
given a sign. Mercury in Virgo holds both domicile and exaltation and is
reported as `domicile`.

`NULL` in, `NULL` out. A body with no house returns `NULL` from `ANGULAR`
rather than a default. A name no sign or body carries is refused, and the
message quotes the value it was given:

```python
client.query(birth={...}, sql="SELECT ELEMENT('Lion') AS e FROM planets")
# ValidationError: ELEMENT does not know the sign 'Lion'
```

```python
# Elemental balance.
"SELECT ELEMENT(sign) AS element, COUNT(*) AS n "
"FROM planets GROUP BY ELEMENT(sign) ORDER BY n DESC"

# Planets in their own sign.
"SELECT name, sign FROM planets WHERE DIGNITY(name, sign) = 'domicile'"

# The single tightest aspect in the chart.
"SELECT MIN(orb) AS tightest FROM aspects"

# Angular houses only, with the decan.
"SELECT name, sign, DECAN(longitude) AS decan "
"FROM planets WHERE ANGULAR(house) = 'angular'"
```

#### Subqueries

A subquery may stand after `IN` or `NOT IN`, after `EXISTS`, or as a single
value in the `SELECT` list. The inner statement may name a different table
than the outer one; both charts are already calculated, so this filters data in
hand rather than calculating a second time.

```python
# Everything aspecting a retrograde planet.
"SELECT a, b, aspect, orb FROM aspects "
"WHERE a IN (SELECT name FROM planets WHERE retrograde = 1)"
```

The inner statement must select exactly one column, and is told so by count:

```python
client.query(birth={...}, sql="SELECT a FROM aspects "
                              "WHERE a IN (SELECT name, sign FROM planets)")
# ValidationError: subquery must select one column, got 2
```

The hundred-row cap applies to the final answer only. An inner query may
legitimately produce all 953 stars while the outer answer is three rows.

`NOT IN` follows standard SQL where the inner set contains a `NULL`, which
surprises people and is worth stating plainly: **if any inner value is `NULL`,
`NOT IN` returns no rows at all.** The comparison is unknown rather than false,
and unknown is not true, so nothing passes. `IN` is unaffected: it still
matches the values that are there. Add `WHERE col IS NOT NULL` to the inner
statement when the column has gaps. An empty inner set behaves the way the
logic implies: `IN` matches nothing, `NOT IN` matches everything.

Two charts in one statement, which is synastry written as a join:

```python
rows = client.query(
    birth={"date": "2000-01-01", "time": "12:00",
           "lat": 51.4779, "lon": 0.0, "timezone": 0},
    partner={"date": "1995-03-14", "time": "08:20",
             "lat": 41.0082, "lon": 28.9784, "timezone": 3},
    sql="SELECT a.name, a.sign, b.name AS partner "
        "FROM natal_a a JOIN natal_b b ON a.sign = b.sign LIMIT 50",
)
```

And transits against the natal chart:

```python
rows = client.query(
    birth={"date": "2000-01-01", "time": "12:00",
           "lat": 51.4779, "lon": 0.0, "timezone": 0},
    moment={"date": "2026-08-17", "time": "12:00",
            "lat": 51.4779, "lon": 0.0, "timezone": 0},
    sql="SELECT t.name, t.sign, n.name AS natal "
        "FROM transits t JOIN chart n ON t.sign = n.sign LIMIT 50",
)
```

A join multiplies rows, so it reaches the hundred sooner than a plain select.
Both of these overrun it without the `LIMIT`.

### Rendered output

Without `format` the answer is rows. `box` and `csv` render it as text, meant
for a terminal rather than for parsing, and arrive as `str`:

```python
print(client.query(birth={...}, sql="SELECT name, sign FROM planets LIMIT 3",
                   format="box"))
# ┌─────────┬───────────┐
# │ name    │ sign      │
# ├─────────┼───────────┤
# │ Sun     │ Capricorn │
# └─────────┴───────────┘
```

`border` picks the box style from `sharp`, `round`, `ascii`, `rules` and
`markdown`.

`json` renders too, and the client parses it back, so it reads like any other
response rather than like a string you have to decode yourself.

`scalar` returns the single value a one-row, one-column answer holds, and
`object` returns a one-row answer as a mapping, which saves indexing into a
list of one:

```python
client.query(birth={...}, sql="SELECT COUNT(*) AS n FROM stars",
             format="scalar").data          # 953.0

client.query(birth={...}, sql="SELECT name, sign FROM planets LIMIT 1",
             format="object").data["sign"]  # 'Capricorn'
```

## Every endpoint

Every published operation, 66 of them, has a method on both clients and a
module-level shortcut, all generated from the schema: `natal`, `transits`, `synastry`, `composite`,
`solar_return`, `progression`, `harmonics`, `astrocartography`, `vedic_chart`,
`zodiacal_releasing`, `firdaria`, `horary`, `electional` and the rest.

Anything new is reachable before this client names it:

```python
result = client.request("POST", "/v1/harmonics", json={"birth": {...}})
```

Authentication, timeouts, retries and error handling behave identically there.

## Errors

```python
from astromansion import QuotaExceededError, RateLimitError

try:
    chart = client.natal(date="1990-07-19", lat=41.0, lon=29.0)
except RateLimitError as error:
    print("wait", error.retry_after, "seconds")
except QuotaExceededError:
    print("this period's allowance is spent")
```

| Exception | Meaning |
|---|---|
| `AuthenticationError` | Key missing, malformed or unknown |
| `PermissionDeniedError` | Valid key, feature not in the plan |
| `QuotaExceededError` | Allowance for the period is spent |
| `RateLimitError` | Too many requests just now; `retry_after` says how long |
| `ValidationError` | Request rejected; `details` names the field |
| `NotFoundError`, `ConflictError` | Missing resource, conflicting state |
| `ServerError` | The API failed to answer |
| `AstroMansionConnectionError` | The request never completed |

All descend from `AstroMansionError`. Each carries `status_code`,
`error_code`, `details`, `request_id` and `retry_after` when the API supplies
them.

## Rate limits and quota

A rate limit clears on its own after `retry_after`. A spent quota does not:
it needs a new period or a larger plan. They are separate exceptions for that
reason.

The client retries only failures that carry no result: connection errors, 429
and 5xx, twice by default, honouring `Retry-After`. A refusal you must fix is
never retried.

```python
client = AstroMansion(timeout=60.0, max_retries=0)
```

## Documents

```python
pdf = client.export_pdf(date="1990-07-19", lat=41.0082, lon=28.9784)

with open("chart.pdf", "wb") as file:
    file.write(pdf)
```

Or name a path and let the client write it:

```python
client.export_pdf(date="1990-07-19", lat=41.0082, lon=28.9784, output="chart.pdf")
```

Every endpoint that answers with a document takes `output` the same way:
`export_pdf`, `export_csv`, `render_svg`, `render_png`, `render_biwheel` and
`render_sharecard`, on both clients.

```python
client.render_svg(date="1990-07-19", lat=41.0082, lon=28.9784, output="wheel.svg")
```

Nothing is written to disk unless you name a path, so a call cannot overwrite
a file you did not choose. Without one you get the bytes and decide yourself.

## Security

The key travels in the `X-API-Key` header, never in a URL. It is masked in
`repr(client)` and appears in no exception or log line the package writes.
Keep it in the environment or a secret store, not in source control. Rotate it
from your account page if it leaks.

## Staging

```python
client = AstroMansion(base_url="http://localhost:8000")
```

Also readable from `ASTROMANSION_BASE_URL`.

## Links

- [API reference](https://api.astromansion.com/docs)
- [Documentation](https://astromansion.com/en/docs)
