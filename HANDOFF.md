# Chittin' and Chattin' — account handoff

Site ownership: **Chittinandchattin** (GitHub + Cloudflare).  
Laughing Dragons no longer hosts the public site after cutover.

---

## Stack

| Piece | Where |
|-------|--------|
| **Repo** | https://github.com/Chittinandchattin/website |
| **Live site** | https://chittinandchattin.com |
| **Hosting** | Cloudflare Pages (auto-deploy on push to `main`) |
| **Episode + sips refresh** | **GitHub Actions** (not a Cloudflare Worker) |

---

## Automatic episode & sips refresh

Every **Monday ~7am Eastern**, GitHub Actions runs [`.github/workflows/refresh-episodes.yml`](.github/workflows/refresh-episodes.yml):

1. `scripts/pull-episodes.py` — pulls Anchor/Spotify RSS → `assets/data/episodes.json`
2. `scripts/extract-sips.py` — rebuilds sips archive → `sips.json`, `sips.txt`, `sips-checklist.csv`
3. Commits and pushes to `main` **only if something changed**
4. Cloudflare Pages redeploys automatically (1–3 minutes)

**Manual run:** GitHub → **Actions** → **Refresh episodes and sips from RSS** → **Run workflow**

**Local run** (same as the workflow):

```powershell
python scripts/pull-episodes.py
python scripts/extract-sips.py
.\scripts\push-update.ps1 "Refresh episodes from RSS"
```

---

## Push site updates

```powershell
cd "G:\Laughing Dragons\Chittinnchattin.com"
.\scripts\preview.ps1          # http://localhost:8780
.\scripts\push-update.ps1 "Describe what you changed"
```

Content locations: see [UPDATE.md](UPDATE.md).

---

## GitHub Actions settings (one-time)

**Settings → Actions → General:**

- Actions permissions: **Allow all actions**
- Workflow permissions: **Read and write** (needed for the bot to commit RSS updates)

The workflow file also sets `permissions: contents: write` — that is what allows pushes.

---

## Cloudflare DNS (important)

Custom domain must use **CNAME** records to `chittinandchattin.pages.dev` (proxied).

Do **not** use A/AAAA records pointing at Cloudflare IPs — that causes **Error 1000** (site down).

If the site breaks after DNS edits: delete A/AAAA for `@` and `www`, re-add custom domains on the Pages project, or restore the two CNAMEs manually.

---

## Verify everything

```powershell
.\scripts\verify-migration.ps1
```

Check `/episodes/` and `/sips/` in the browser after a workflow run.

---

## Laughing Dragons cleanup (after 24–48h stable)

On the **old** Cloudflare account only:

- Remove old Pages custom domains / delete old Pages project
- Remove old zone for `chittinandchattin.com`
- Revoke old API tokens

See [MIGRATION.md](MIGRATION.md) Phase 6.
