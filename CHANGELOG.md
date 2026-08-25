# Changelog

## 0.2.1

- The MansionSQL reference in the README now matches what the server answers.
  `HAVING`, `OFFSET`, `DISTINCT`, `BETWEEN`, `EXISTS`, `CASE WHEN` and
  subqueries after `IN` and `NOT IN` all worked and none of them was written
  down, so the documented dialect was smaller than the real one and a caller
  reading it had no way to find them.
- Six astrological scalar functions are documented and are new on the server:
  `ELEMENT`, `MODALITY`, `RULER`, `DIGNITY`, `DECAN` and `ANGULAR`. They work
  wherever a column does, `GROUP BY ELEMENT(sign)` included.
- Three refusals became specific. `AVG` and `SUM` over a text column now say
  which column and that it is text, rather than dropping the rows they cannot
  read and answering an average of the rest. `HAVING` without a `GROUP BY` is
  refused and points at `WHERE`. A subquery selecting more than one column
  says how many it selected.
- The `NOT IN` behaviour when the inner set contains a `NULL` is written down.
  It follows standard SQL, which means it returns no rows at all, and that
  surprises people who have not met it before.
- `COALESCE`, `LENGTH` and `SUBSTR` are new. The two text functions count
  characters rather than bytes, which matters because a degree reads `11°1′36″`
  and is eight characters in thirteen bytes; a byte-indexed slice of it returns
  half of a character and displays as nothing.
- `SUM` and `AVG` no longer lose the small end of a sum. They accumulated
  plainly, so summing one large value and many small ones dropped the small
  ones entirely: `1e16` followed by a hundred `1`s answered `1e16`. Over 953
  rows the drift reached the twelfth figure. They now carry the rounding error
  alongside the total and answer the correctly rounded sum.
- Names are found whatever case they are written in, in every language the
  engine publishes them in. Folding lowercased A to Z and passed everything
  else through, so `Balık` resolved and `BALIK` did not, and seven of the
  twelve Turkish sign names and twenty-four body names were unreachable in
  capitals.

  The client is unchanged: `query` forwards a statement and always did.

## 0.2.0

- Releases are built and uploaded by GitHub Actions through PyPI Trusted
  Publishing. No long-lived upload token exists any more, and every release
  is traceable to the tag and workflow run that produced it. The package
  itself is unchanged from 0.1.14.

## 0.1.14

- A natal card takes one name. `render_sharecard(type="natal", name="...")`
  replaces having to pass a two-entry `names` with a placeholder in the second
  slot for a person the card never draws. `names` still takes two for a
  synastry card, and now refuses a count that does not match the card.

## 0.1.13

- `render_natalcard` is gone and `render_sharecard` takes `type` instead. The
  natal card was published in 0.1.12 as a second endpoint, which split one
  product across two paths for no reason: it is the same card with a different
  subject. `type="natal"` draws it from `birth` alone, `type="synastry"` stays
  the default and still reads both charts.
- 0.1.12 calls `POST /v1/render/natalcard`, which no longer exists. Upgrade.

## 0.1.12

- Added `render_natalcard`, the story-sized card for a single chart. It answers
  an SVG the same way the other document endpoints do, so `output=` writes it
  to a path and omitting that hands back the bytes.
- `render_sharecard` now carries `names` and `lang`. The card could always be
  drawn with real names in a chosen language; the endpoint simply had no field
  for either, so every card published as "Person A" and "Person B" in English.

## 0.1.11

- A rendered table now arrives as text. `query(..., format="box")` answers
  `text/plain`, and the client was handing that back as `bytes`, so printing
  it showed the repr with the box drawing escaped and unreadable. Documents
  are unchanged: a PDF, a PNG, a CSV export and an SVG wheel are still bytes,
  because they are written to files.
- Documented MansionSQL. The `query` endpoint answers SQL over a calculated
  chart, and the README now carries its tables and columns, the hundred-row
  cap, the `SELECT`-only rule, the joins across `natal_a`/`natal_b` and
  `transits`, and every output format.
- Documented that a body arrives under the catalog's category rather than the
  asker's. Ceres is a dwarf planet, so a loop reading only `asteroids` finds
  Pallas, Juno and Vesta and reports Ceres as missing.

## 0.1.10

- `bodies` no longer walks an enormous category in silence. `asteroids` is
  twenty-eight thousand bodies and a hundred and seventy-seven round trips,
  and a program printing nothing for a minute reads as a hung one. The walk
  now stops after the first page and names the size; `confirm_large=True`
  reads it anyway and `on_page` reports progress as it arrives.

## 0.1.9

- Withdrew `planetary_system`. The satellite ephemerides it depended on are
  no longer carried, and a method that cannot answer is worse than one that
  is not there. It will return when the data behind it does.

## 0.1.8

- Replaced the birth data used in the README and the example with a neutral
  one. The previous values were a real person's, which had no business being
  the documented sample.
- Translated the bundled example to English; it ships to every reader of the
  package and was half in another language.

## 0.1.7

- `planetary_system` now covers six planets and twenty-five moons: Mars,
  Jupiter, Saturn, Uranus, Neptune and Pluto. The response names the kernel
  it ran on, and says plainly where that kernel disagrees with JPL Horizons
  rather than leaving a reader to discover it.

## 0.1.6

- Added `planetary_system`, which reads a planet's moons in the three frames
  they legitimately have: where each sits in its own orbit, how far its light
  travelled, and where that orbital phase falls on the natal circle. The three
  are returned apart, with no shared longitude field, because they are
  measured on three different circles.

## 0.1.5

- Every endpoint that answers with a document now takes `output`, on both
  clients. Until now `export_pdf` alone could save itself, and only
  synchronously, so a caller had to remember which of six could.

## 0.1.4

Fixes for defects an independent review measured against 0.1.3.

- `chart_with_custom_body` sent the path template rather than the name, so
  every call reached `/v1/custom-body/{name}` literally. Path parameters are
  now carried by every endpoint kind, not only the query-style ones, and are
  percent-encoded so a name cannot reshape the path it is written into.
- `request` accepted an absolute URL and sent the `X-API-Key` header to
  whatever host it named. It now takes published API paths only, and refuses
  before opening a connection.
- A spent quota answers 429 like a rate limit does, and the client repeated
  it twice more before giving up. A permanent refusal is no longer retried;
  a real rate limit, a 429 with no machine code, and 5xx still are.
- `bodies` returned a partial catalog silently when the page ceiling was
  reached, and would have counted the same rows repeatedly had the API
  stopped advancing. Both now raise rather than look complete.
- The generator formats and lints what it writes, so regenerating no longer
  undoes `ruff format`.

## 0.1.3

- Added `bodies`, which reads whole catalog categories and follows the
  `/v1/chart` paging itself. Reading 890 fixed stars is one call.

## 0.1.2

- Corrected the catalog example in the README: a page is a window over the
  whole selection, so a category can be absent from a page and must be read
  with `.get`.
- Documented the response envelope, `.data` / `.raw` / `.technique`, and
  `reset`.

## 0.1.1

- Install `httpx` with its SOCKS support, so a corporate proxy, a local SOCKS
  proxy or Tor needs nothing further installed.
- Check the API key in the constructor, before the transport is built, so a
  missing key is reported as a missing key rather than as a proxy failure.

## 0.1.0

- First public release. Every published endpoint, synchronous and
  asynchronous, with module-level shortcuts.
