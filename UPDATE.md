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
| Brand images | `assets/brand/` |
| Feature art | `assets/features/` |

Reference copy (not served directly): `content/` folder.

---

## Phase 2 — not built yet

### On-site inbox → bot → Telegram

Replace Instagram CTAs on `/spill-it-bestie/` and `/healing-inbox/` with an on-site message form that posts to a bot and notifies via Telegram. Tag submissions as Spill it vs Healing.

### Episodes from Spotify

Pull metadata from Spotify show `5XmmJuVjc7S4j0aElFIeeF` (titles, descriptions, dates, URLs) into static JSON via a script, then build `/episodes/`. RSS works as a fallback data source.

### Sips of the Week archive

Mine episode descriptions for weekly drinks → `sips.json` → replace `/sips/` coming-soon stub with a full listing. Use Drift bar art as hero. Fill gaps from Instagram/TikTok if needed.

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
