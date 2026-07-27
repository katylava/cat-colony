# CLAUDE.md

Guidance for working on this repo.

## What this is

A frontend-only site that shows a cat colony, read live from a public Google
Sheet. Hosted on GitHub Pages at https://katylava.github.io/cat-colony/. No
backend, no framework, no build step — the whole app is one `index.html` of
plain HTML/CSS/JS.

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
- **`Name` is the photo join key** — it must match between the photo tab and the
  data tabs, or the photo silently drops.
- The colony screen carries a stats strip: colony spay/neuter (with trapped &
  waiting), all-time spay/neuter, up for adoption, adopted, and remembered.

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
