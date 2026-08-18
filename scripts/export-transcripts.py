#!/usr/bin/env python3
"""Export annotated transcripts to Markdown and a cross-episode funny index."""

from __future__ import annotations

import argparse
import csv
import sys
from datetime import UTC, datetime

from transcript_common import (
    FUNNY_INDEX_PATH,
    FULL_TRANSCRIPTS_DIR,
    SCAN_LIST_CSV_PATH,
    SCAN_LIST_MD_PATH,
    add_episode_selection_args,
    format_timestamp,
    full_transcript_json_path,
    full_transcript_md_path,
    full_transcript_quotes_path,
    load_transcript_json,
    resolve_cli_episode_numbers,
)


def render_episode_markdown(payload: dict) -> str:
    ep_num = payload.get("episodeNumber", 0)
    title = payload.get("title") or f"Episode {ep_num}"
    lines = [f"# Ep {ep_num} - {title}", ""]
    if payload.get("link"):
        lines.append(f"Listen: {payload['link']}")
        lines.append("")

    for seg in payload.get("segments", []):
        text = (seg.get("text") or "").strip()
        ts = format_timestamp(seg.get("start", 0))
        if seg.get("funny"):
            quote = (seg.get("funnyNote") or text).strip()
            lines.append(f"[{ts}] >> FUNNY: {quote}")
        elif text:
            lines.append(f"[{ts}] {text}")
        if seg.get("laughterAfter"):
            lines.append("")
            lines.append("[LAUGHTER]")
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def render_quotes_only(payload: dict) -> str:
    ep_num = payload.get("episodeNumber", 0)
    title = payload.get("title") or f"Episode {ep_num}"
    lines = [f"# Ep {ep_num} - Funny quotes only", ""]
    found = False
    for seg in payload.get("segments", []):
        if not seg.get("funny"):
            continue
        found = True
        ts = format_timestamp(seg.get("start", 0))
        quote = (seg.get("funnyNote") or seg.get("text") or "").strip()
        lines.append(f"- [{ts}] {quote}")
    if not found:
        lines.append("_No funny flags in this episode._")
    lines.append("")
    return "\n".join(lines)


def build_funny_index(episodes: list[dict]) -> str:
    lines = [
        "# Chittin' and Chattin' - Funny index",
        "",
        f"Generated: {datetime.now(UTC).strftime('%Y-%m-%d %H:%M UTC')}",
        "",
        "Pull quotes flagged by the annotation pipeline (`>> FUNNY` in full transcripts).",
        "",
    ]
    total = 0
    for payload in episodes:
        ep_num = payload.get("episodeNumber", 0)
        title = payload.get("title", "")
        md_name = full_transcript_md_path(ep_num).name
        for seg in payload.get("segments", []):
            if not seg.get("funny"):
                continue
            total += 1
            ts = format_timestamp(seg.get("start", 0))
            quote = (seg.get("funnyNote") or seg.get("text") or "").strip()
            lines.append(f"## Ep {ep_num} [{ts}] - {title}")
            lines.append(f"> {quote}")
            lines.append(f"Full transcript: `transcripts/episodes/{md_name}`")
            lines.append("")

    if total == 0:
        lines.append("_No funny lines flagged yet. Run annotate-transcripts.py with Ollama running._")
        lines.append("")
    else:
        lines.insert(4, f"**Total flagged:** {total}")
        lines.insert(5, "")

    return "\n".join(lines)


def collect_scan_entries(payload: dict) -> list[dict]:
    """Flat rows for scan-list export: funny lines and laughter moments."""
    ep_num = payload.get("episodeNumber", 0)
    title = payload.get("title") or f"Episode {ep_num}"
    rows: list[dict] = []
    for seg in payload.get("segments", []):
        ts = format_timestamp(seg.get("start", 0))
        seconds = float(seg.get("start", 0))
        text = (seg.get("text") or "").strip()
        if seg.get("funny"):
            rows.append(
                {
                    "episode": ep_num,
                    "title": title,
                    "timestamp": ts,
                    "seconds": seconds,
                    "type": "FUNNY",
                    "quote": (seg.get("funnyNote") or text or "").strip(),
                }
            )
        if seg.get("laughterAfter"):
            rows.append(
                {
                    "episode": ep_num,
                    "title": title,
                    "timestamp": ts,
                    "seconds": seconds,
                    "type": "LAUGHTER",
                    "quote": text or "(laughter)",
                }
            )
    rows.sort(key=lambda r: (r["episode"], r["seconds"], r["type"]))
    return rows


def build_scan_list_markdown(episodes: list[dict]) -> str:
    lines = [
        "# Chittin' and Chattin' — Scan list",
        "",
        f"Generated: {datetime.now(UTC).strftime('%Y-%m-%d %H:%M UTC')}",
        "",
        "Funny quotes and laughter moments with episode number, title, and timestamp.",
        "Open `scan-list.csv` in Excel/Sheets to sort and filter.",
        "",
    ]
    all_rows = collect_scan_entries_from_episodes(episodes)
    funny_n = sum(1 for r in all_rows if r["type"] == "FUNNY")
    laugh_n = sum(1 for r in all_rows if r["type"] == "LAUGHTER")
    lines.extend(
        [
            f"**Episodes:** {', '.join(str(p.get('episodeNumber', 0)) for p in episodes)}",
            f"**Entries:** {len(all_rows)} ({funny_n} funny, {laugh_n} laughter)",
            "",
            "## Quick jump",
            "",
        ]
    )
    for payload in episodes:
        ep_num = payload.get("episodeNumber", 0)
        title = payload.get("title") or f"Episode {ep_num}"
        lines.append(f"- [Ep {ep_num} — {title}](#ep-{ep_num})")
    lines.append("")

    current_ep = None
    for row in all_rows:
        if row["episode"] != current_ep:
            current_ep = row["episode"]
            lines.extend(["", f"## Ep {current_ep} — {row['title']}", f"<a id=\"ep-{current_ep}\"></a>", ""])
        lines.append(f"- **[{row['timestamp']}] {row['type']}** — {row['quote']}")
    lines.append("")
    return "\n".join(lines)


def collect_scan_entries_from_episodes(episodes: list[dict]) -> list[dict]:
    rows: list[dict] = []
    for payload in episodes:
        rows.extend(collect_scan_entries(payload))
    return rows


def write_scan_list_csv(rows: list[dict], path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(
            fh,
            fieldnames=["episode", "title", "timestamp", "seconds", "type", "quote"],
        )
        writer.writeheader()
        writer.writerows(rows)


def add_range_args(parser: argparse.ArgumentParser) -> None:
    add_episode_selection_args(parser)


def resolve_export_episodes(args) -> list[int] | None:
    nums = resolve_cli_episode_numbers(args)
    if nums is None:
        print("Error: use only one of --episode, --last, or --from/--to.", file=sys.stderr)
    return nums


def main() -> int:
    parser = argparse.ArgumentParser(description="Export transcript JSON to Markdown.")
    add_range_args(parser)
    args = parser.parse_args()

    episode_nums = resolve_export_episodes(args)
    if episode_nums is None:
        return 1

    if not episode_nums:
        print("No transcript JSON files found.", file=sys.stderr)
        return 1

    FULL_TRANSCRIPTS_DIR.mkdir(parents=True, exist_ok=True)
    payloads = []
    ok = 0
    for ep_num in episode_nums:
        path = full_transcript_json_path(ep_num)
        if not path.exists():
            print(f"  ep {ep_num:02d}: skip (no JSON)")
            continue
        payload = load_transcript_json(ep_num)
        payloads.append(payload)
        md = render_episode_markdown(payload)
        full_transcript_md_path(ep_num).write_text(md, encoding="utf-8")
        full_transcript_quotes_path(ep_num).write_text(render_quotes_only(payload), encoding="utf-8")
        print(f"  ep {ep_num:02d}: wrote .md + .quotes-only.md")
        ok += 1

    payloads.sort(key=lambda p: p.get("episodeNumber", 0))
    FUNNY_INDEX_PATH.parent.mkdir(parents=True, exist_ok=True)
    FUNNY_INDEX_PATH.write_text(build_funny_index(payloads), encoding="utf-8")
    print(f"Wrote {FUNNY_INDEX_PATH}")

    scan_rows = collect_scan_entries_from_episodes(payloads)
    SCAN_LIST_MD_PATH.write_text(build_scan_list_markdown(payloads), encoding="utf-8")
    write_scan_list_csv(scan_rows, SCAN_LIST_CSV_PATH)
    print(f"Wrote {SCAN_LIST_MD_PATH}")
    print(f"Wrote {SCAN_LIST_CSV_PATH} ({len(scan_rows)} entries)")

    print(f"Done: {ok}/{len(episode_nums)} exported")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
