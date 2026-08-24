# Migrate to `chittinandchattin` (GitHub + Cloudflare)

Move the site from `laughingdragonsproductions` / old Cloudflare to the **chittinandchattin** accounts.

**New GitHub repo:** [Chittinandchattin/website](https://github.com/Chittinandchattin/website)  
**Accounts:** GitHub `Chittinandchattin` · Cloudflare `chittinandchattin` (same login)

Follow phases in order — do not change nameservers until Phase 4.

---

## Phase 1 — GitHub transfer

1. Sign into GitHub as **`chittinandchattin`** (and ensure you can admin the old repo).
2. Open **https://github.com/laughingdragonsproductions/Chittinandchattin/settings**
3. Scroll to **Danger Zone** → **Transfer ownership**
4. New owner: **`chittinandchattin`**
5. Accept the transfer if prompted on the new account.
6. Confirm the repo lives at **https://github.com/Chittinandchattin/website**
7. **Settings → Actions → General** — ensure Actions are allowed (needed for Monday RSS refresh).
8. Locally, run:
   ```powershell
   cd "G:\Laughing Dragons\Chittinnchattin.com"
   .\scripts\push-to-new-github.ps1
   ```
   Or if the repo already has commits: `.\scripts\migrate-github-remote.ps1`
9. Optional: `gh auth login` as `chittinandchattin`, then re-run the script to verify Actions.

**Expected:** No site downtime. Old Cloudflare Pages may show a broken Git link until Phase 2–4.

---

## Phase 2 — New Cloudflare Pages (before DNS)

On the **new** Cloudflare account:

1. **Workers & Pages** → **Create** → **Pages** → **Connect to Git**
2. Authorize GitHub; select **`Chittinandchattin/website`**
3. Build settings:
   - Framework preset: **None**
   - Build command: *(empty)*
   - Build output directory: **`/`**
4. Deploy and note the `*.pages.dev` preview URL.
5. Spot-check preview: `/`, `/listen/`, `/ads.txt`, `/sitemap.xml`

Do **not** delete the old Pages project yet.

---

## Phase 3 — DNS on new Cloudflare account

### On the **old** Cloudflare account

1. Open zone **`chittinandchattin.com`**
2. **DNS → Export** (or screenshot every record)
3. Note **Redirect Rules**, **SSL/TLS** mode, and any email records (MX, SPF, DKIM TXT)

### On the **new** Cloudflare account

1. **Add a site** → `chittinandchattin.com` (Free plan)
2. Recreate all DNS records from the export
3. Copy the **new nameservers** — do **not** change the registrar yet
4. Match SSL/TLS to old zone (usually **Full** for Pages)

---

## Phase 4 — Nameserver cutover

1. New Pages project → **Custom domains** → add:
   - `chittinandchattin.com`
   - `www.chittinandchattin.com`
2. At the **domain registrar**, replace nameservers with the **new** Cloudflare pair
3. Wait for propagation (minutes–hours)
4. Run verification:
   ```powershell
   .\scripts\verify-migration.ps1
   ```
5. Recreate any **Redirect Rules** from the old zone (e.g. alias domains → canonical)

Until NS flip, traffic still uses the **old** zone — intentional.

---

## Phase 5 — Docs and monitoring secrets

Repo docs already point at the new GitHub URL. After cutover, refresh local monitoring if you use Jarvis / OpenClaw:

| Item | Location |
|------|----------|
| Cloudflare API token | `~/.openclaw/secrets/cloudflare.env` |
| Zone ID | Jarvis `config.toml` → `[free_tier_monitor]` |

Create a new API token on the **new** Cloudflare account (Zone → Analytics read, Zone read).

---

## Phase 6 — Retire old Cloudflare (wait 24–48h)

Only after `verify-migration.ps1` passes on production:

- [ ] Remove custom domains from **old** Pages (or delete old project)
- [ ] Remove/cancel old zone on old Cloudflare account
- [ ] Revoke old Cloudflare API tokens
- [ ] Old GitHub org can stay; transferred repo redirects automatically

---

## Post-migration: RSS / sips automation

Episode and sips refresh is **GitHub Actions**, not a Cloudflare Worker.

- Workflow: [`.github/workflows/refresh-episodes.yml`](.github/workflows/refresh-episodes.yml)
- Schedule: Monday ~7am Eastern
- Manual run: GitHub → **Actions** → **Refresh episodes and sips from RSS** → **Run workflow**
- Handoff details: [HANDOFF.md](HANDOFF.md)

---

## Quick commands

```powershell
# After GitHub transfer
.\scripts\migrate-github-remote.ps1

# After DNS cutover
.\scripts\verify-migration.ps1

# Normal deploy (unchanged)
.\scripts\push-update.ps1 "Your message"
```
