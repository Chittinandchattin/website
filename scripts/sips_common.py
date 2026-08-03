#!/usr/bin/env python3
"""Shared helpers for the Sips of the Week pipeline."""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EPISODES_PATH = ROOT / "assets" / "data" / "episodes.json"
SIPS_PATH = ROOT / "assets" / "data" / "sips.json"
OVERRIDES_PATH = ROOT / "assets" / "data" / "sips-overrides.json"
CHECKLIST_PATH = ROOT / "assets" / "data" / "sips-checklist.csv"
PLAINTEXT_PATH = ROOT / "assets" / "data" / "sips.txt"
OPENINGS_DIR = ROOT / "audio" / "openings"
TRANSCRIPTS_DIR = ROOT / "transcripts" / "openings"
CONTENT_DIR = ROOT / "content"

OPENING_SECONDS = 600  # 10 minutes

SIP_LABEL_RE = re.compile(
    r"[Ss]ips? of the [Ww]eek(?:\s+(?:is|was|were|are))?\s+",
    re.IGNORECASE,
)
ALT_OPENING_PATTERNS = [
    re.compile(
        r"(?:this episode is )?powered by\s+(.{10,200}?)(?:\.|,|\s+(?:paired|while|we))",
        re.IGNORECASE,
    ),
    re.compile(
        r"start out strong with\s+(.{10,200}?)(?:\.|,|\s+(?:served|while|we))",
        re.IGNORECASE,
    ),
    re.compile(
        r"(?:our )?sips of the week were\s+(.{10,200}?)(?:\.|,|\s+(?:in the|while|we))",
        re.IGNORECASE,
    ),
    re.compile(
        r"(?:our )?sips of the week was\s+(.{10,200}?)(?:\.|,|\s+(?:in the|while|we))",
        re.IGNORECASE,
    ),
    re.compile(
        r"treat of the week[!?.]?\s*(.{10,200}?)(?:\.|,|\s+(?:we paired|the bulk))",
        re.IGNORECASE,
    ),
    re.compile(
        r"enjoy our [Ss]ips? of the [Ww]eek\s*,?\s*(.{10,120}?)(?:\.|,|\s+in this)",
        re.IGNORECASE,
    ),
    re.compile(
        r"(?:we.?re back with (?:our )?(?:second )?)?[Ss]ips? of the [Ww]eek\s*,?\s*(?:featuring\s+)?(.{10,200}?)(?:\.|,|\s+(?:we also|on top))",
        re.IGNORECASE,
    ),
]

HOST_DRINK_RE = re.compile(
    r"(?:Syd(?:ney)?|M)\s+(?:is|was)\s+(?:sipping on|enjoying|drinking)\s+(?:a|an|the)?\s*([^.,]+)",
    re.IGNORECASE,
)
PAIRED_FOOD_RE = re.compile(
    r"(?:paired (?:with|perfectly with)|served with|along with)\s+(.{5,120}?)(?:\.|,|\s+(?:while|we|in the|as we))",
    re.IGNORECASE,
)
VESSEL_RE = re.compile(
    r"(?:served in|sipping from|from the)\s+(?:the\s+)?(.{5,80}?)(?:\.|,|\s+(?:which|while|and))",
    re.IGNORECASE,
)
INGREDIENT_HINTS = re.compile(
    r"\b(?:tea|coffee|vodka|bourbon|margarita|latte|soda|cream|syrup|honey|"
    r"ice cream|ros[eé]|wine|dr pepper|refresher|milkshake|float|Bloom|"
    r"French vanilla|cinnamon|blueberry|mango|peach|egg nog|eggnog|"
    r"sarsaparilla|sparkling|espresso|matcha|chai|rum|tequila|whiskey|"
    r"caramel|chocolate|lemon|lime|mint|ginger|oat milk|almond milk)\b",
    re.IGNORECASE,
)


def load_episodes() -> list[dict]:
    data = json.loads(EPISODES_PATH.read_text(encoding="utf-8"))
    return data["episodes"]


def episodes_chronological(episodes: list[dict]) -> list[dict]:
    """Oldest first by published date."""
    from email.utils import parsedate_to_datetime

    def sort_key(ep: dict) -> tuple:
        pub = ep.get("published", "")
        try:
            return (parsedate_to_datetime(pub), ep.get("title", ""))
        except (TypeError, ValueError, IndexError):
            return (0, ep.get("title", ""))

    return sorted(episodes, key=sort_key)


def episodes_with_numbers(episodes: list[dict] | None = None) -> list[dict]:
    """Return chronological episodes each with episodeNumber 1..N."""
    if episodes is None:
        episodes = load_episodes()
    ordered = episodes_chronological(episodes)
    result = []
    for index, ep in enumerate(ordered, start=1):
        copy = dict(ep)
        copy["episodeNumber"] = index
        if ep.get("episodeNumber") is not None:
            copy["rssEpisodeNumber"] = ep["episodeNumber"]
        result.append(copy)
    return result


def episode_slug(episode_number: int) -> str:
    return f"ep-{episode_number:02d}"


def opening_audio_path(episode_number: int) -> Path:
    return OPENINGS_DIR / f"{episode_slug(episode_number)}.mp3"


def transcript_path(episode_number: int) -> Path:
    return TRANSCRIPTS_DIR / f"{episode_slug(episode_number)}.txt"


def relative_transcript_path(episode_number: int) -> str:
    return f"transcripts/openings/{episode_slug(episode_number)}.txt"


def clean_fragment(text: str) -> str:
    text = (text or "").replace("\u2014", "-").replace("\u2013", "-")
    text = re.sub(r"\s+", " ", text).strip(" .,--")
    text = re.sub(r"\s+,\s+", ", ", text)
    return text


def extract_sip_from_description(description: str) -> dict:
    """Best-effort parse of sip details from RSS show notes."""
    result = {
        "name": "",
        "hosts": [],
        "ingredients": [],
        "method": "",
        "notes": "",
        "pairedFood": "",
        "vessel": "",
        "sourceExcerpt": "",
    }
    if not description:
        return result

    excerpt = ""
    name = ""

    label_match = SIP_LABEL_RE.search(description)
    if label_match:
        start = label_match.end()
        rest = description[start : start + 280]
        stop = re.search(
            r"\.\s+(?:We |Syd|M |In |On |From |Oh |Also |Happy |The bulk|Grab |Listen |Cue |Naturally |She |He |This week)",
            rest,
        )
        fragment = rest[: stop.start() + 1] if stop else rest.split(".")[0]
        excerpt = description[max(0, label_match.start() - 10) : start + len(fragment)]
        name = clean_fragment(fragment)
    else:
        for pattern in ALT_OPENING_PATTERNS:
            match = pattern.search(description)
            if match:
                name = clean_fragment(match.group(1))
                excerpt = match.group(0)[:240]
                break

    if not name and description:
        first_sentence = description.split(".")[0][:200]
        if re.search(r"\b(tea|coffee|margarita|latte|drink|sip|milkshake|float|soda)\b", first_sentence, re.I):
            name = clean_fragment(first_sentence)
            excerpt = first_sentence

    result["name"] = name
    result["sourceExcerpt"] = clean_fragment(excerpt)[:300]

    for match in HOST_DRINK_RE.finditer(description):
        host = "Syd" if match.group(0).lower().startswith("syd") else "M"
        drink = clean_fragment(match.group(1))
        if drink:
            result["hosts"].append({"host": host, "drink": drink})

    paired = PAIRED_FOOD_RE.search(description)
    if paired:
        result["pairedFood"] = clean_fragment(paired.group(1))

    vessel = VESSEL_RE.search(description)
    if vessel:
        result["vessel"] = clean_fragment(vessel.group(1))

    ingredients = set()
    for token in INGREDIENT_HINTS.findall(name or description[:400]):
        ingredients.add(token.strip().lower())
    result["ingredients"] = sorted(ingredients)

    if re.search(r"\b(recipe|homemade|whipped up|brewed|steeped|mixed|infused|handcrafted)\b", description[:500], re.I):
        method_bits = []
        for pat in [
            r"homemade ([^.,]{5,80})",
            r"whipped up (?:a|an|some)?\s*([^.,]{5,80})",
            r"infused with ([^.,]{5,80})",
            r"mixed with ([^.,]{5,80})",
            r"added some ([^.,]{5,80})",
            r"turned them into ([^.,]{5,80})",
        ]:
            m = re.search(pat, description[:600], re.I)
            if m:
                method_bits.append(clean_fragment(m.group(0)))
        if method_bits:
            result["method"] = "; ".join(method_bits[:3])

    return result


def extract_sip_from_transcript(text: str) -> dict:
    """Parse opening transcript for sip segment details."""
    result = {
        "name": "",
        "hosts": [],
        "ingredients": [],
        "method": "",
        "notes": "",
        "pairedFood": "",
        "vessel": "",
        "sourceExcerpt": "",
    }
    if not text:
        return result

    opening = text[:4000]
    sip_match = re.search(
        r"(?:sips?|tips) of the week.{0,800}",
        opening,
        re.IGNORECASE | re.DOTALL,
    )
    segment = sip_match.group(0) if sip_match else opening[:1500]
    result["sourceExcerpt"] = clean_fragment(segment)[:400]

    if sip_match:
        after = sip_match.group(0)
        for pattern in (
            r"(?:sips?|tips) of the week is\s+([^.,\n]{3,80})",
            r"(?:is|was|were|are)\s+(?:a|an|the|our)?\s*([^.\n]{5,120})",
        ):
            name_match = re.search(pattern, after, re.IGNORECASE)
            if name_match:
                result["name"] = clean_fragment(name_match.group(1))
                break

    # Loose-leaf / spoken ingredient lists
    tea_desc = re.search(
        r"(?:black tea|green tea|herbal tea|loose leaf|loose-leaf)[^.]{0,200}\.",
        segment,
        re.IGNORECASE,
    )
    if tea_desc and not result["name"]:
        result["name"] = clean_fragment(tea_desc.group(0))
    elif tea_desc and len(tea_desc.group(0)) > len(result.get("name", "")):
        result["notes"] = clean_fragment(tea_desc.group(0))

    for match in re.finditer(
        r"(?:with|contains?|has)\s+([^.\n]{10,160})",
        segment,
        re.IGNORECASE,
    ):
        fragment = match.group(1)
        if re.search(r"\b(tea|coffee|spice|cream|syrup|vodka|mango|peach|cinnamon)\b", fragment, re.I):
            parts = re.split(r",|\band\b", fragment)
            for part in parts:
                part = clean_fragment(part)
                if part and len(part) > 2:
                    result["ingredients"].append(part.lower())

    for match in HOST_DRINK_RE.finditer(opening):
        host = "Syd" if match.group(0).lower().startswith("syd") else "M"
        drink = clean_fragment(match.group(1))
        if drink:
            result["hosts"].append({"host": host, "drink": drink})

    paired = PAIRED_FOOD_RE.search(opening)
    if paired:
        result["pairedFood"] = clean_fragment(paired.group(1))

    vessel = VESSEL_RE.search(opening)
    if vessel:
        result["vessel"] = clean_fragment(vessel.group(1))

    ingredients = set(result.get("ingredients") or [])
    for token in INGREDIENT_HINTS.findall(segment):
        ingredients.add(token.strip().lower())
    result["ingredients"] = sorted(ingredients)

    method_bits = []
    for pat in [
        r"(?:we |I |M |Syd(?:ney)? )(?:mixed|added|brewed|steeped|made|whipped up|poured)[^.]{5,120}\.",
        r"(?:you (?:just|can|need to)|(?:just|simply)) [^.]{10,120}\.",
    ]:
        for m in re.finditer(pat, segment, re.IGNORECASE):
            method_bits.append(clean_fragment(m.group(0)))
    if method_bits:
        result["method"] = " ".join(method_bits[:2])

    return result


def extract_rss_sip_paragraph(description: str) -> dict:
    """Extract polished displayName and description from RSS show notes."""
    result = {"displayName": "", "description": ""}
    if not description:
        return result

    sip_data = extract_sip_from_description(description)
    paragraph = ""
    label_match = SIP_LABEL_RE.search(description)
    if label_match:
        start = label_match.start()
        rest = description[start:]
        stop = re.search(
            r"\.\s+(?:We |Syd|M |In |On |From |Oh |Also |Happy |The bulk|Grab |Listen |Cue |Naturally |She |He |This week|Hi friends|Hey |Welcome|Our brains|Somewhere|And of course|To wrap|Before we|Meanwhile|This episode|We also|We chat|We get|We dive|We kick|We wasted|We celebrate|We didn't|20 episodes|Happy Episode|Happy Pride|Sips of the Week ☕)",
            rest,
            re.IGNORECASE,
        )
        paragraph = rest[: stop.start() + 1] if stop else rest.split(".")[0] + "."
    else:
        for pattern in ALT_OPENING_PATTERNS:
            match = pattern.search(description)
            if match:
                paragraph = match.group(0)
                if not paragraph.endswith("."):
                    paragraph = paragraph.split(".")[0] + "."
                break
        if not paragraph:
            powered = re.search(
                r"This episode is powered by[^.]+\.",
                description,
                re.IGNORECASE,
            )
            if powered:
                paragraph = powered.group(0)
            else:
                strong = re.search(
                    r"start out strong with[^.]+\.",
                    description,
                    re.IGNORECASE,
                )
                if strong:
                    paragraph = strong.group(0)

    paragraph = clean_fragment(paragraph)
    result["description"] = paragraph

    name = sip_data.get("name", "")
    if name and len(name) <= 80 and not _looks_like_garbage(name):
        result["displayName"] = _short_display_name(name)
    elif paragraph:
        result["displayName"] = _short_display_name(paragraph)

    return result


def _looks_like_garbage(text: str) -> bool:
    """Heuristic: transcript fragments and mid-sentence grabs."""
    lower = text.lower()
    bad_starts = (
        "week and ",
        "watching, ",
        "room is ",
        "a boy",
        "super cute",
        "really good",
        "new mug",
        "tea maker and",
        "where m makes",
        "featuring sydney whipping",
    )
    if any(lower.startswith(s) for s in bad_starts):
        return True
    if len(text) > 100:
        return True
    return False


def _short_display_name(text: str) -> str:
    """Derive a short title from a sip phrase."""
    text = clean_fragment(text)
    text = re.sub(r"^(?:this week'?s? |our )?[Ss]ips? of the [Ww]eek(?:\s+(?:is|was|were|are))?\s*", "", text, flags=re.I)
    text = re.sub(r"^(?:enjoy our )?[Ss]ips? of the [Ww]eek\s*,?\s*", "", text, flags=re.I)
    text = re.sub(r"^featuring\s+", "", text, flags=re.I)
    text = re.sub(r"^a (?:chaotic \(but delicious\) mix-|beautiful and cozy recipe from )", "", text, flags=re.I)
    # First sentence or clause
    short = text.split(".")[0].split("-")[0].split(", and ")[0].strip()
    if len(short) > 70:
        short = short[:67].rsplit(" ", 1)[0] + "…"
    return short


def merge_display_fields(rss_para: dict, transcript: dict, override: dict, merged: dict) -> dict:
    """Build displayName and description; override > RSS > transcript."""
    display = {"displayName": "", "description": ""}

    if override.get("displayName"):
        display["displayName"] = override["displayName"]
    elif rss_para.get("displayName"):
        display["displayName"] = rss_para["displayName"]
    elif merged.get("name") and not _looks_like_garbage(merged["name"]):
        display["displayName"] = _short_display_name(merged["name"])

    if override.get("description"):
        display["description"] = override["description"]
    elif rss_para.get("description"):
        display["description"] = rss_para["description"]
    elif merged.get("notes"):
        display["description"] = merged["notes"]
    elif merged.get("sourceExcerpt") and len(merged["sourceExcerpt"]) < 300:
        display["description"] = merged["sourceExcerpt"]

    if override.get("descriptionHtml"):
        display["descriptionHtml"] = override["descriptionHtml"]

    return display


def merge_sip_fields(rss: dict, transcript: dict, override: dict) -> dict:
    """Merge layers; override wins; RSS preferred over transcript for name."""
    merged = {
        "name": "",
        "hosts": [],
        "ingredients": [],
        "method": "",
        "notes": "",
        "pairedFood": "",
        "vessel": "",
        "sourceExcerpt": "",
        "manualNotes": "",
    }

    # name: override > rss (if clean) > transcript
    if override.get("name"):
        merged["name"] = override["name"]
    elif rss.get("name") and not _looks_like_garbage(rss["name"]):
        merged["name"] = rss["name"]
    elif transcript.get("name") and not _looks_like_garbage(transcript["name"]):
        merged["name"] = transcript["name"]
    elif rss.get("name"):
        merged["name"] = rss["name"]
    elif transcript.get("name"):
        merged["name"] = transcript["name"]

    for key in ("method", "notes", "pairedFood", "vessel", "manualNotes"):
        for layer in (override, rss, transcript):
            val = layer.get(key)
            if val:
                merged[key] = val
                break

    if override.get("sourceExcerpt"):
        merged["sourceExcerpt"] = override["sourceExcerpt"]
    elif rss.get("sourceExcerpt"):
        merged["sourceExcerpt"] = rss["sourceExcerpt"]
    elif transcript.get("sourceExcerpt"):
        merged["sourceExcerpt"] = transcript["sourceExcerpt"]

    # hosts: prefer override, else merge unique from transcript then rss
    if override.get("hosts"):
        merged["hosts"] = override["hosts"]
    else:
        seen = set()
        hosts = []
        for layer in (transcript, rss):
            for item in layer.get("hosts") or []:
                key = (item.get("host"), item.get("drink"))
                if key not in seen:
                    seen.add(key)
                    hosts.append(item)
        merged["hosts"] = hosts

    # ingredients: union
    if override.get("ingredients"):
        merged["ingredients"] = override["ingredients"]
    else:
        ingredients = set(rss.get("ingredients") or [])
        ingredients.update(transcript.get("ingredients") or [])
        merged["ingredients"] = sorted(ingredients)

    return merged


def assess_completeness(sip: dict) -> tuple[str, bool]:
    name = (sip.get("displayName") or sip.get("name") or "").strip()
    description = (sip.get("description") or "").strip()
    ingredients = sip.get("ingredients") or []
    method = (sip.get("method") or "").strip()
    manual = (sip.get("manualNotes") or "").strip()

    if manual and name:
        return "full", False
    if name and description and (ingredients or method):
        return "full", False
    if name and description:
        return "full", False
    if name and len(name) > 3:
        return "partial", not bool(description)
    if name:
        return "partial", True
    return "blank", True


def load_content_recipes(episodes: list[dict] | None = None) -> dict[int, dict]:
    """Map chronological episode numbers to extra recipe content from content/ folder."""
    if episodes is None:
        episodes = episodes_with_numbers()

    rss_to_chrono = {}
    for ep in episodes:
        rss_num = ep.get("rssEpisodeNumber")
        if rss_num is not None:
            rss_to_chrono[rss_num] = ep["episodeNumber"]

    recipes: dict[int, dict] = {}
    ep29 = CONTENT_DIR / "episode 29.txt"
    root_ep29 = ROOT / "episode 29.txt"
    for path in (ep29, root_ep29):
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        recipe_match = re.search(r"Recipe:\s*(.+)", text, re.DOTALL | re.IGNORECASE)
        if not recipe_match:
            break
        body = recipe_match.group(1).strip()
        chrono = rss_to_chrono.get(29)
        if chrono is None:
            for ep in episodes:
                if "Nolan Wells" in ep.get("title", ""):
                    chrono = ep["episodeNumber"]
                    break
        if chrono is not None:
            recipes[chrono] = {
                "pairedFood": "homemade peach crisp",
                "method": body,
                "notes": "From social post recipe note; paired with coffee.",
                "sources_extra": [str(path.relative_to(ROOT)).replace("\\", "/")],
            }
        break
    return recipes
