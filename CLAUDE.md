# CLAUDE.md

Guidance for working on this repo.

## What this is

A frontend-only site that shows a cat colony, read live from a public Google
Sheet. Hosted on GitHub Pages at https://katylava.github.io/cat-colony/. No
backend, no framework, no build step — the whole app is one `index.html` of
plain HTML/CSS/JS.

## How to work on this repo

Claude owns the code. I care about the user experience, not how the site is
built — pick whatever structure, files, and build steps serve the UX and change
them freely. Don't ask me to choose between implementation approaches, and don't
use the chunked review workflow here. Do check with me on anything that changes
what a visitor sees or how the site behaves.

When you bring me one of those decisions, explain the trade-offs first. I'm
deciding about the site, not about the code, so tell me:

- What each option looks like to a visitor, or to me when I'm using the site or
  updating the sheet.
- What each one costs me — ongoing chores, waiting, things that can break, things
  I'd have to remember.
- Which one you'd pick and why.

Don't present it as a menu I have to decode. A decision that's really about
implementation isn't one of these — make that call yourself. And if an option
saddles me with a recurring manual step, say so plainly and up front rather than
mentioning it after I've agreed to it.

## Purpose (do not state it on the page)

The site is a credibility artifact for rescue organizations (showing the colony
is managed responsibly) and a status board for neighbors. Design decisions flow
from that, but the page must never announce why it exists. Keep the tone factual
and let the data speak.

## Files

- `index.html` — the entire app. Edit this for any UI or data-display change.
- `build_photos.py` — resolves the sheet's Google Photos share links into
  embeddable image URLs and writes `photos.json`.
- `photos.json` — generated (name → `{img, share}`). Do not hand-edit.

## The data

The sheet (ID `1UHlnzkYfQK-DDTvkqu8x-IDl3tB7L8fdiBQw_-V9GzY`) has one tab per
screen, plus a photo-lookup tab:

- `gid=0` — the colony (living here now)
- `gid=679410925` — adopted by the owner
- `gid=1859449606` — feral visitors (seen too rarely to trap)
- `gid=2113017747` — in memoriam
- `gid=869689683` — photo lookup (Name, Image URL, Share URL)
- `gid=1710528874` — news (Date, Update), not a screen — see below

`index.html` fetches the four data tabs live via the gviz JSON endpoint on every
load, so sheet edits appear on refresh with no rebuild. A cat is never listed on
more than one tab; its tab is its screen.

## Photos

The sheet's raw image URLs are account-private (403 for anyone but the owner),
so they can't be embedded. `build_photos.py` follows each share link to the
public `lh3.googleusercontent.com` image and records it. Photos therefore do NOT
update live — after adding or changing a photo in the sheet, run:

```sh
python build_photos.py
```

then commit `photos.json`.

## News

The News tab is a running log of colony updates: a `Date` and an `Update`. It
isn't a screen — it renders as a panel beside every screen (cat grids, search
results, a single cat's page), newest first, and it's live like the cat tabs, so
adding a row to the sheet is the whole publishing step.

The page is one grid with three regions: a full-width band (`#topbar` — stats,
blurb, back link), the cats (`#main`), and the news. The band spans both columns
and the other two share row two, which is what makes the news panel's top line
up with the first cat card. That alignment is why the band exists at all, so
anything added above the cats belongs in it rather than at the top of `#main`.

On a phone there's no room for a column, so the panel moves above the screen
content and shows only the newest entry, with the rest behind a "N more updates"
tap. That keeps what's new first without pushing the cats down the page.

Sorting reads the raw date cell, not the formatted one. `parseNews` is separate
from `parseGviz` for exactly this reason: `parseGviz` deliberately throws away
`c.v` (see Gotchas), but news needs a real `Date` to sort on. It parses
`Date(2026,7,3)` and falls back to parsing the display text.

## Per-cat screens

Every cat has its own URL — `https://katylava.github.io/cat-colony/#cat/deebo` —
so a link about one specific cat can be texted to a neighbor. The slug is the
name lowercased with runs of non-alphanumerics collapsed to `-`, so
`Thomas (aka Hey Hey)` is `#cat/thomas-aka-hey-hey`. It's a route, not a file:
a cat added to the sheet has a working link on the next page load, with nothing
to rebuild.

The screen shows the same card as the grid, capped in width and centered, with a
back link to the screen the cat lives on. A slug matching no cat says so rather
than showing an empty screen. Searching from a cat's screen takes over the view,
as it does everywhere else.

These links do NOT get rich previews when texted — the message shows the site's
generic title and no photo. That's deliberate. Preview crawlers don't run
JavaScript, so per-cat previews would mean generating a real HTML file per cat,
which means a build step someone has to run (or a scheduled job) every time the
sheet changes. That was judged not worth it. If it ever comes up again, the two
real options are a scheduled GitHub Action that regenerates and commits the
files, or a small server that renders the tags on request.

## Conventions the code encodes (don't "clean these up" without asking)

- **Neuter status** is a fixed vocabulary in the sheet: `yes` / `no` /
  `trapped and waiting`. Pills are screen-aware: a ✓ shows wherever a cat is
  fixed; the colony screen shows "not yet fixed" / "trapped & waiting"; feral
  visitors show "Not fixed — rarely seen"; adopted and gone cats show no
  negative pill (a fix-to-do is meaningless for them).
- **A trailing `(...)` in a column header is a value qualifier, not part of the
  label** — e.g. `Last Flea Treatment (Sentry topical)` renders as label "Last
  Flea Treatment" with "(Sentry topical)" folded into the value.
- **`Statement`** is a per-cat blurb, rendered as its own block, shown only when
  filled in.
- **`Name` is the photo join key and the per-cat URL** — it must match between
  the photo tab and the data tabs, or the photo silently drops, and it's what
  `#cat/<slug>` is derived from. Renaming a cat changes its link, so a link
  already texted to someone stops resolving.
- The colony screen carries a stats strip: colony spay/neuter (with trapped &
  waiting), all-time spay/neuter, up for adoption, adopted, and remembered. The
  tiles stretch with the window, but the column count is pinned to 6, 3 or 2 —
  the divisors of six — so a wrap never strands a tile alone on its own row.
  Adding or removing a tile means revisiting those numbers. The strip lives in
  the full-width band above the two columns, not in the cat column, so it spans
  the page rather than stopping at the news sidebar.

## Gotchas

- gviz serializes date cells in `c.v` as `Date(2026,5,27)` (0-indexed month).
  `parseGviz` prefers `c.f` (the formatted value) to avoid this — keep it that
  way for any date column.
- `photos.app.goo.gl` links serve a JS interstitial to browser user-agents and a
  real redirect to curl-like ones. `build_photos.py` sends a curl UA on purpose.
- Both the gviz and CSV endpoints allow cross-origin fetch, which is why the
  browser-only app works.

## Working on it

- Node and Python are provided via mise. If a scratch dir outside a project
  errors, pin a version there with `mise use node@24.5.0`.
- Preview locally with `python -m http.server` in the repo root.
- Verify changes with a headless browser (Playwright) screenshotting the live
  URL or the local server — don't rely on driving the user's Chrome.
- Deploy = commit and push to `main`; GitHub Pages rebuilds in a minute or two.
