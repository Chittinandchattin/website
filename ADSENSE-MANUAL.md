# AdSense — manual steps for Brandon

Code changes from the AdSense readiness batch are live after deploy. Complete these steps in **Google AdSense**:

## Current status (code)

| Item | Status |
|------|--------|
| Publisher script on every page | Live (`ca-pub-7048606415692002`) |
| `ads.txt` at repo root | Live |
| Privacy / Terms / About / Contact | Linked in footer |
| **Ad unit slot IDs** in `assets/js/config.js` | **Empty** — no `<ins>` units render until IDs are pasted |
| Home hero | `adSlots: false` (no header ad on homepage) |

Until slot IDs are filled, browsers load the AdSense bootstrap script but **no display ads are requested** and there is no ad revenue from this site.

## 1. Create ad units

AdSense → **Ads** → **By ad unit** → **Display ads**

| Unit name | Site |
|-----------|------|
| Chittin Header | chittinandchattin.com |
| Chittin Footer | chittinandchattin.com |
| Chittin In-content (optional) | chittinandchattin.com |

Update `assets/js/config.js` → `adsense.slots` (`header`, `footer`, `inContent`) and push.

## 2. EU consent (CMP)

AdSense → **Privacy & messaging** → **European regulations**

- Publish message for `chittinandchattin.com`
- Link to `https://chittinandchattin.com/privacy/`

## 3. Add site

AdSense → **Sites** → **+ New site** → `chittinandchattin.com`

Confirm ads.txt detected.

## 4. Search Console (recommended)

- Verify domain
- Submit `https://chittinandchattin.com/sitemap.xml`

## 5. Request review

Submit **chittinandchattin.com first** (higher readiness, no kids content).

Publisher: `ca-pub-7048606415692002`

## Jarvis monitoring

Jarvis free-tier matrix flags `slots_configured: false` until slot IDs exist. AdSense **email** alerts (policy / serving limits) use the existing Gmail monitor in `desktop-agent` — separate from hosting quotas. See [DEPLOY.md](DEPLOY.md) → Free-tier map.
