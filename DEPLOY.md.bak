# Deploy chittinandchattin.com to Cloudflare Pages

Static site — no build step. Cloudflare serves files from the repo root.

## 1. Push this repo to GitHub

```powershell
cd "G:\Laughing Dragons\chittinandchattin.com"
git init
git add .
git commit -m "Initial Chittin' and Chattin podcast site"
git branch -M main
git remote add origin https://github.com/laughingdragonsproductions/Chittinandchattin.git
git push -u origin main
```

## 2. Create Cloudflare Pages project

1. Log in at [dash.cloudflare.com](https://dash.cloudflare.com)
2. **Workers & Pages** → **Create** → **Pages** → **Connect to Git**
3. Select the repository
4. Build settings:
   - **Framework preset:** None
   - **Build command:** (leave empty)
   - **Build output directory:** `/`
5. Deploy

Preview URL: `https://chittinnchattin-site.pages.dev` (name may vary).

## 3. Custom domains

**Canonical:** `chittinandchattin.com` + `www.chittinandchattin.com`

1. Pages project → **Custom domains** → add both
2. If domains are on Cloudflare, DNS is automatic

**Alias redirect:** `chittinandchattin.com` + `www.chittinandchattin.com`

Add both to the same Pages project, then create a **Redirect Rule** (or Bulk Redirect):

| Match | Redirect to |
|-------|-------------|
| `chittinandchattin.com/*` | `https://chittinandchattin.com/$1` (301) |
| `www.chittinandchattin.com/*` | `https://chittinandchattin.com/$1` (301) |

All canonical URLs in this repo use `https://chittinandchattin.com`.

## 4. AdSense (shared account)

Publisher ID: `ca-pub-7048606415692002`

Every page includes the AdSense script in `<head>`. Root `ads.txt` is set for `pub-7048606415692002`.

After the domain is live:

1. AdSense → **Sites** → **Add site** → `chittinandchattin.com`
2. Verify `https://chittinandchattin.com/ads.txt`
3. Privacy, Terms, About, and Contact are linked in the footer
4. Create ad units and paste slot IDs into `assets/js/config.js` → `adsense.slots`
5. Wait for review (can take days)

You usually do **not** need a separate AdSense property for `chittinandchattin.com` if it 301-redirects to the canonical site.

## 5. Search Console

1. Add property at [Google Search Console](https://search.google.com/search-console)
2. Submit `https://chittinandchattin.com/sitemap.xml`

## 6. Ongoing updates

Use [UPDATE.md](UPDATE.md). Push to `main` — Cloudflare redeploys automatically.

### Scheduled episode sync

Workflow: `.github/workflows/refresh-episodes.yml`

- Runs every **Monday 11:00 UTC** (~7am Eastern) to catch Thursday–Saturday episode drops
- Pulls RSS via `scripts/pull-episodes.py`, then rebuilds sips via `scripts/extract-sips.py`
- Commits only if `episodes.json` or sips data files changed
- Manual run: GitHub → **Actions** → **Refresh episodes and sips from RSS** → **Run workflow**

Ensure **Settings → Actions → General** allows workflows on this repo.

## Troubleshooting

| Issue | Fix |
|-------|-----|
| 404 on `/listen/` | Ensure `listen/index.html` exists |
| ads.txt 404 | File must be at repo root |
| Ads not showing | Site may need AdSense approval; add slot IDs in config.js |
| Wrong domain in canonicals | All pages use `chittinandchattin.com` |

## Free-tier map

Jarvis (`desktop-agent`) runs a daily **free-tier matrix** for this site and the static fleet. Matrix file: `G:\openclaw\business\jarvis\state\free-tier-matrix.json`. Briefing HUD: `GET http://127.0.0.1:8765/briefing/free-tier/matrix`.

| Service | Free ceiling | This stack | Risk today |
|---------|--------------|------------|------------|
| **Cloudflare Pages** (static) | Unlimited requests & bandwidth | Git-connected Pages, no build | None at ~12k req/mo |
| **Cloudflare Pages builds** | 500/month | Manual pushes + weekly Action | Low |
| **Cloudflare file limits** | 20k files; 25 MiB max per file | Small static tree | Low |
| **Cloudflare Workers** | 100k requests/day | Not used (no Functions) | N/A |
| **GitHub Actions** | Free on public repos; else 2k min/mo | 1 weekly RSS workflow | Low |
| **Git LFS / Packages** | Not used | — | N/A |
| **Web3Forms** | 250 submissions/month | Spill / healing / sip forms | Soft cap if forms go viral |
| **Google AdSense** | Policy + serving limits (not a request quota) | Script + ads.txt live; **slot IDs empty** — see [ADSENSE-MANUAL.md](ADSENSE-MANUAL.md) | Revenue blocked until units created |
| **Podcast audio** | Anchor/Spotify hosting | Off-site; site stores URLs only | Not on Cloudflare |

**House rules (local):** `scripts/check-site-size.ps1` blocks push above 1 GB deployable size (warn 80%, block 95%). Cloudflare’s hard per-file limit is **25 MiB**.

**Monitoring:** Cloudflare analytics pull needs `~/.openclaw/secrets/cloudflare.env` (see `desktop-agent/secrets/cloudflare.env.example`). Zone ID goes in Jarvis `config.toml` → `[free_tier_monitor]`.
