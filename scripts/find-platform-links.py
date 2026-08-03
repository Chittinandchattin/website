#!/usr/bin/env python3
"""Find podcast platform links for Chittin' and Chattin."""

import re
import urllib.request

FEED = "https://anchor.fm/s/10d11a464/podcast/rss"


def fetch(url: str) -> tuple[str | None, str]:
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=20) as r:
            return r.read().decode("utf-8", errors="replace"), str(r.url)
    except Exception as exc:
        return None, str(exc)


def main() -> None:
    tests = [
        "https://music.amazon.com/search/Chittin+and+Chattin+podcast",
        "https://www.iheart.com/search/?q=Chittin%20and%20Chattin",
        "https://player.fm/series/chittin-and-chattin",
        "https://www.castbox.fm/search?keyword=Chittin%20and%20Chattin",
        "https://podcastaddict.com/?q=Chittin%20and%20Chattin",
        "https://www.deezer.com/search/Chittin%20and%20Chattin/podcast",
        "https://pocketcasts.com/search?q=Chittin%20and%20Chattin",
    ]
    for url in tests:
        body, final = fetch(url)
        print(f"\n=== {url} ===")
        if not body:
            print("FAIL", final)
            continue
        print("final:", final[:100])
        hits = re.findall(r'https?://[^"\s<>]+chittin[^"\s<>]*', body, re.I)
        for h in sorted(set(hits))[:8]:
            print(" ", h[:120])

    ln_url = "https://www.listennotes.com/podcasts/chittin-and-chattin/let-the-lizards-get-him-SqHPMKmCtvi/"
    body, _ = fetch(ln_url)
    if body:
        print("\n=== Listen Notes episode links ===")
        for pat in [
            r"https://music\.amazon\.com/podcasts/[a-f0-9-]+/[^\"'\s<>]+",
            r"https://open\.spotify\.com/show/[A-Za-z0-9]+",
            r"https://podcasts\.apple\.com/[^\"'\s<>]+",
        ]:
            for m in sorted(set(re.findall(pat, body))):
                print(" ", m)


if __name__ == "__main__":
    main()
