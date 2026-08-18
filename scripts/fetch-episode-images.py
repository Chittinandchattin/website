#!/usr/bin/env python3
"""Fetch per-episode cover art from Spotify Pathfinder and save local thumbnails."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import urllib.parse
import urllib.request
from datetime import UTC, datetime
from email.utils import parsedate_to_datetime
from pathlib import Path

from sips_common import EPISODES_PATH, download_file, episode_slug, episodes_with_numbers, load_episodes
from transcript_common import add_episode_selection_args, resolve_cli_episode_numbers

ROOT = Path(__file__).resolve().parent.parent
THUMBS_DIR = ROOT / "assets" / "episodes" / "thumbs"
SPOTIFY_SHOW_ID = "5XmmJuVjc7S4j0aElFIeeF"
SHOW_EPISODES_HASH = "e0e5ce27bd7748d2c59b4d44ba245a8992a05be75d6fabc3b20753fc8857444d"
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
)
BROWSER_HEADERS = {
    "User-Agent": USER_AGENT,
    "Accept": "application/json",
    "Referer": "https://open.spotify.com/",
    "App-Platform": "WebPlayer",
}


def normalize_title(text: str) -> str:
    text = (text or "").lower()
    text = re.sub(r"[^\w\s]", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def parse_published(value: str) -> str | None:
    if not value:
        return None
    try:
        return parsedate_to_datetime(value).strftime("%Y-%m-%d")
    except (TypeError, ValueError, IndexError):
        return None


def fetch_access_token(explicit: str | None = None) -> str:
    if explicit:
        return explicit.strip()
    env_token = os.environ.get("SPOTIFY_ACCESS_TOKEN", "").strip()
    if env_token:
        return env_token
    token_url = "https://open.spotify.com/get_access_token?reason=transport&productType=web_player"
    req = urllib.request.Request(token_url, headers=BROWSER_HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        token = (data.get("accessToken") or "").strip()
        if token:
            return token
    except Exception as exc:
        raise RuntimeError(
            "Could not fetch Spotify access token automatically. "
            "Open https://open.spotify.com/show/5XmmJuVjc7S4j0aElFIeeF in a browser, "
            "DevTools → Network → filter get_access_token → copy accessToken, then run:\n"
            "  $env:SPOTIFY_ACCESS_TOKEN = 'paste-token-here'\n"
            "  python scripts/fetch-episode-images.py\n"
            f"Original error: {exc}"
        ) from exc
    raise RuntimeError("Spotify access token response was empty.")


def pathfinder_show_episodes(token: str, show_id: str = SPOTIFY_SHOW_ID) -> list[dict]:
    """Return Spotify episode metadata with coverArt."""
    variables = json.dumps(
        {"limit": 100, "offset": 0, "uri": f"spotify:show:{show_id}"},
        separators=(",", ":"),
    )
    extensions = json.dumps(
        {"persistedQuery": {"sha256Hash": SHOW_EPISODES_HASH}},
        separators=(",", ":"),
    )
    query = urllib.parse.urlencode(
        {
            "operationName": "queryShowEpisodes",
            "variables": variables,
            "extensions": extensions,
        }
    )
    api_url = f"https://api-partner.spotify.com/pathfinder/v1/query?{query}"
    req = urllib.request.Request(
        api_url,
        headers={**BROWSER_HEADERS, "authorization": f"Bearer {token}"},
    )
    with urllib.request.urlopen(req, timeout=45) as resp:
        payload = json.loads(resp.read().decode("utf-8"))
    items = payload.get("data", {}).get("podcast", {}).get("episodes", {}).get("items", [])
    episodes: list[dict] = []
    for item in items:
        episode = item.get("episode") or {}
        episode_id = episode.get("id")
        title = (episode.get("name") or "").strip()
        if not episode_id or not title:
            continue
        release = (
            (episode.get("releaseDate") or {}).get("isoString")
            or (episode.get("releaseDate") or {}).get("isoString")
            or ""
        )
        release_day = release[:10] if release else None
        sources = (episode.get("coverArt") or {}).get("sources") or []
        best = max(sources, key=lambda s: int(s.get("width") or 0), default=None)
        image_url = (best or {}).get("url", "").strip()
        episodes.append(
            {
                "spotifyEpisodeId": episode_id,
                "title": title,
                "titleKey": normalize_title(title),
                "releaseDate": release_day,
                "imageUrl": image_url,
            }
        )
    return episodes


def match_spotify_episode(local_ep: dict, spotify_eps: list[dict]) -> dict | None:
    title_key = normalize_title(local_ep.get("title", ""))
    pub = parse_published(local_ep.get("published", ""))
    candidates = [ep for ep in spotify_eps if ep["titleKey"] == title_key]
    if not candidates and title_key:
        fuzzy = [ep for ep in spotify_eps if title_key in ep["titleKey"] or ep["titleKey"] in title_key]
        candidates = fuzzy
    if not candidates:
        return None
    if pub:
        for ep in candidates:
            if ep.get("releaseDate") == pub:
                return ep
    return candidates[0]


def pick_extension(url: str) -> str:
    path = urllib.parse.urlparse(url).path.lower()
    for ext in (".jpg", ".jpeg", ".png", ".webp"):
        if path.endswith(ext):
            return ext.lstrip(".")
    return "jpg"


def local_thumb_web_path(episode_number: int, ext: str = "jpg") -> str:
    return f"/assets/episodes/thumbs/{episode_slug(episode_number)}.{ext}"


def local_thumb_disk_path(episode_number: int, ext: str = "jpg") -> Path:
    return THUMBS_DIR / f"{episode_slug(episode_number)}.{ext}"


def load_episodes_payload() -> dict:
    if not EPISODES_PATH.exists():
        raise FileNotFoundError(f"Missing {EPISODES_PATH}. Run pull-episodes.py first.")
    return json.loads(EPISODES_PATH.read_text(encoding="utf-8"))


def save_episodes_payload(payload: dict) -> None:
    EPISODES_PATH.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def process_episode(
    local_ep: dict,
    spotify_ep: dict | None,
    *,
    force: bool,
    dry_run: bool,
) -> str:
    ep_num = local_ep["episodeNumber"]
    slug = episode_slug(ep_num)
    if spotify_ep is None:
        return f"{slug}: skip (no Spotify match for '{local_ep.get('title', '')[:40]}')"

    image_url = spotify_ep.get("imageUrl", "")
    if not image_url:
        return f"{slug}: skip (Spotify match has no coverArt)"

    ext = pick_extension(image_url)
    dest = local_thumb_disk_path(ep_num, ext)
    web_path = local_thumb_web_path(ep_num, ext)

    if dest.exists() and dest.stat().st_size > 0 and not force:
        local_ep.setdefault("localThumbPath", web_path)
        local_ep.setdefault("spotifyEpisodeId", spotify_ep["spotifyEpisodeId"])
        return f"{slug}: skip (thumb exists)"

    if dry_run:
        return (
            f"{slug}: would download {spotify_ep['spotifyEpisodeId']} "
            f"-> {dest.name} ({image_url[:70]}...)"
        )

    download_file(image_url, dest)
    local_ep["imageUrl"] = image_url
    local_ep["localThumbPath"] = web_path
    local_ep["spotifyEpisodeId"] = spotify_ep["spotifyEpisodeId"]
    local_ep["thumbUpdated"] = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
    size_kb = dest.stat().st_size / 1024
    return f"{slug}: wrote {dest.name} ({size_kb:.0f} KB)"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Download per-episode Spotify thumbnails into assets/episodes/thumbs/."
    )
    add_episode_selection_args(parser)
    parser.add_argument("--force", action="store_true", help="Re-download even if thumb exists")
    parser.add_argument("--dry-run", action="store_true", help="Print matches only; do not download")
    parser.add_argument(
        "--token",
        help="Spotify Bearer token (else SPOTIFY_ACCESS_TOKEN env or auto-fetch)",
    )
    args = parser.parse_args()

    episode_nums = resolve_cli_episode_numbers(args)
    if episode_nums is None:
        print("Error: use only one of --episode, --last, or --from/--to.", file=sys.stderr)
        return 1

    payload = load_episodes_payload()
    local_episodes = episodes_with_numbers(payload.get("episodes", []))
    if episode_nums:
        wanted = set(episode_nums)
        local_episodes = [ep for ep in local_episodes if ep.get("episodeNumber") in wanted]
    if not local_episodes:
        print("No episodes selected.", file=sys.stderr)
        return 1

    try:
        token = fetch_access_token(args.token)
        spotify_eps = pathfinder_show_episodes(token)
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    print(f"Spotify returned {len(spotify_eps)} episodes with cover art metadata.")
    print(f"Processing {len(local_episodes)} local episode(s)...")

    THUMBS_DIR.mkdir(parents=True, exist_ok=True)
    ok = 0
    for local_ep in local_episodes:
        spotify_ep = match_spotify_episode(local_ep, spotify_eps)
        try:
            print(process_episode(local_ep, spotify_ep, force=args.force, dry_run=args.dry_run))
            ok += 1
        except Exception as exc:
            print(f"  ep {local_ep['episodeNumber']:02d}: ERROR {exc}", file=sys.stderr)

    if not args.dry_run:
        by_num = {ep.get("episodeNumber"): ep for ep in payload.get("episodes", [])}
        for local_ep in local_episodes:
            num = local_ep.get("episodeNumber")
            if num in by_num:
                for key in ("imageUrl", "localThumbPath", "spotifyEpisodeId", "thumbUpdated"):
                    if key in local_ep:
                        by_num[num][key] = local_ep[key]
        payload["thumbsUpdated"] = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
        save_episodes_payload(payload)
        print(f"Updated {EPISODES_PATH}")

    print(f"Done: {ok}/{len(local_episodes)} processed.")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
