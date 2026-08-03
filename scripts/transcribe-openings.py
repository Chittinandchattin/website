#!/usr/bin/env python3
"""Transcribe opening audio clips with local Whisper."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from sips_common import OPENINGS_DIR, TRANSCRIPTS_DIR, opening_audio_path, transcript_path


def transcribe_with_whisper(audio: Path, model_name: str) -> str:
    try:
        import whisper
    except ImportError as exc:
        raise RuntimeError(
            "openai-whisper not installed. Run: pip install openai-whisper"
        ) from exc

    model = whisper.load_model(model_name)
    result = model.transcribe(str(audio), fp16=False)
    return (result.get("text") or "").strip()


def transcribe_with_faster_whisper(audio: Path, model_name: str) -> str:
    try:
        from faster_whisper import WhisperModel
    except ImportError as exc:
        raise RuntimeError(
            "faster-whisper not installed. Run: pip install faster-whisper"
        ) from exc

    model = WhisperModel(model_name, device="cpu", compute_type="int8")
    segments, _info = model.transcribe(str(audio), beam_size=5)
    return " ".join(segment.text.strip() for segment in segments).strip()


def transcribe_file(audio: Path, model_name: str, engine: str) -> str:
    if engine == "faster-whisper":
        return transcribe_with_faster_whisper(audio, model_name)
    return transcribe_with_whisper(audio, model_name)


def main() -> int:
    parser = argparse.ArgumentParser(description="Transcribe opening audio clips.")
    parser.add_argument("--model", default="base", help="Whisper model (default: base)")
    parser.add_argument(
        "--engine",
        choices=("whisper", "faster-whisper"),
        default="whisper",
        help="Transcription backend",
    )
    parser.add_argument("--episode", type=int, help="Only transcribe this episode number")
    parser.add_argument("--force", action="store_true", help="Overwrite existing transcripts")
    args = parser.parse_args()

    if args.episode is not None:
        clips = [opening_audio_path(args.episode)]
        if not clips[0].exists():
            print(f"Error: no audio clip at {clips[0]}", file=sys.stderr)
            return 1
    else:
        clips = sorted(OPENINGS_DIR.glob("ep-*.mp3"))
        clips = [p for p in clips if not p.name.endswith("-full.mp3")]

    if not clips:
        print("No opening clips found. Run scripts/download-openings.py first.", file=sys.stderr)
        return 1

    TRANSCRIPTS_DIR.mkdir(parents=True, exist_ok=True)
    ok = 0
    for audio in clips:
        ep_num = int(audio.stem.split("-")[1])
        out = transcript_path(ep_num)
        if out.exists() and not args.force:
            print(f"  ep {ep_num:02d}: skip (transcript exists)")
            ok += 1
            continue
        print(f"  Transcribing ep {ep_num:02d}…", flush=True)
        try:
            text = transcribe_file(audio, args.model, args.engine)
            out.write_text(text + "\n", encoding="utf-8")
            print(f"  ep {ep_num:02d}: wrote {out.name} ({len(text)} chars)")
            ok += 1
        except Exception as exc:
            print(f"  ep {ep_num:02d}: ERROR {exc}", file=sys.stderr)

    print(f"Done: {ok}/{len(clips)} transcripts")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
