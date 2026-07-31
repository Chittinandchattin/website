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

Mine episode descriptions for weekly drinks → `sips.json` → replace `/sips/` coming-soon stub with a full listing. Fill gaps from Instagram/TikTok if needed.

Suggested script workflow (future):

```powershell
# Example — implement when ready
python scripts/pull-spotify-episodes.py
python scripts/extract-sips.py
git add assets/data/
.\scripts\push-update.ps1 "Refresh episodes and sips"
```

---

## Do not commit

- `SpillitBestie2_files/` (saved-page junk)
- Root-level duplicate images (use `assets/` copies only)
