# AstroMansion Python Examples

This cookbook uses the public methods shipped by the SDK. Copy an example,
set an API key, and run it without building request envelopes by hand.

```bash
export ASTROMANSION_API_KEY="your key"
pip install astromansion
```

The examples use this birth data:

```python
BIRTH = {
    "date": "2000-01-01",
    "time": "12:00",
    "lat": 51.4779,
    "lon": 0.0,
    "timezone": "Europe/London",
}
```

An IANA timezone is preferable when the calculation may cross a daylight-saving
boundary. A numeric UTC offset is also accepted.

Short fragments below assume `BIRTH` is defined and `client` is an open
`AstroMansion` instance. The complete sections show client construction when
it materially affects the example.

## Natal chart

```python
from astromansion import AstroMansion

BIRTH = {
    "date": "2000-01-01",
    "time": "12:00",
    "lat": 51.4779,
    "lon": 0.0,
    "timezone": "Europe/London",
}

with AstroMansion() as client:
    chart = client.natal(BIRTH)

print("Sun:", chart.summary.Sun.sign)
for planet in chart.planets:
    state = "retrograde" if planet.retrograde else "direct"
    print(planet.name, planet.sign, planet.dms, planet.house, state)
```

Choose a different house system by adding `houses` to the birth mapping:

```python
whole_sign = {**BIRTH, "houses": "whole_sign"}
with AstroMansion() as client:
    chart = client.natal(whole_sign)
```

Use a context manager in application code so the underlying HTTP connection
pool closes deterministically.

## Async client

The async client has the same methods and arguments:

```python
import asyncio

from astromansion import AsyncAstroMansion


async def main() -> None:
    async with AsyncAstroMansion() as client:
        natal, aspects = await asyncio.gather(
            client.natal(BIRTH),
            client.aspects(BIRTH, options={"orb": 1, "limit": 25}),
        )

    print(natal.summary.Sun.sign)
    print(aspects.data)


asyncio.run(main())
```

Do not create one client per request. Reusing the client preserves connection
pooling in both synchronous and asynchronous programs.

## Find a place before calculating

```python
from astromansion import AstroMansion

with AstroMansion() as client:
    matches = client.search_places(q="Greenwich", limit=5, lang="en")

for place in matches.data["results"]:
    print(place["label"], place["lat"], place["lon"])
```

Use the returned coordinates and timezone rather than guessing a city centre
or a historical UTC offset.

## Extended bodies

Request named categories on `chart`:

```python
from astromansion import AstroMansion

with AstroMansion() as client:
    chart = client.chart(
        BIRTH,
        options={"categories": ["dwarfs", "centaurs", "arabic_lots"]},
    )

for category, bodies in chart.data["bodies"].items():
    for body in bodies:
        print(category, body["name"], body["sign"], body["dms"])
```

Calculate only a short list of named objects:

```python
chart = client.chart(
    BIRTH,
    options={
        "include": ["Ceres", "Chiron", "Eris", "Sedna"],
        "exclusive": True,
    },
)
```

Large categories are paginated. `bodies` follows every page and returns a
mapping keyed by category:

```python
with AstroMansion() as client:
    catalog = client.bodies("fixed_stars", "arabic_lots", payload=BIRTH)

print(len(catalog["fixed_stars"]))
print(len(catalog["arabic_lots"]))
```

The asteroid catalog is intentionally protected from accidental full walks.
Pass `confirm_large=True` and an `on_page` callback only when the application
really needs every row.

## Synastry and compatibility

```python
from astromansion import AstroMansion

PARTNER = {
    "date": "1992-11-03",
    "time": "08:15",
    "lat": 48.8566,
    "lon": 2.3522,
    "timezone": "Europe/Paris",
}

with AstroMansion() as client:
    synastry = client.synastry(BIRTH, PARTNER)
    compatibility = client.compatibility(
        BIRTH,
        PARTNER,
        options={"language": "en", "names": ["Alex", "Morgan"]},
    )

print(synastry.data)
print(compatibility.data)
```

`synastry` returns the technical two-chart analysis. `compatibility` returns
the product-level score and interpretation; they answer related but different
questions.

## Predictive techniques

### Transits and stations

```python
with AstroMansion() as client:
    year = client.transits(BIRTH, options={"year": 2027, "orb": 1.0})
    mercury = client.stations(
        BIRTH,
        options={"body": "Mercury", "year": 2027},
    )

print(year.data)
print(mercury.data)
```

Use an explicit range when the application does not need a whole year:

```python
hits = client.transit_hits(
    BIRTH,
    options={
        "body": "Mars",
        "natal_point": "Sun",
        "from": "2027-01-01",
        "to": "2027-03-31",
    },
)
```

### Progressions and returns

```python
progressed = client.progression(BIRTH, options={"age": 36, "orb": 1.0})
solar_return = client.solar_return(BIRTH, options={"year": 2027})
```

### Electional scan

```python
candidates = client.electional(
    BIRTH,
    options={
        "from": "2027-06-01",
        "to": "2027-06-07",
        "step_minutes": 30,
        "top": 10,
    },
)

for candidate in candidates.data:
    print(candidate)
```

Date ranges are interpreted at the birth location. Keep the timezone in the
birth mapping so local day boundaries remain local.

## Vedic calculations

```python
with AstroMansion() as client:
    vedic = client.vedic_chart(
        BIRTH,
        options={"ayanamsa": "true_citra", "node_mode": "mean"},
    )
    navamsa = client.navamsa(
        BIRTH,
        options={"division": "D9", "ayanamsa": "true_citra"},
    )
    dasha = client.vimshottari(
        BIRTH,
        options={"ayanamsa": "true_citra", "levels": 2},
    )

print(vedic.data)
print(navamsa.data)
print(dasha.data)
```

The selected ayanamsa and node mode are explicit so another system can
reproduce the same chart.

## MansionSQL

Select tight natal aspects:

```python
with AstroMansion() as client:
    aspects = client.query(
        birth=BIRTH,
        sql=(
            "SELECT a, b, aspect, orb FROM aspects "
            "WHERE orb < 1 ORDER BY orb LIMIT 20"
        ),
    )

for row in aspects.data:
    print(row["a"], row["aspect"], row["b"], row["orb"])
```

Aggregate planets by element:

```python
balance = client.query(
    birth=BIRTH,
    sql=(
        "SELECT ELEMENT(sign) AS element, COUNT(*) AS n "
        "FROM planets GROUP BY ELEMENT(sign) ORDER BY n DESC"
    ),
)
```

Render a terminal table instead of JSON:

```python
table = client.query(
    birth=BIRTH,
    sql="SELECT name, sign, dms FROM planets ORDER BY longitude",
    format="box",
    border="round",
)
print(table)
```

MansionSQL accepts `SELECT` only. The complete table, function, aggregation,
join, subquery, and result-limit contract is documented in the
[README](README.md#mansionsql).

## SVG, PNG, PDF, CSV, and share cards

```python
from astromansion import AstroMansion

with AstroMansion() as client:
    client.render_svg(
        BIRTH,
        options={"theme": "dark", "scale": 1.5},
        output="chart.svg",
    )
    client.render_png(
        BIRTH,
        options={"theme": "dark", "width": 1600},
        output="chart.png",
    )
    client.export_pdf(BIRTH, output="chart.pdf")
    client.export_csv(BIRTH, output="chart.csv")
    client.render_sharecard(
        BIRTH,
        type="natal",
        name="Alex",
        lang="en",
        output="sharecard.svg",
    )
```

Without `output`, document methods return bytes and never touch the filesystem:

```python
svg = client.render_svg(BIRTH)
print(len(svg), "bytes")
```

## Enterprise batch and background jobs

Batch several independent calculations into one request:

```python
result = client.batch(
    items=[
        {"technique": "natal", "body": {"birth": BIRTH, "options": {}}},
        {
            "technique": "solar-return",
            "body": {"birth": BIRTH, "options": {"year": 2027}},
        },
    ]
)
```

Queue a long-running operation and poll its state:

```python
accepted = client.submit_job(
    technique="transits",
    body={"birth": BIRTH, "options": {"year": 2027}},
)
job_id = accepted.data["id"]
status = client.job(job_id)
print(status.data["state"])
```

Batch and job methods require the corresponding plan scope. A queued response
does not imply completion; poll until the state is terminal or configure the
documented signed callback URL.

## Errors and request IDs

```python
from astromansion import (
    AstroMansion,
    AstroMansionError,
    PermissionDeniedError,
    QuotaExceededError,
    RateLimitError,
    ValidationError,
)

try:
    with AstroMansion() as client:
        result = client.natal(BIRTH)
except ValidationError as error:
    print("invalid request", error.details)
except PermissionDeniedError:
    print("the current plan does not include this operation")
except RateLimitError as error:
    print("retry after", error.retry_after)
except QuotaExceededError:
    print("the billing-period allowance is exhausted")
except AstroMansionError as error:
    print(error.request_id, error.error_code, error)
```

The client retries connection failures, HTTP 429, and HTTP 5xx responses twice
by default. It does not retry validation, authentication, or permission errors.

## Call a newly published endpoint

The generated clients cover every endpoint in the release. If the server adds
one before the next SDK release, use the transport directly without giving up
authentication, retries, or response decoding:

```python
result = client.request(
    "POST",
    "/v1/new-technique",
    json={"birth": BIRTH, "options": {}},
)
```

Replace the raw request with the generated named method after upgrading the
SDK.
