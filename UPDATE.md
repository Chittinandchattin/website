# How to Add Content and Push Updates

**Repo:** `G:\Laughing Dragons\chittinandchattin.com`  
**Remote:** `https://github.com/laughingdragonsproductions/Chittinandchattin.git`  
**Live (when deployed):** `https://chittinandchattin.com`

Every push to `main` triggers Cloudflare Pages redeploy (usually 1–3 minutes). No build step.

---

## Standard workflow

```powershell
cd "G:\Laughing Dragons\chittinandchattin.com"
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
| Suggest a Sip inbox | `suggestasip/index.html`, `assets/js/config.js` → `web3forms.sip` |
| AdSense slot IDs | `assets/js/config.js` → `adsense.slots` |
| New page | Create `section/index.html`, add to `NAV` in `site.js`, add to `sitemap.xml` |
| Refresh episode list | `python scripts/pull-episodes.py` then push (or use GitHub Actions — see below) |
| Brand images | `assets/brand/` |
| Feature art | `assets/features/` |

Reference copy (not served directly): `content/` folder.

---

## Automatic episode refresh (Mondays)

New episodes usually drop on **Thursday**, but sometimes land **Friday or Saturday**. A GitHub Actions workflow runs every **Monday at ~7am Eastern**, pulls the Anchor/Spotify RSS feed, refreshes **`assets/data/episodes.json`** and the **Sips of the Week** archive (`sips.json`, `sips.txt`, `sips-checklist.csv`), and pushes to `main` only when something changed. Cloudflare Pages redeploys automatically.

**Manual refresh:** GitHub repo → **Actions** → **Refresh episodes and sips from RSS** → **Run workflow**

**Local refresh** (same as the workflow):

```powershell
python scripts/pull-episodes.py
.\scripts\push-update.ps1 "Refresh episodes from RSS"
```

---

### Episodes from Spotify (via RSS)

Episodes and sips auto-refresh every Monday via `.github/workflows/refresh-episodes.yml`. Manual refresh:

```powershell
python scripts/pull-episodes.py
.\scripts\push-update.ps1 "Refresh episodes from RSS"
```

Data lands in `assets/data/episodes.json` and powers `/episodes/`.

**Episode thumbnails:** The Anchor RSS feed only includes **show-level** artwork (the studio/ring-light photo), not unique art per episode. On `/episodes/`, when an episode image matches that shared show art, the site shows the podcast icon from `assets/brand/icon.png` instead of repeating the same recording setup photo on every card. If you later upload unique cover art per episode in Spotify for Creators, those distinct URLs will display automatically.

### Sips of the Week archive

Live at **`/sips/`** — reads from `assets/data/sips.json`. Build and refresh the sip log from RSS show notes, optional opening transcripts, and hand edits.

**Data files (committed):**
- `assets/data/sips.json` — one row per episode
- `assets/data/sips.txt` — plain-text copy-paste list
- `assets/data/sips-checklist.csv` — spreadsheet for manual fill-in
- `assets/data/sips-overrides.json` — your edits (merged on re-run)

**Local only (gitignored):** `audio/episodes/` (full MP3s), `audio/openings/`, `transcripts/` (openings + full episode JSON/MD)

**Prerequisites:** Python 3, `ffmpeg` on PATH, `pip install openai-whisper` (or `faster-whisper`)

```powershell
python scripts/pull-episodes.py
python scripts/download-episodes.py   # full RSS MP3s → audio/episodes/
python scripts/download-openings.py      # downloads RSS MP3s, trims first 10 min
python scripts/transcribe-openings.py    # local Whisper → transcripts/openings/
python scripts/extract-sips.py           # merges RSS + transcripts + overrides → sips.json
git add assets/data/
.\scripts\push-update.ps1 "Refresh episodes and sips"
```

Single episode: `--episode 3` on download/transcribe scripts. Re-transcribe: `--force`.

Hand-fill gaps in `sips-overrides.json` (keyed by `episodeNumber`), then re-run `extract-sips.py`. Episodes flagged `needsListen` show a review banner on `/sips/`.

**Cleaning bad auto-extracts:** Opening transcripts sometimes produce nonsense in `method`, `vessel`, or `pairedFood` (speech-to-text fragments). To fix an episode, set the field in `sips-overrides.json` — use a real value, or `""` to clear transcript garbage. Re-run `extract-sips.py`. The merge script skips known garbage patterns; the site also hides obvious junk on `/sips/` as a backup.

---

## Full-episode transcripts (local, funny + laughter markers)

Transcribe all downloaded full MP3s, mark `[LAUGHTER]` and `>> FUNNY:` lines for quote mining. Output stays gitignored under `transcripts/episodes/`.

**Prerequisites:** NVIDIA GPU recommended, `ffmpeg` on PATH, [Ollama](https://ollama.com/) running for funny flags.

System Python on Windows often ships CPU-only PyTorch. Use the project venv with CUDA wheels:

```powershell
python -m venv .venv-transcribe
.\.venv-transcribe\Scripts\pip install torch torchvision --index-url https://download.pytorch.org/whl/cu126
.\.venv-transcribe\Scripts\pip install -r scripts/requirements-transcripts.txt
ollama pull qwen2.5:7b
```

Verify GPU before a long run:

```powershell
.\.venv-transcribe\Scripts\python.exe -c "import torch; print(torch.cuda.is_available(), torch.cuda.device_count())"
```

**Pipeline** (use venv Python):

```powershell
.\.venv-transcribe\Scripts\python.exe scripts/download-episodes.py       # if not already done
.\.venv-transcribe\Scripts\python.exe scripts/transcribe-episodes.py --device cuda
.\.venv-transcribe\Scripts\python.exe scripts/annotate-transcripts.py --ollama-model qwen2.5:7b
.\.venv-transcribe\Scripts\python.exe scripts/export-transcripts.py
```

**Last N episodes** (e.g. newest 10 for funny-moment mining — no new downloads needed if MP3s are already in `audio/episodes/`):

```powershell
.\.venv-transcribe\Scripts\python.exe scripts/transcribe-episodes.py --device cuda --parallel-gpus --last 10
.\.venv-transcribe\Scripts\python.exe scripts/annotate-transcripts.py --last 10 --ollama-model qwen2.5:7b
.\.venv-transcribe\Scripts\python.exe scripts/export-transcripts.py --last 10
```

Review `transcripts/episodes/ep-32.md`, `transcripts/funny-index.md`, and `.quotes-only.md` files under `transcripts/episodes/`.

**Scan list** (easy browsing / spreadsheet filter):

```powershell
.\.venv-transcribe\Scripts\python.exe scripts/export-transcripts.py --from 23 --to 32
```

Outputs:
- `transcripts/scan-list.md` — grouped by episode with timestamp, type (FUNNY/LAUGHTER), and quote
- `transcripts/scan-list.csv` — same data for Excel/Sheets (sort by episode, filter LAUGHTER only, etc.)

**Outputs (local):**
- `transcripts/episodes/ep-XX.json` — segments with timestamps, laughter, funny flags
- `transcripts/episodes/ep-XX.md` — readable transcript with `[LAUGHTER]` and `>> FUNNY:`
- `transcripts/episodes/ep-XX.quotes-only.md` — funny lines only
- `transcripts/funny-index.md` — all flagged quotes across episodes

**Options:** `--episode 5` or `--last 10` on transcribe / annotate / export; `--force` on transcribe; `--skip-funny` on annotate if Ollama is unavailable; `--model medium` on transcribe for better accuracy (slower).

**Suggested first run:** `transcribe-episodes.py --episode 24` then annotate + export, review `ep-24.md`, then batch overnight for all 32.

---

## Do not commit

- `SpillitBestie2_files/` (saved-page junk)
- Root-level duplicate images (use `assets/` copies only)
