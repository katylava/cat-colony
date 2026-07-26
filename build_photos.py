#!/usr/bin/env python
"""Resolve Google Photos share links from the sheet's photo tab into public,
embeddable image URLs and write them to photos.json.

The sheet stores each cat's photo as a `photos.app.goo.gl` share link. Those
open a viewer page, not an embeddable image, and the raw
`photos.fife.usercontent.google.com` URLs in the sheet are account-private
(403 for anyone but the owner). But the share page embeds a public
`lh3.googleusercontent.com/pw/<id>` URL that loads for anyone, at any size,
with a cross-origin resource policy that allows embedding.

Browsers can't do this resolution at runtime (the share page is CORS-blocked
and ~1MB each), so we resolve it here at build time and commit the result.
The frontend reads photos.json and appends a size suffix (e.g. `=w500`).
"""

import csv
import io
import json
import re
import sys
import urllib.request
from collections import Counter

SHEET_ID = "1UHlnzkYfQK-DDTvkqu8x-IDl3tB7L8fdiBQw_-V9GzY"
PHOTO_GID = "869689683"
PHOTO_CSV = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={PHOTO_GID}"

# The `pw/<id>` base of a public Google Photos image. We strip any size suffix
# (=w600-h315-...) so the frontend can request whatever size it wants.
LH3_RE = re.compile(r"https://lh3\.googleusercontent\.com/pw/[A-Za-z0-9_-]+")

# A browser-like UA makes goo.gl serve a JS interstitial that never redirects;
# a curl-like UA gets a plain server redirect through to the real share page.
UA = "curl/8.4.0"


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read().decode("utf-8", "replace")


def resolve_share_url(share_url):
    """Return the embeddable lh3 base URL for a share link, or None."""
    html = fetch(share_url)
    matches = LH3_RE.findall(html)
    if not matches:
        return None
    # The main photo's URL is repeated several times in the page markup;
    # avatars and other chrome appear once. The mode is the reliable pick.
    return Counter(matches).most_common(1)[0][0]


def main():
    rows = list(csv.DictReader(io.StringIO(fetch(PHOTO_CSV))))
    photos = {}
    for row in rows:
        name = (row.get("Name") or "").strip()
        share = (row.get("Share URL") or "").strip()
        if not name or not share:
            continue
        try:
            url = resolve_share_url(share)
        except Exception as e:
            print(f"  ! {name}: {e}", file=sys.stderr)
            continue
        if url:
            # img = embeddable image URL; share = the Google Photos page to open on click.
            photos[name] = {"img": url, "share": share}
            print(f"  ok {name}")
        else:
            print(f"  -- {name}: no embeddable image found", file=sys.stderr)

    with open("photos.json", "w") as f:
        json.dump(photos, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print(f"\nWrote {len(photos)} photos to photos.json")


if __name__ == "__main__":
    main()
