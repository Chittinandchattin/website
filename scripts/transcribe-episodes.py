#!/usr/bin/env python3
"""Transcribe full episode MP3s with faster-whisper (GPU when available)."""

from __future__ import annotations

import argparse
import multiprocessing as mp
import sys

from sips_common import full_episode_audio_path
from transcript_common import (
    FULL_TRANSCRIPTS_DIR,
    build_transcript_payload,
    full_transcript_json_path,
    add_episode_selection_args,
    resolve_cli_episode_numbers,
    resolve_whisper_device,
    save_transcript_json,
    transcribe_audio,
)


def _gpu_count() -> int:
    try:
        import torch

        if torch.cuda.is_available():
            return torch.cuda.device_count()
    except ImportError:
        pass
    return 0


def _transcribe_episodes(
    episode_nums: list[int],
    *,
    model: str,
    device_arg: str | None,
    device_index: int,
    force: bool,
) -> tuple[int, int]:
    device, _compute = resolve_whisper_device(device_arg)
    ok = 0
    for ep_num in episode_nums:
        audio = full_episode_audio_path(ep_num)
        if not audio.exists():
            print(f"  [gpu {device_index}] ep {ep_num:02d}: skip (no audio)", flush=True)
            continue

        out_json = full_transcript_json_path(ep_num)
        if out_json.exists() and not force:
            print(f"  [gpu {device_index}] ep {ep_num:02d}: skip (transcript exists)", flush=True)
            ok += 1
            continue

        print(f"  [gpu {device_index}] Transcribing ep {ep_num:02d} ({audio.name})…", flush=True)
        try:
            segments = transcribe_audio(
                audio,
                model_name=model,
                device=device_arg,
                device_index=device_index,
            )
            payload = build_transcript_payload(
                ep_num,
                segments,
                model=model,
                device=f"{device}:{device_index}",
                audio_path=audio,
            )
            save_transcript_json(payload)
            print(f"  [gpu {device_index}] ep {ep_num:02d}: wrote {len(segments)} segments", flush=True)
            ok += 1
        except Exception as exc:
            print(f"  [gpu {device_index}] ep {ep_num:02d}: ERROR {exc}", file=sys.stderr, flush=True)
    return ok, len(episode_nums)


def _worker(args: tuple[list[int], str, str | None, int, bool]) -> tuple[int, int]:
    episode_nums, model, device_arg, device_index, force = args
    return _transcribe_episodes(
        episode_nums,
        model=model,
        device_arg=device_arg,
        device_index=device_index,
        force=force,
    )


def _split_episodes(episode_nums: list[int], parts: int) -> list[list[int]]:
    buckets: list[list[int]] = [[] for _ in range(parts)]
    for idx, ep_num in enumerate(episode_nums):
        buckets[idx % parts].append(ep_num)
    return [bucket for bucket in buckets if bucket]


def main() -> int:
    parser = argparse.ArgumentParser(description="Transcribe full episodes to JSON + TXT.")
    parser.add_argument("--model", default="small", help="Whisper model (default: small)")
    parser.add_argument(
        "--device",
        choices=("auto", "cuda", "cpu"),
        default="auto",
        help="Compute device (default: auto-detect CUDA)",
    )
    parser.add_argument(
        "--gpu-index",
        type=int,
        default=None,
        help="Use a specific CUDA device index (disables multi-GPU split)",
    )
    parser.add_argument(
        "--parallel-gpus",
        action="store_true",
        help="Split episodes across all visible CUDA devices",
    )
    add_episode_selection_args(parser)
    parser.add_argument("--force", action="store_true", help="Overwrite existing transcripts")
    args = parser.parse_args()

    episode_nums = resolve_cli_episode_numbers(args)
    if episode_nums is None:
        print("Error: use only one of --episode, --last, or --from/--to.", file=sys.stderr)
        return 1
    if args.episode is not None:
        audio = full_episode_audio_path(args.episode)
        if not audio.exists():
            print(f"Error: no audio at {audio}. Run download-episodes.py first.", file=sys.stderr)
            return 1

    device_arg = None if args.device == "auto" else args.device
    device, _compute = resolve_whisper_device(device_arg)

    if not episode_nums:
        print("No full episode MP3s found. Run scripts/download-episodes.py first.", file=sys.stderr)
        return 1

    FULL_TRANSCRIPTS_DIR.mkdir(parents=True, exist_ok=True)

    gpu_total = _gpu_count()
    use_parallel = args.parallel_gpus and device != "cpu" and gpu_total > 1 and args.gpu_index is None
    if args.parallel_gpus and not use_parallel:
        if device == "cpu":
            print("Warning: --parallel-gpus ignored (CPU mode).", file=sys.stderr)
        elif gpu_total <= 1:
            print("Warning: --parallel-gpus ignored (only one CUDA device visible).", file=sys.stderr)

    if use_parallel:
        print(
            f"Device: cuda x{gpu_total} (parallel) | Model: {args.model} | Episodes: {len(episode_nums)}",
            flush=True,
        )
        buckets = _split_episodes(episode_nums, gpu_total)
        for idx, bucket in enumerate(buckets):
            print(f"  GPU {idx}: {len(bucket)} episodes -> {', '.join(f'{n:02d}' for n in bucket)}", flush=True)

        worker_args = [
            (bucket, args.model, device_arg, gpu_index, args.force)
            for gpu_index, bucket in enumerate(buckets)
        ]
        with mp.Pool(processes=len(worker_args)) as pool:
            results = pool.map(_worker, worker_args)
        ok = sum(r[0] for r in results)
        total = sum(r[1] for r in results)
    else:
        gpu_index = args.gpu_index if args.gpu_index is not None else 0
        label = f"{device}:{gpu_index}" if device == "cuda" else device
        print(f"Device: {label} | Model: {args.model} | Episodes: {len(episode_nums)}", flush=True)
        ok, total = _transcribe_episodes(
            episode_nums,
            model=args.model,
            device_arg=device_arg,
            device_index=gpu_index,
            force=args.force,
        )

    print(f"Done: {ok}/{len(episode_nums)} transcripts", flush=True)
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
