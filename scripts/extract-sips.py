#!/usr/bin/env python3
"""Build Sips of the Week archive from RSS, transcripts, content notes, and overrides."""

from __future__ import annotations

import csv
import json
import sys
from datetime import UTC, datetime
from pathlib import Path

from sips_common import (
    CHECKLIST_PATH,
    OVERRIDES_PATH,
    PLAINTEXT_PATH,
    SIPS_PATH,
    assess_completeness,
    episodes_with_numbers,
    extract_rss_sip_paragraph,
    extract_sip_from_description,
    extract_sip_from_transcript,
    load_content_recipes,
    load_episodes,
    merge_display_fields,
    merge_sip_fields,
    relative_transcript_path,
    transcript_path,
)


def load_overrides() -> dict[str, dict]:
    if not OVERRIDES_PATH.exists():
        return {}
    data = json.loads(OVERRIDES_PATH.read_text(encoding="utf-8"))
    overrides = data.get("overrides") if isinstance(data, dict) else data
    if not isinstance(overrides, dict):
        return {}
    return {str(k): v for k, v in overrides.items()}


def build_sip_entry(episode: dict, content_recipes: dict, overrides: dict[str, dict]) -> dict:
    ep_num = episode.get("episodeNumber")
    if ep_num is None:
        ep_num = 0

    rss = extract_sip_from_description(episode.get("description", ""))
    rss_para = extract_rss_sip_paragraph(episode.get("description", ""))

    transcript_data: dict = {}
    tx_path = transcript_path(ep_num)
    transcript_rel = ""
    if tx_path.exists():
        transcript_text = tx_path.read_text(encoding="utf-8")
        transcript_data = extract_sip_from_transcript(transcript_text)
        transcript_rel = relative_transcript_path(ep_num)

    override = overrides.get(str(ep_num), {})
    merged = merge_sip_fields(rss, transcript_data, override)
    display = merge_display_fields(rss_para, transcript_data, override, merged)

    sources = []
    if episode.get("description"):
        sources.append("rss")
    if transcript_rel:
        sources.append("transcript")

    content_extra = content_recipes.get(ep_num)
    if content_extra:
        if content_extra.get("pairedFood"):
            merged["pairedFood"] = content_extra["pairedFood"]
        if content_extra.get("method") and not merged.get("method"):
            merged["method"] = content_extra["method"]
        if content_extra.get("notes"):
            merged["notes"] = content_extra["notes"]
        for src in content_extra.get("sources_extra", []):
            sources.append(src)

    if override:
        sources.append("override")

    sip_for_assess = {**merged, **display}
    completeness, needs_listen = assess_completeness(sip_for_assess)
    if override.get("needsListen") is False:
        needs_listen = False
    elif override.get("needsListen") is True:
        needs_listen = True

    entry = {
        "episodeNumber": ep_num,
        "title": episode.get("title", ""),
        "published": episode.get("published", ""),
        "link": episode.get("link", ""),
        "audioUrl": episode.get("audioUrl", ""),
        "duration": episode.get("duration", ""),
        "displayName": display.get("displayName", ""),
        "description": display.get("description", ""),
        "descriptionHtml": display.get("descriptionHtml", ""),
        "name": merged.get("name", ""),
        "hosts": merged.get("hosts", []),
        "ingredients": merged.get("ingredients", []),
        "method": merged.get("method", ""),
        "notes": merged.get("notes", ""),
        "pairedFood": merged.get("pairedFood", ""),
        "vessel": merged.get("vessel", ""),
        "sourceExcerpt": merged.get("sourceExcerpt", ""),
        "sources": sources,
        "transcriptPath": transcript_rel,
        "completeness": completeness,
        "needsListen": needs_listen,
        "manualNotes": merged.get("manualNotes", ""),
    }
    return entry


def write_checklist(sips: list[dict]) -> None:
    CHECKLIST_PATH.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "episodeNumber",
        "title",
        "displayName",
        "description",
        "name",
        "ingredients",
        "method",
        "pairedFood",
        "vessel",
        "completeness",
        "needsListen",
        "manualNotes",
        "link",
    ]
    with CHECKLIST_PATH.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        for sip in sips:
            writer.writerow(
                {
                    "episodeNumber": sip["episodeNumber"],
                    "title": sip["title"],
                    "displayName": sip.get("displayName", ""),
                    "description": sip.get("description", ""),
                    "name": sip["name"],
                    "ingredients": "; ".join(sip.get("ingredients") or []),
                    "method": sip.get("method", ""),
                    "pairedFood": sip.get("pairedFood", ""),
                    "vessel": sip.get("vessel", ""),
                    "completeness": sip["completeness"],
                    "needsListen": sip["needsListen"],
                    "manualNotes": sip.get("manualNotes", ""),
                    "link": sip.get("link", ""),
                }
            )


def write_plaintext(sips: list[dict], updated: str) -> None:
    PLAINTEXT_PATH.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "CHITTIN' AND CHATTIN' - SIPS OF THE WEEK",
        f"Updated: {updated}",
        f"Episodes: {len(sips)}",
        "",
        "=" * 60,
        "",
    ]
    for sip in sips:
        ep = sip["episodeNumber"]
        lines.append(f"EPISODE {ep}: {sip['title']}")
        lines.append(f"Published: {sip.get('published', '')}")
        lines.append("")
        if sip.get("displayName") or sip.get("name"):
            lines.append(f"Sip: {sip.get('displayName') or sip.get('name')}")
        else:
            lines.append("Sip: (unknown)")
        if sip.get("description"):
            lines.append(f"Description: {sip['description']}")
        hosts = sip.get("hosts") or []
        if hosts:
            for h in hosts:
                lines.append(f"  {h.get('host', '?')}: {h.get('drink', '')}")
        ingredients = sip.get("ingredients") or []
        if ingredients:
            lines.append(f"Ingredients: {', '.join(ingredients)}")
        if sip.get("method"):
            lines.append(f"Method: {sip['method']}")
        if sip.get("pairedFood"):
            lines.append(f"Paired with: {sip['pairedFood']}")
        if sip.get("vessel"):
            lines.append(f"Vessel: {sip['vessel']}")
        if sip.get("notes"):
            lines.append(f"Notes: {sip['notes']}")
        if sip.get("manualNotes"):
            lines.append(f"Manual notes: {sip['manualNotes']}")
        status = sip.get("completeness", "")
        if sip.get("needsListen"):
            lines.append(f"Status: {status} - needs listen")
        elif status:
            lines.append(f"Status: {status}")
        if sip.get("link"):
            lines.append(f"Link: {sip['link']}")
        lines.extend(["", "-" * 60, ""])
    PLAINTEXT_PATH.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def ensure_overrides_template() -> None:
    if OVERRIDES_PATH.exists():
        return
    template = {
        "comment": "Hand-edited sip details keyed by episodeNumber. Re-run extract-sips.py to merge.",
        "overrides": {},
    }
    OVERRIDES_PATH.write_text(json.dumps(template, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main() -> int:
    ensure_overrides_template()
    episodes = episodes_with_numbers(load_episodes())
    content_recipes = load_content_recipes(episodes)
    overrides = load_overrides()

    sips = []
    for episode in episodes:
        ep_num = episode["episodeNumber"]
        sips.append(build_sip_entry(episode, content_recipes, overrides))

    payload = {
        "updated": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "count": len(sips),
        "sips": sips,
    }
    SIPS_PATH.parent.mkdir(parents=True, exist_ok=True)
    SIPS_PATH.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    write_checklist(sips)
    write_plaintext(sips, payload["updated"])

    full = sum(1 for s in sips if s["completeness"] == "full")
    partial = sum(1 for s in sips if s["completeness"] == "partial")
    blank = sum(1 for s in sips if s["completeness"] == "blank")
    needs = sum(1 for s in sips if s["needsListen"])
    with_tx = sum(1 for s in sips if s.get("transcriptPath"))

    print(f"Wrote {len(sips)} sips to {SIPS_PATH}")
    print(f"Wrote checklist to {CHECKLIST_PATH}")
    print(f"Wrote plain text to {PLAINTEXT_PATH}")
    print(f"Coverage: full={full}, partial={partial}, blank={blank}, needsListen={needs}, transcripts={with_tx}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
