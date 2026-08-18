#!/usr/bin/env python3
"""Download full episode MP3s from RSS enclosure URLs in episodes.json."""

from __future__ import annotations

import argparse
import sys

from sips_common import (
    EPISODES_DIR,
    download_file,
    episodes_with_numbers,
    full_episode_audio_path,
    load_episodes,
)


def process_episode(episode: dict, force: bool) -> str:
    ep_num = episode["episodeNumber"]
    audio_url = episode.get("audioUrl")
    if not audio_url:
        return f"ep {ep_num:02d}: skip (no audioUrl in RSS data)"

    dest = full_episode_audio_path(ep_num)
    if dest.exists() and dest.stat().st_size > 0 and not force:
        size_mb = dest.stat().st_size / (1024 * 1024)
        return f"ep {ep_num:02d}: skip (exists, {size_mb:.1f} MB)"

    print(f"  Downloading ep {ep_num:02d}…", flush=True)
    download_file(audio_url, dest)
    size_mb = dest.stat().st_size / (1024 * 1024)
    return f"ep {ep_num:02d}: wrote {dest.name} ({size_mb:.1f} MB)"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Download full episode audio from the Anchor/Spotify RSS feed."
    )
    parser.add_argument("--episode", type=int, help="Only download this episode number (1-based)")
    parser.add_argument(
        "--force",
        action="store_true",
        help="Re-download even if the MP3 already exists",
    )
    args = parser.parse_args()

    episodes = episodes_with_numbers(load_episodes())
    if args.episode is not None:
        episodes = [ep for ep in episodes if ep.get("episodeNumber") == args.episode]
        if not episodes:
            print(f"Error: episode {args.episode} not found.", file=sys.stderr)
            return 1

    EPISODES_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Saving to {EPISODES_DIR}")
    print(f"Processing {len(episodes)} episode(s)")

    ok = 0
    for episode in episodes:
        try:
            print(process_episode(episode, args.force))
            ok += 1
        except Exception as exc:
            print(f"  ep {episode['episodeNumber']:02d}: ERROR {exc}", file=sys.stderr)

    print(f"Done ({ok}/{len(episodes)} processed).")
    return 0 if ok == len(episodes) else 1


if __name__ == "__main__":
    raise SystemExit(main())
