#!/usr/bin/env python3
"""Annotate full transcripts with laughter markers and Ollama funny flags."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

import requests

from sips_common import full_episode_audio_path
from transcript_common import (
    FULL_TRANSCRIPTS_DIR,
    dedupe_laughter_events,
    full_transcript_json_path,
    load_transcript_json,
    normalize_laughter_text,
    add_episode_selection_args,
    resolve_cli_episode_numbers,
    save_transcript_json,
)

OLLAMA_URL = "http://localhost:11434/api/generate"
DEFAULT_OLLAMA_MODEL = "llama3.1:8b"
CHUNK_MAX_SECONDS = 150  # ~2.5 minutes per LLM batch


def detect_audio_laughter(audio_path: Path, segments: list[dict]) -> list[dict]:
    """Find laughter-like energy bursts in gaps between speech segments."""
    try:
        import librosa
        import numpy as np
    except ImportError as exc:
        raise RuntimeError("librosa required. pip install -r scripts/requirements-transcripts.txt") from exc

    y, sr = librosa.load(str(audio_path), sr=16000, mono=True)
    duration = len(y) / sr
    frame_length = 1024
    hop = 256
    rms = librosa.feature.rms(y=y, frame_length=frame_length, hop_length=hop)[0]
    times = librosa.frames_to_time(np.arange(len(rms)), sr=sr, hop_length=hop)

    if len(rms) == 0:
        return []

    baseline = float(np.median(rms))
    spread = float(np.std(rms))
    threshold = baseline + max(0.02, spread * 2.2)

    speech_mask = np.zeros(len(times), dtype=bool)
    for seg in segments:
        start = max(0.0, seg["start"] - 0.15)
        end = min(duration, seg["end"] + 0.15)
        speech_mask |= (times >= start) & (times <= end)

    events: list[dict] = []
    i = 0

    def in_speech(t: float) -> bool:
        for seg in segments:
            if seg["start"] <= t <= seg["end"]:
                return True
        return False

    while i < len(rms):
        if speech_mask[i] or rms[i] < threshold:
            i += 1
            continue
        j = i
        while j < len(rms) and rms[j] >= threshold * 0.85:
            j += 1
        start_t = float(times[i])
        end_t = float(times[min(j, len(times) - 1)])
        span = end_t - start_t
        if 0.18 <= span <= 3.5:
            peak = float(np.max(rms[i:j]))
            mid = (start_t + end_t) / 2
            if peak >= threshold and not in_speech(mid):
                events.append(
                    {
                        "start": round(start_t, 2),
                        "end": round(end_t, 2),
                        "source": "audio",
                    }
                )
        i = max(j, i + 1)

    return dedupe_laughter_events(events)


def detect_text_laughter(segments: list[dict]) -> list[dict]:
    events: list[dict] = []
    cleaned_segments: list[dict] = []
    for seg in segments:
        copy = dict(seg)
        text, had = normalize_laughter_text(copy.get("text", ""))
        copy["text"] = text
        if had:
            copy["laughterAfter"] = True
            events.append(
                {
                    "start": round(copy["end"], 2),
                    "end": round(copy["end"] + 0.5, 2),
                    "source": "text",
                }
            )
        cleaned_segments.append(copy)
    return cleaned_segments, dedupe_laughter_events(events)


def apply_laughter_to_segments(segments: list[dict], events: list[dict]) -> list[dict]:
    for seg in segments:
        seg["laughterAfter"] = bool(seg.get("laughterAfter"))
    for event in events:
        best_idx = None
        best_dist = 999.0
        for idx, seg in enumerate(segments):
            dist = abs(event["start"] - seg["end"])
            if dist < best_dist and dist <= 1.2:
                best_dist = dist
                best_idx = idx
        if best_idx is not None:
            segments[best_idx]["laughterAfter"] = True
    return segments


def annotate_laughter(payload: dict, audio_path: Path) -> dict:
    segments = payload.get("segments", [])
    segments, text_events = detect_text_laughter(segments)
    audio_events: list[dict] = []
    if audio_path.exists():
        try:
            audio_events = detect_audio_laughter(audio_path, segments)
        except Exception as exc:
            print(f"    audio laughter warning: {exc}", file=sys.stderr)
    all_events = dedupe_laughter_events(text_events + audio_events)
    segments = apply_laughter_to_segments(segments, all_events)
    payload["segments"] = segments
    payload["laughterEvents"] = all_events
    return payload


def chunk_segments(segments: list[dict], max_seconds: float) -> list[list[tuple[int, dict]]]:
    chunks: list[list[tuple[int, dict]]] = []
    current: list[tuple[int, dict]] = []
    span = 0.0
    chunk_start = segments[0]["start"] if segments else 0.0
    for idx, seg in enumerate(segments):
        if not current:
            chunk_start = seg["start"]
        current.append((idx, seg))
        span = seg["end"] - chunk_start
        if span >= max_seconds:
            chunks.append(current)
            current = []
    if current:
        chunks.append(current)
    return chunks


def ollama_available(base_url: str = OLLAMA_URL) -> bool:
    try:
        host = base_url.replace("/api/generate", "")
        r = requests.get(f"{host}/api/tags", timeout=3)
        return r.status_code == 200
    except requests.RequestException:
        return False


def call_ollama(prompt: str, model: str, base_url: str = OLLAMA_URL) -> str:
    resp = requests.post(
        base_url,
        json={
            "model": model,
            "prompt": prompt,
            "stream": False,
            "format": "json",
            "options": {"temperature": 0.2},
        },
        timeout=300,
    )
    resp.raise_for_status()
    data = resp.json()
    return (data.get("response") or "").strip()


def build_funny_prompt(title: str, chunk: list[tuple[int, dict]]) -> str:
    lines = []
    for idx, seg in chunk:
        lines.append(f'{idx}: [{seg["start"]:.1f}s] {seg["text"]}')
    body = "\n".join(lines)
    return f"""You annotate a podcast transcript for quotable funny moments.

Show: Chittin' and Chattin' (two besties, chaotic humor, Spill It Bestie energy).
Episode: {title}

Flag lines that are funny, absurd, quotable, or messy-bestie chaos.
Do NOT flag heavy trauma/healing unless the line itself is a clear punchline or ironic joke.

Return JSON only:
{{"segments":[{{"index":0,"funny":false}},{{"index":1,"funny":true,"quote":"short pull quote"}}]}}

Include every index from the list below exactly once.

Transcript lines:
{body}
"""


def parse_funny_response(raw: str) -> list[dict]:
    raw = raw.strip()
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", raw, re.DOTALL)
        if not match:
            return []
        data = json.loads(match.group(0))
    return data.get("segments") or []


def annotate_funny(payload: dict, model: str, base_url: str = OLLAMA_URL) -> dict:
    segments = payload.get("segments", [])
    if not segments:
        return payload

    title = payload.get("title", "Unknown episode")
    for chunk in chunk_segments(segments, CHUNK_MAX_SECONDS):
        prompt = build_funny_prompt(title, chunk)
        try:
            raw = call_ollama(prompt, model, base_url)
            results = parse_funny_response(raw)
        except Exception as exc:
            print(f"    Ollama chunk error: {exc}", file=sys.stderr)
            continue
        by_index = {item.get("index"): item for item in results if "index" in item}
        for idx, seg in chunk:
            item = by_index.get(idx)
            if not item:
                continue
            if item.get("funny"):
                segments[idx]["funny"] = True
                quote = (item.get("quote") or "").strip()
                if quote:
                    segments[idx]["funnyNote"] = quote
    payload["segments"] = segments
    return payload


def process_episode(
    ep_num: int,
    *,
    skip_funny: bool,
    ollama_model: str,
    ollama_url: str,
) -> str:
    path = full_transcript_json_path(ep_num)
    if not path.exists():
        return f"ep {ep_num:02d}: skip (no transcript JSON; run transcribe-episodes.py)"

    payload = load_transcript_json(ep_num)
    audio = full_episode_audio_path(ep_num)
    if payload.get("audioPath"):
        audio = Path(payload["audioPath"])

    payload = annotate_laughter(payload, audio)

    if not skip_funny:
        if ollama_available(ollama_url):
            payload = annotate_funny(payload, ollama_model, ollama_url)
        else:
            print(f"    ep {ep_num:02d}: Ollama not running; skipping funny pass", file=sys.stderr)

    payload["annotated"] = True
    save_transcript_json(payload)
    laugh_n = len(payload.get("laughterEvents", []))
    funny_n = sum(1 for s in payload.get("segments", []) if s.get("funny"))
    return f"ep {ep_num:02d}: annotated ({laugh_n} laughter, {funny_n} funny)"


def main() -> int:
    parser = argparse.ArgumentParser(description="Add laughter + funny annotations to transcripts.")
    add_episode_selection_args(parser)
    parser.add_argument("--skip-funny", action="store_true", help="Laughter only; skip Ollama")
    parser.add_argument("--ollama-model", default=DEFAULT_OLLAMA_MODEL, help="Ollama model name")
    parser.add_argument("--ollama-url", default=OLLAMA_URL, help="Ollama generate API URL")
    args = parser.parse_args()

    episode_nums = resolve_cli_episode_numbers(args)
    if episode_nums is None:
        print("Error: use only one of --episode, --last, or --from/--to.", file=sys.stderr)
        return 1

    if not episode_nums:
        print("No transcripts found. Run transcribe-episodes.py first.", file=sys.stderr)
        return 1

    ok = 0
    for ep_num in episode_nums:
        try:
            print(process_episode(
                ep_num,
                skip_funny=args.skip_funny,
                ollama_model=args.ollama_model,
                ollama_url=args.ollama_url,
            ))
            ok += 1
        except Exception as exc:
            print(f"  ep {ep_num:02d}: ERROR {exc}", file=sys.stderr)

    print(f"Done: {ok}/{len(episode_nums)} annotated")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
