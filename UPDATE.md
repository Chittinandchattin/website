# How to Add Content and Push Updates

**Repo:** `G:\Laughing Dragons\Chittinnchattin.com`  
**Remote:** `https://github.com/laughingdragonsproductions/Chittinandchattin.git`  
**Live (when deployed):** `https://chittinnchattin.com`

Every push to `main` triggers Cloudflare Pages redeploy (usually 1–3 minutes). No build step.

---

## Standard workflow

```powershell
cd "G:\Laughing Dragons\Chittinnchattin.com"
.\scripts\preview.ps1          # http://localhost:8080
.\scripts\push-update.ps1 "Your commit message"
```

---

## Where to edit

| What | File(s) |
|------|---------|
| Show name, bio, social URLs | `assets/js/config.js` |
| Nav labels / layout helpers | `assets/js/site.js` |
| Colors, fonts, layout | `assets/css/site.css` |
| Home hero + teasers | `index.html` |
| Listen platforms | `assets/js/config.js` → `links` |
| Host TikToks | `assets/js/config.js` → `hosts` |
| Spill it / Healing copy | `spill-it-bestie/index.html`, `healing-inbox/index.html` |
| AdSense slot IDs | `assets/js/config.js` → `adsense.slots` |
| New page | Create `section/index.html`, add to `NAV` in `site.js`, add to `sitemap.xml` |
| Refresh episode list | `python scripts/pull-episodes.py` then push (or use GitHub Actions — see below) |
| Brand images | `assets/brand/` |
| Feature art | `assets/features/` |

Reference copy (not served directly): `content/` folder.

---

## Automatic episode refresh (Fridays)

New episodes usually drop on **Thursday**. A GitHub Actions workflow runs every **Friday at ~11am Eastern**, pulls the Anchor/Spotify RSS feed, and pushes to `main` only when `assets/data/episodes.json` changed. Cloudflare Pages redeploys automatically.

**Manual refresh:** GitHub repo → **Actions** → **Refresh episodes from RSS** → **Run workflow**

**Local refresh** (same as the workflow):

```powershell
python scripts/pull-episodes.py
.\scripts\push-update.ps1 "Refresh episodes from RSS"
```

---

## Phase 2 — not built yet

### On-site inbox → bot → Telegram

Replace Instagram CTAs on `/spill-it-bestie/` and `/healing-inbox/` with an on-site message form that posts to a bot and notifies via Telegram. Tag submissions as Spill it vs Healing.

### Episodes from Spotify (via RSS)

Episodes auto-refresh every Friday via `.github/workflows/refresh-episodes.yml`. Manual refresh:

```powershell
python scripts/pull-episodes.py
.\scripts\push-update.ps1 "Refresh episodes from RSS"
```

Data lands in `assets/data/episodes.json` and powers `/episodes/`.

### Sips of the Week archive

Live at **`/sips/`** — reads from `assets/data/sips.json`. Build and refresh the sip log from RSS show notes, optional opening transcripts, and hand edits.

**Data files (committed):**
- `assets/data/sips.json` — one row per episode
- `assets/data/sips.txt` — plain-text copy-paste list
- `assets/data/sips-checklist.csv` — spreadsheet for manual fill-in
- `assets/data/sips-overrides.json` — your edits (merged on re-run)

**Local only (gitignored):** `audio/openings/`, `transcripts/openings/`

**Prerequisites:** Python 3, `ffmpeg` on PATH, `pip install openai-whisper` (or `faster-whisper`)

```powershell
python scripts/pull-episodes.py
python scripts/download-openings.py      # downloads RSS MP3s, trims first 10 min
python scripts/transcribe-openings.py    # local Whisper → transcripts/openings/
python scripts/extract-sips.py           # merges RSS + transcripts + overrides → sips.json
git add assets/data/
.\scripts\push-update.ps1 "Refresh episodes and sips"
```

Single episode: `--episode 3` on download/transcribe scripts. Re-transcribe: `--force`.

Hand-fill gaps in `sips-overrides.json` (keyed by `episodeNumber`), then re-run `extract-sips.py`. Episodes flagged `needsListen` show a review banner on `/sips/`.

---

## Do not commit

- `SpillitBestie2_files/` (saved-page junk)
- Root-level duplicate images (use `assets/` copies only)
