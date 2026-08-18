#!/usr/bin/env python3
"""Shared helpers for full-episode transcription and annotation."""

from __future__ import annotations

import json
import re
from datetime import UTC, datetime
from pathlib import Path

from sips_common import (
    EPISODES_DIR,
    episode_slug,
    episodes_with_numbers,
    full_episode_audio_path,
    load_episodes,
)

ROOT = Path(__file__).resolve().parent.parent
FULL_TRANSCRIPTS_DIR = ROOT / "transcripts" / "episodes"
FUNNY_INDEX_PATH = ROOT / "transcripts" / "funny-index.md"
SCAN_LIST_MD_PATH = ROOT / "transcripts" / "scan-list.md"
SCAN_LIST_CSV_PATH = ROOT / "transcripts" / "scan-list.csv"

LAUGHTER_TEXT_RE = re.compile(
    r"\(?(?:laugh(?:ing|s|ter)?|giggles?|chuckles?|haha+|hehe+|lol)\)?",
    re.IGNORECASE,
)
LAUGHTER_ONLY_RE = re.compile(
    r"^\s*\(?(?:laugh(?:ing|s|ter)?|giggles?|chuckles?|haha+|hehe+|lol)\)?\.?\s*$",
    re.IGNORECASE,
)


def full_transcript_json_path(episode_number: int) -> Path:
    return FULL_TRANSCRIPTS_DIR / f"{episode_slug(episode_number)}.json"


def full_transcript_txt_path(episode_number: int) -> Path:
    return FULL_TRANSCRIPTS_DIR / f"{episode_slug(episode_number)}.txt"


def full_transcript_md_path(episode_number: int) -> Path:
    return FULL_TRANSCRIPTS_DIR / f"{episode_slug(episode_number)}.md"


def full_transcript_quotes_path(episode_number: int) -> Path:
    return FULL_TRANSCRIPTS_DIR / f"{episode_slug(episode_number)}.quotes-only.md"


def episode_meta_by_number() -> dict[int, dict]:
    """Chronological episodeNumber -> episode metadata."""
    return {ep["episodeNumber"]: ep for ep in episodes_with_numbers(load_episodes())}


def resolve_whisper_device(requested: str | None = None) -> tuple[str, str]:
    """Return (device, compute_type) for faster-whisper."""
    if requested == "cpu":
        return "cpu", "int8"
    if requested == "cuda":
        return "cuda", "float16"
    try:
        import torch

        if torch.cuda.is_available():
            return "cuda", "float16"
    except ImportError:
        pass
    return "cpu", "int8"


def transcribe_audio(
    audio: Path,
    model_name: str = "small",
    device: str | None = None,
    device_index: int | list[int] = 0,
) -> list[dict]:
    """Transcribe audio to segments with start/end/text using faster-whisper."""
    try:
        from faster_whisper import WhisperModel
    except ImportError as exc:
        raise RuntimeError(
            "faster-whisper not installed. Run: pip install -r scripts/requirements-transcripts.txt"
        ) from exc

    dev, compute = resolve_whisper_device(device)
    model = WhisperModel(
        model_name,
        device=dev,
        device_index=device_index,
        compute_type=compute,
    )
    segments_iter, _info = model.transcribe(
        str(audio),
        beam_size=5,
        vad_filter=True,
        word_timestamps=False,
    )
    segments = []
    for seg in segments_iter:
        text = (seg.text or "").strip()
        if not text:
            continue
        segments.append(
            {
                "start": round(float(seg.start), 2),
                "end": round(float(seg.end), 2),
                "text": text,
                "laughterAfter": False,
                "funny": False,
                "funnyNote": "",
            }
        )
    return segments


def segments_to_plain_text(segments: list[dict]) -> str:
    return " ".join(seg.get("text", "") for seg in segments if seg.get("text")).strip()


def build_transcript_payload(
    episode_number: int,
    segments: list[dict],
    *,
    model: str,
    device: str,
    audio_path: Path | None = None,
    laughter_events: list[dict] | None = None,
    annotated: bool = False,
) -> dict:
    meta = episode_meta_by_number().get(episode_number, {})
    payload = {
        "episodeNumber": episode_number,
        "title": meta.get("title", ""),
        "published": meta.get("published", ""),
        "link": meta.get("link", ""),
        "audioPath": str(audio_path) if audio_path else "",
        "model": model,
        "device": device,
        "updated": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "annotated": annotated,
        "segments": segments,
        "laughterEvents": laughter_events or [],
    }
    return payload


def load_transcript_json(episode_number: int) -> dict:
    path = full_transcript_json_path(episode_number)
    if not path.exists():
        raise FileNotFoundError(f"No transcript at {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def save_transcript_json(payload: dict) -> Path:
    ep_num = payload["episodeNumber"]
    path = full_transcript_json_path(ep_num)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    txt_path = full_transcript_txt_path(ep_num)
    txt_path.write_text(segments_to_plain_text(payload.get("segments", [])) + "\n", encoding="utf-8")
    return path


def list_episode_numbers() -> list[int]:
    if not EPISODES_DIR.exists():
        return []
    nums = []
    for path in sorted(EPISODES_DIR.glob("ep-*.mp3")):
        if path.name.endswith("-full.mp3"):
            continue
        try:
            nums.append(int(path.stem.split("-")[1]))
        except (IndexError, ValueError):
            continue
    return sorted(nums)


def list_transcript_episode_numbers() -> list[int]:
    """Episode numbers that already have transcript JSON."""
    if not FULL_TRANSCRIPTS_DIR.exists():
        return []
    nums = []
    for path in sorted(FULL_TRANSCRIPTS_DIR.glob("ep-*.json")):
        try:
            nums.append(int(path.stem.split("-")[1]))
        except (IndexError, ValueError):
            continue
    return sorted(nums)


def resolve_episode_numbers(
    *,
    episode: int | None = None,
    last: int | None = None,
    from_ep: int | None = None,
    to_ep: int | None = None,
) -> list[int]:
    """Resolve which episode numbers to process from CLI flags."""
    if episode is not None:
        return [episode]

    nums = list_episode_numbers()
    if not nums:
        nums = list_transcript_episode_numbers()

    nums = sorted(nums)
    if from_ep is not None or to_ep is not None:
        start = from_ep if from_ep is not None else nums[0]
        end = to_ep if to_ep is not None else nums[-1]
        return [n for n in nums if start <= n <= end]
    if last is not None:
        return nums[-last:] if last > 0 else []
    return nums


def resolve_cli_episode_numbers(args) -> list[int] | None:
    """Shared CLI episode selection for transcribe / annotate / export."""
    modes = []
    if getattr(args, "episode", None) is not None:
        modes.append("episode")
    if getattr(args, "last", None) is not None:
        modes.append("last")
    from_ep = getattr(args, "from_ep", None)
    to_ep = getattr(args, "to_ep", None)
    if from_ep is not None or to_ep is not None:
        modes.append("range")
    if len(modes) > 1:
        return None
    if from_ep is not None and to_ep is not None and from_ep > to_ep:
        return None
    return resolve_episode_numbers(
        episode=getattr(args, "episode", None),
        last=getattr(args, "last", None),
        from_ep=from_ep,
        to_ep=to_ep,
    )


def add_episode_selection_args(parser) -> None:
    parser.add_argument("--episode", type=int, help="Only process this episode number")
    parser.add_argument(
        "--last",
        type=int,
        metavar="N",
        help="Only process the last N episodes (by episode number)",
    )
    parser.add_argument("--from", dest="from_ep", type=int, metavar="N", help="Start episode (inclusive)")
    parser.add_argument("--to", dest="to_ep", type=int, metavar="N", help="End episode (inclusive)")


def format_timestamp(seconds: float) -> str:
    total = max(0, int(seconds))
    h, rem = divmod(total, 3600)
    m, s = divmod(rem, 60)
    if h:
        return f"{h:02d}:{m:02d}:{s:02d}"
    return f"{m:02d}:{s:02d}"


def normalize_laughter_text(text: str) -> tuple[str, bool]:
    """Strip laughter tokens from text; return (cleaned, had_laughter)."""
    if LAUGHTER_ONLY_RE.match(text or ""):
        return "", True
    had = bool(LAUGHTER_TEXT_RE.search(text or ""))
    cleaned = LAUGHTER_TEXT_RE.sub("", text or "")
    cleaned = re.sub(r"\s+", " ", cleaned).strip(" .,-")
    return cleaned, had


def dedupe_laughter_events(events: list[dict], min_gap: float = 1.5) -> list[dict]:
    if not events:
        return []
    ordered = sorted(events, key=lambda e: e["start"])
    merged = [ordered[0]]
    for event in ordered[1:]:
        prev = merged[-1]
        if event["start"] - prev["start"] < min_gap:
            continue
        merged.append(event)
    return merged
