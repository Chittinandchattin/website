#!/usr/bin/env python3
"""Pull episode titles and descriptions from the Anchor/Spotify RSS feed."""

import html
import json
import re
import sys
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

FEED_URL = "https://anchor.fm/s/10d11a464/podcast/rss"
ROOT = Path(__file__).resolve().parent.parent
OUT_PATH = ROOT / "assets" / "data" / "episodes.json"


def strip_html(text: str) -> str:
    if not text:
        return ""
    text = html.unescape(text)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def text_of(elem) -> str:
    if elem is None:
        return ""
    return "".join(elem.itertext()).strip()


def fetch_episodes(feed_url: str) -> list[dict]:
    req = urllib.request.Request(feed_url, headers={"User-Agent": "ChittinnchattinSite/1.0"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = resp.read()

    root = ET.fromstring(data)
    channel = root.find("channel")
    if channel is None:
        raise RuntimeError("No channel in RSS feed")

    episodes = []
    for item in channel.findall("item"):
        title = text_of(item.find("title"))
        desc_elem = item.find("description")
        if desc_elem is None:
            desc_elem = item.find("{http://purl.org/rss/1.0/modules/content/}encoded")
        description = strip_html(text_of(desc_elem))
        pub = text_of(item.find("pubDate"))
        link = text_of(item.find("link"))
        if not title:
            continue
        episodes.append(
            {
                "title": title,
                "description": description,
                "published": pub,
                "link": link,
            }
        )

    return episodes


def main() -> int:
    try:
        episodes = fetch_episodes(FEED_URL)
    except Exception as exc:
        print(f"Error fetching feed: {exc}", file=sys.stderr)
        return 1

    from datetime import UTC, datetime

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "feedUrl": FEED_URL,
        "updated": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "count": len(episodes),
        "episodes": episodes,
    }
    OUT_PATH.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {len(episodes)} episodes to {OUT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
