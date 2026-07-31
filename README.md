# Chittin' and Chattin — Podcast Site

Static site for **chittinnchattin.com** — listen links, host bios, Spill it / Healing inbox (Instagram for now), and Sips archive stub.

## Stack

- Static HTML + CSS + JS (no build step)
- GitHub → Cloudflare Pages (auto-deploy on push to `main`)
- Google AdSense (`ca-pub-7048606415692002`) — shared with Laughing Dragons

## Preview locally

```powershell
cd "G:\Laughing Dragons\Chittinnchattin.com"
.\scripts\preview.ps1
```

Open `http://localhost:8080/`

## Push updates

```powershell
.\scripts\push-update.ps1 "Describe what you changed"
```

See [UPDATE.md](UPDATE.md) for content edits and phase-2 plans.

## Deploy

See [DEPLOY.md](DEPLOY.md) for GitHub, Cloudflare Pages, dual domains, and AdSense.
