#!/usr/bin/env python3
"""Download episode audio from RSS and trim to opening segment for transcription."""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import tempfile
import urllib.request
from pathlib import Path

from sips_common import (
    OPENING_SECONDS,
    OPENINGS_DIR,
    episodes_with_numbers,
    load_episodes,
    opening_audio_path,
)


def download_file(url: str, dest: Path) -> None:
    req = urllib.request.Request(url, headers={"User-Agent": "ChittinnchattinSite/1.0"})
    with urllib.request.urlopen(req, timeout=120) as resp, dest.open("wb") as out:
        while True:
            chunk = resp.read(1024 * 256)
            if not chunk:
                break
            out.write(chunk)


def trim_opening(source: Path, dest: Path, seconds: int) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        "ffmpeg",
        "-y",
        "-i",
        str(source),
        "-t",
        str(seconds),
        "-acodec",
        "copy",
        str(dest),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "ffmpeg failed")


def process_episode(episode: dict, seconds: int, keep_full: bool) -> str:
    ep_num = episode["episodeNumber"]
    audio_url = episode.get("audioUrl")
    if not audio_url:
        return f"ep {ep_num:02d}: skip (no audioUrl)"

    dest = opening_audio_path(ep_num)
    if dest.exists() and dest.stat().st_size > 0:
        return f"ep {ep_num:02d}: skip (clip exists)"

    OPENINGS_DIR.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        full_path = Path(tmp) / "full.mp3"
        print(f"  Downloading ep {ep_num:02d}…", flush=True)
        download_file(audio_url, full_path)
        trim_opening(full_path, dest, seconds)
        if keep_full:
            full_dest = OPENINGS_DIR / f"{dest.stem}-full.mp3"
            shutil.copy2(full_path, full_dest)

    size_mb = dest.stat().st_size / (1024 * 1024)
    return f"ep {ep_num:02d}: wrote {dest.name} ({size_mb:.1f} MB)"


def main() -> int:
    parser = argparse.ArgumentParser(description="Download and trim episode openings.")
    parser.add_argument("--seconds", type=int, default=OPENING_SECONDS, help="Trim length (default 600)")
    parser.add_argument("--keep-full", action="store_true", help="Keep full MP3 alongside clip")
    parser.add_argument("--episode", type=int, help="Only process this episode number")
    args = parser.parse_args()

    if not shutil.which("ffmpeg"):
        print("Error: ffmpeg not found on PATH. Install ffmpeg to trim audio.", file=sys.stderr)
        return 1

    episodes = episodes_with_numbers(load_episodes())
    if args.episode is not None:
        episodes = [ep for ep in episodes if ep.get("episodeNumber") == args.episode]
        if not episodes:
            print(f"Error: episode {args.episode} not found.", file=sys.stderr)
            return 1

    print(f"Processing {len(episodes)} episode(s), trim={args.seconds}s")
    for episode in episodes:
        if episode.get("episodeNumber") is None:
            print(f"  skip {episode.get('title', '?')}: no episodeNumber")
            continue
        try:
            print(process_episode(episode, args.seconds, args.keep_full))
        except Exception as exc:
            print(f"  ep {episode['episodeNumber']:02d}: ERROR {exc}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
