#!/usr/bin/env python3
"""Pull episode titles and descriptions from the Anchor/Spotify RSS feed."""

import html
import json
import re
import sys
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

FEED_URL = "https://anchor.fm/s/10d11a464/podcast/rss"
SPOTIFY_SHOW_URL = "https://open.spotify.com/show/5XmmJuVjc7S4j0aElFIeeF"
ITUNES_NS = "http://www.itunes.com/dtds/podcast-1.0.dtd"
ROOT = Path(__file__).resolve().parent.parent
OUT_PATH = ROOT / "assets" / "data" / "episodes.json"


def normalize_dashes(text: str) -> str:
    if not text:
        return ""
    return text.replace("\u2014", "-").replace("\u2013", "-")


def strip_html(text: str) -> str:
    if not text:
        return ""
    text = html.unescape(text)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return normalize_dashes(text)


def text_of(elem) -> str:
    if elem is None:
        return ""
    return "".join(elem.itertext()).strip()


def itunes_tag(name: str) -> str:
    return f"{{{ITUNES_NS}}}{name}"


def parse_int(value: str) -> int | None:
    if not value:
        return None
    try:
        return int(value.strip())
    except ValueError:
        return None


def itunes_image(elem) -> str:
    if elem is None:
        return ""
    img = elem.find(itunes_tag("image"))
    if img is not None and img.get("href"):
        return img.get("href", "").strip()
    return ""


def fetch_spotify_show_thumbnail(show_url: str) -> str:
    """Official Spotify square art via oEmbed (no API key)."""
    try:
        q = urllib.parse.urlencode({"url": show_url.split("?")[0]})
        req = urllib.request.Request(
            f"https://open.spotify.com/oembed?{q}",
            headers={"User-Agent": "ChittinnchattinSite/1.0"},
        )
        with urllib.request.urlopen(req, timeout=20) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        return (data.get("thumbnail_url") or "").strip()
    except Exception:
        return ""


def fetch_episodes(feed_url: str) -> tuple[list[dict], str, str]:
    req = urllib.request.Request(feed_url, headers={"User-Agent": "ChittinnchattinSite/1.0"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = resp.read()

    root = ET.fromstring(data)
    channel = root.find("channel")
    if channel is None:
        raise RuntimeError("No channel in RSS feed")

    channel_image = itunes_image(channel)
    spotify_thumbnail = fetch_spotify_show_thumbnail(SPOTIFY_SHOW_URL)

    episodes = []
    for item in channel.findall("item"):
        title = normalize_dashes(text_of(item.find("title")))
        desc_elem = item.find("description")
        if desc_elem is None:
            desc_elem = item.find("{http://purl.org/rss/1.0/modules/content/}encoded")
        description = strip_html(text_of(desc_elem))
        pub = text_of(item.find("pubDate"))
        link = text_of(item.find("link"))
        enclosure = item.find("enclosure")
        audio_url = enclosure.get("url", "") if enclosure is not None else ""
        duration = text_of(item.find(itunes_tag("duration")))
        episode_number = parse_int(text_of(item.find(itunes_tag("episode"))))
        item_rss = itunes_image(item)
        if item_rss and channel_image and item_rss != channel_image:
            item_image = item_rss
        else:
            item_image = spotify_thumbnail or item_rss or channel_image
        if not title:
            continue
        episode: dict = {
            "title": title,
            "description": description,
            "published": pub,
            "link": link,
            "imageUrl": item_image,
        }
        if audio_url:
            episode["audioUrl"] = audio_url
        if duration:
            episode["duration"] = duration
        if episode_number is not None:
            episode["episodeNumber"] = episode_number
        episodes.append(episode)

    return episodes, spotify_thumbnail, channel_image


def main() -> int:
    try:
        episodes, spotify_thumbnail, channel_image = fetch_episodes(FEED_URL)
    except Exception as exc:
        print(f"Error fetching feed: {exc}", file=sys.stderr)
        return 1

    from datetime import UTC, datetime

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "feedUrl": FEED_URL,
        "spotifyShowUrl": SPOTIFY_SHOW_URL,
        "spotifyThumbnailUrl": spotify_thumbnail,
        "channelImageUrl": channel_image,
        "updated": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "count": len(episodes),
        "episodes": episodes,
    }
    OUT_PATH.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {len(episodes)} episodes to {OUT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
