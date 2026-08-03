const NAV = [
  { href: "/listen/", label: "Listen" },
  { href: "/episodes/", label: "Episodes" },
  { href: "/about/", label: "About" },
  { href: "/spill-it-bestie/", label: "Spill it" },
  { href: "/healing-inbox/", label: "Healing" },
  { href: "/sips/", label: "Sips" },
];

function isNavActive(activePath, item) {
  if (activePath === item.href) return true;
  return activePath && activePath.startsWith(item.href) && item.href !== "/";
}

function renderHeader(activePath) {
  const cfg = window.SITE_CONFIG || {};
  return `<header class="site-header">
    <div class="container header-inner">
      <a class="brand" href="/" aria-label="${cfg.name} home">
        <img src="/assets/brand/icon.png" alt="${cfg.name}" class="brand-logo" width="72" height="72" />
        <span class="brand-text">${cfg.name}</span>
      </a>
      <button class="nav-toggle" type="button" aria-expanded="false" aria-controls="site-nav">Menu</button>
      <nav id="site-nav" class="site-nav" aria-label="Primary">
        ${NAV.map((item) => {
          const active = isNavActive(activePath, item);
          return `<a href="${item.href}" class="nav-link${active ? " active" : ""}">${item.label}</a>`;
        }).join("")}
      </nav>
    </div>
  </header>`;
}

function renderFooter() {
  const cfg = window.SITE_CONFIG || {};
  const year = new Date().getFullYear();
  const ig = cfg.links?.instagram || "#";
  return `<footer class="site-footer">
    <div class="container footer-grid">
      <div class="footer-brand">
        <img src="/assets/brand/icon.png" alt="" class="footer-logo" width="88" height="88" loading="lazy" />
        <p class="footer-tagline">${cfg.tagline || ""}</p>
      </div>
      <nav class="footer-nav" aria-label="Explore">
        <strong>Explore</strong>
        ${NAV.map((item) => `<a href="${item.href}">${item.label}</a>`).join("")}
        <a href="/contact/">Contact</a>
      </nav>
      <nav class="footer-nav" aria-label="Social">
        <strong>Follow</strong>
        <a href="${cfg.links?.spotify || "#"}" target="_blank" rel="noopener">Spotify</a>
        <a href="${cfg.links?.youtube || "#"}" target="_blank" rel="noopener">YouTube</a>
        <a href="${ig}" target="_blank" rel="noopener">Instagram</a>
        <a href="${cfg.links?.tiktok || "#"}" target="_blank" rel="noopener">TikTok</a>
      </nav>
      <nav class="footer-nav" aria-label="Legal">
        <strong>Legal</strong>
        <a href="/privacy/">Privacy</a>
        <a href="/terms/">Terms</a>
        <a href="/about/">About</a>
      </nav>
    </div>
    <div class="container footer-bottom">
      <p>&copy; ${year} ${cfg.legalName || cfg.name}. All rights reserved.</p>
    </div>
  </footer>`;
}

function renderAdSlot(key, className = "ad-unit") {
  const cfg = window.SITE_CONFIG?.adsense || {};
  const slot = cfg.slots?.[key];
  if (!cfg.publisherId || !slot) {
    return `<div class="${className} ad-placeholder" aria-hidden="true">Ad space</div>`;
  }
  return `<ins class="adsbygoogle ${className}"
    style="display:block"
    data-ad-client="${cfg.publisherId}"
    data-ad-slot="${slot}"
    data-ad-format="auto"
    data-full-width-responsive="true"></ins>`;
}

function pushAds() {
  try {
    (window.adsbygoogle = window.adsbygoogle || []).push({});
  } catch (_) {
    /* AdSense not loaded yet */
  }
}

function renderHero() {
  const cfg = window.SITE_CONFIG || {};
  return `<section class="hero" aria-label="Welcome">
    <div class="hero-media">
      <img class="hero-image" src="/assets/brand/hero.png" alt="" />
      <div class="hero-scrim"></div>
    </div>
    <div class="hero-content container">
      <img class="hero-mark" src="/assets/brand/icon.png" alt="" width="96" height="96" />
      <h1 class="hero-title">${cfg.name}</h1>
      <p class="hero-subline">${cfg.bio || cfg.tagline}</p>
      <div class="hero-cta">
        ${renderListenButtons("btn btn-primary", "btn btn-soft")}
      </div>
    </div>
  </section>`;
}

function renderListenButtons(primaryClass = "btn btn-primary", secondaryClass = "btn btn-soft") {
  const links = window.SITE_CONFIG?.links || {};
  return `<a class="${primaryClass}" href="${links.spotify || "#"}" target="_blank" rel="noopener">Spotify</a>
    <a class="${primaryClass}" href="${links.apple || "#"}" target="_blank" rel="noopener">Apple Podcasts</a>
    <a class="${secondaryClass}" href="${links.youtube || "#"}" target="_blank" rel="noopener">YouTube</a>
    <a class="${secondaryClass}" href="${links.instagram || "#"}" target="_blank" rel="noopener">Instagram</a>`;
}

function renderListenGrid() {
  const links = window.SITE_CONFIG?.links || {};
  const items = [
    { label: "Spotify", href: links.spotify, note: "Direct on Spotify for Creators" },
    { label: "Apple Podcasts", href: links.apple, note: "Listen on iPhone & Mac" },
    { label: "Amazon Music", href: links.amazon, note: "Search & subscribe" },
    { label: "Pocket Casts", href: links.pocketcasts, note: "Follow in Pocket Casts" },
    { label: "Castro", href: links.castro, note: "Follow in Castro" },
    { label: "Overcast", href: links.overcast, note: "Follow in Overcast" },
    { label: "YouTube", href: links.youtube, note: "Clips, episodes & more" },
    { label: "YouTube Music", href: links.youtubeMusic, note: "Search in YT Music" },
    { label: "Instagram", href: links.instagram, note: "DMs, Spill it & Healing inbox" },
    { label: "TikTok", href: links.tiktok, note: "Show account" },
    { label: "iHeartRadio", href: links.iheart, note: "Search on iHeart" },
    { label: "Deezer", href: links.deezer, note: "Search on Deezer" },
    { label: "RSS Feed", href: window.SITE_CONFIG?.feedUrl, note: "Any podcast app" },
  ];
  return `<div class="listen-grid reveal">
    ${items
      .filter((item) => item.href)
      .map(
        (item) => `<a class="listen-card" href="${item.href}" target="_blank" rel="noopener">
        <span class="listen-label">${item.label}</span>
        <span class="listen-note">${item.note}</span>
      </a>`
      )
      .join("")}
  </div>`;
}

function renderFollowShowList() {
  const cfg = window.SITE_CONFIG || {};
  const links = cfg.links || {};
  const items = cfg.followShow || [];
  if (!items.length) {
    return `<ul class="meta-list">
      <li><strong>Instagram</strong> - <a href="${links.instagram || "#"}" target="_blank" rel="noopener">@chittinnchattin</a></li>
    </ul>`;
  }
  return `<ul class="meta-list">
    ${items
      .map((item) => {
        const href =
          item.hrefKey === "feedUrl" ? cfg.feedUrl || links.feedUrl : links[item.hrefKey];
        if (!href) return "";
        const handle = escapeHtml(item.handle || item.label);
        return `<li><strong>${escapeHtml(item.label)}</strong> - <a href="${href}" target="_blank" rel="noopener">${handle}</a></li>`;
      })
      .filter(Boolean)
      .join("")}
  </ul>
  <p class="follow-show-note">Hosted on Spotify for Creators - our RSS feed syndicates to most podcast apps automatically. Can't find us? Search <strong>Chittin' and Chattin</strong>.</p>`;
}

function renderInstagramCTA(label = "Message us on Instagram") {
  const ig = window.SITE_CONFIG?.links?.instagram || "#";
  return `<div class="cta-panel reveal">
    <a class="btn btn-primary btn-lg" href="${ig}" target="_blank" rel="noopener">${label}</a>
    <p class="cta-note">Opens Instagram in a new tab. A private on-site inbox is coming soon.</p>
  </div>`;
}

function renderHostCards() {
  const cfg = window.SITE_CONFIG || {};
  const hosts = cfg.hosts || [];
  return `<div class="host-grid reveal">
    ${hosts
      .map(
        (host) => `<article class="host-card">
        <h3>${host.name}</h3>
        <p class="host-handle">${host.handle}</p>
        <a class="text-link" href="${host.tiktok}" target="_blank" rel="noopener">TikTok &rarr;</a>
      </article>`
      )
      .join("")}
  </div>`;
}

function renderTeaser({ eyebrow, title, body, href, cta, image, reverse = false }) {
  return `<section class="teaser${reverse ? " teaser-reverse" : ""}">
    <div class="container teaser-inner">
      <div class="teaser-copy reveal">
        <p class="teaser-eyebrow">${eyebrow}</p>
        <h2>${title}</h2>
        <p>${body}</p>
        <a class="text-link" href="${href}">${cta} &rarr;</a>
      </div>
      <div class="teaser-visual reveal" aria-hidden="true">
        <div class="teaser-frame" style="background-image:url('${image}')"></div>
      </div>
    </div>
  </section>`;
}

function renderFeaturePage({ eyebrow, title, intro, body, image, ctaLabel, inboxType }) {
  const other =
    inboxType === "spill"
      ? { href: "/healing-inbox/", label: "Healing Inbox", desc: "tender things that want care and space" }
      : { href: "/spill-it-bestie/", label: "Spill it, bestie", desc: "funny, messy, chaotic tea" };

  return `<header class="page-header reveal">
      <p class="teaser-eyebrow">${eyebrow}</p>
      <h1>${title}</h1>
      <p class="page-lead">${intro}</p>
    </header>
    <div class="feature-layout reveal">
      <figure class="feature-art">
        <img src="${image}" alt="" loading="lazy" />
      </figure>
      <div class="prose">
        ${body}
        ${renderInstagramCTA(ctaLabel)}
        <p class="cross-link">Need the other inbox? <a href="${other.href}">${other.label}</a> - ${other.desc}.</p>
      </div>
    </div>`;
}

function truncate(text, max = 280) {
  if (!text || text.length <= max) return text || "";
  return text.slice(0, max).trim() + "…";
}

function escapeHtml(text) {
  if (!text) return "";
  return String(text)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

function renderSipReviewBanner(sips) {
  const needs = sips.filter((s) => s.needsListen).map((s) => s.episodeNumber);
  if (!needs.length) return "";
  const list = needs.join(", ");
  return `<aside class="sip-review-banner reveal" role="note">
    <strong>Episodes needing review:</strong> ${list}
    <span class="sip-review-note">- listen and update <code>sips-overrides.json</code> if you catch more detail.</span>
  </aside>`;
}

function renderSipDetail(sip) {
  const parts = [];
  if (sip.descriptionHtml) {
    parts.push(`<p class="sip-description">${sip.descriptionHtml}</p>`);
  } else if (sip.description) {
    parts.push(`<p class="sip-description">${escapeHtml(sip.description)}</p>`);
  }
  const hosts = sip.hosts || [];
  if (hosts.length) {
    parts.push(
      `<ul class="sip-meta-list">${hosts
        .map((h) => `<li><strong>${escapeHtml(h.host)}:</strong> ${escapeHtml(h.drink)}</li>`)
        .join("")}</ul>`
    );
  }
  const ingredients = sip.ingredients || [];
  if (ingredients.length) {
    parts.push(`<p class="sip-detail-line"><strong>Ingredients:</strong> ${escapeHtml(ingredients.join(", "))}</p>`);
  }
  if (sip.method) {
    parts.push(`<p class="sip-detail-line"><strong>Method:</strong> ${escapeHtml(sip.method)}</p>`);
  }
  if (sip.pairedFood) {
    parts.push(`<p class="sip-detail-line"><strong>Paired with:</strong> ${escapeHtml(sip.pairedFood)}</p>`);
  }
  if (sip.vessel) {
    parts.push(`<p class="sip-detail-line"><strong>Vessel:</strong> ${escapeHtml(sip.vessel)}</p>`);
  }
  if (sip.notes) {
    parts.push(`<p class="sip-detail-line"><strong>Notes:</strong> ${escapeHtml(sip.notes)}</p>`);
  }
  const listen =
    sip.link && sip.link.startsWith("http")
      ? `<a class="btn btn-primary sip-listen" href="${escapeHtml(sip.link)}" target="_blank" rel="noopener">Listen on Spotify</a>`
      : "";
  return `<div class="sip-detail">${parts.join("")}${listen}</div>`;
}

function renderSipCards(sips) {
  if (!sips.length) {
    return `<p class="episode-error">No sips found yet.</p>`;
  }
  const sorted = [...sips].sort((a, b) => a.episodeNumber - b.episodeNumber);
  return `${renderSipReviewBanner(sorted)}
  <div class="sip-list">
    ${sorted
      .map((sip) => {
        const badge = sip.needsListen
          ? `<span class="sip-badge sip-badge-review">needs review</span>`
          : sip.completeness === "partial"
            ? `<span class="sip-badge sip-badge-partial">partial</span>`
            : "";
        const title = escapeHtml(sip.displayName || sip.name || "Sip of the Week");
        return `<details class="sip-card reveal">
          <summary class="sip-summary">
            <span class="sip-ep">Ep ${sip.episodeNumber}</span>
            <span class="sip-summary-text">
              <span class="sip-title">${title}</span>
              <span class="sip-episode-title">${escapeHtml(sip.title)}</span>
              <span class="sip-date">${formatEpisodeDate(sip.published)}</span>
            </span>
            ${badge}
          </summary>
          ${renderSipDetail(sip)}
        </details>`;
      })
      .join("")}
  </div>`;
}

function initSipsPage() {
  const mount = document.getElementById("sip-list-mount");
  if (!mount) return;

  fetch("/assets/data/sips.json")
    .then((res) => {
      if (!res.ok) throw new Error("Failed to load sips");
      return res.json();
    })
    .then((data) => {
      mount.innerHTML = renderSipCards(data.sips || []);
      bindReveal();
    })
    .catch(() => {
      mount.innerHTML = `<p class="episode-error">Could not load sips. Try again later or listen on <a href="/listen/">Spotify</a>.</p>`;
    });
}

function formatEpisodeDate(pubDate) {
  if (!pubDate) return "";
  const d = new Date(pubDate);
  if (Number.isNaN(d.getTime())) return pubDate;
  return d.toLocaleDateString("en-US", { year: "numeric", month: "long", day: "numeric" });
}

const EPISODES_PER_PAGE = 10;

function sortEpisodes(episodes) {
  return [...episodes].sort((a, b) => {
    const na = a.episodeNumber || 0;
    const nb = b.episodeNumber || 0;
    if (na !== nb) return nb - na;
    return new Date(b.published || 0) - new Date(a.published || 0);
  });
}

function getEpisodePageParam() {
  const raw = new URLSearchParams(window.location.search).get("page") || "1";
  const page = parseInt(raw, 10);
  return Number.isFinite(page) && page > 0 ? page : 1;
}

function episodePageHref(page) {
  return page <= 1 ? "/episodes/" : `/episodes/?page=${page}`;
}

function renderEpisodePagination(currentPage, totalPages) {
  if (totalPages <= 1) return "";
  const prev =
    currentPage > 1
      ? `<a class="episode-page-nav" href="${episodePageHref(currentPage - 1)}">&larr; Newer</a>`
      : `<span class="episode-page-nav is-disabled">&larr; Newer</span>`;
  const next =
    currentPage < totalPages
      ? `<a class="episode-page-nav" href="${episodePageHref(currentPage + 1)}">Older &rarr;</a>`
      : `<span class="episode-page-nav is-disabled">Older &rarr;</span>`;
  const nums = Array.from({ length: totalPages }, (_, i) => {
    const n = i + 1;
    if (n === currentPage) {
      return `<span class="episode-page-num active" aria-current="page">${n}</span>`;
    }
    return `<a class="episode-page-num" href="${episodePageHref(n)}">${n}</a>`;
  }).join("");
  return `<nav class="episode-pagination reveal" aria-label="Episode pages">
    ${prev}
    <div class="episode-page-nums">${nums}</div>
    ${next}
  </nav>`;
}

function renderEpisodeCards(episodes, fallbackImage) {
  if (!episodes.length) {
    return `<p class="episode-error">No episodes found yet.</p>`;
  }
  return `<div class="episode-list">
    ${episodes
      .map((ep) => {
        const listenHref =
          ep.link && ep.link.startsWith("http") ? ep.link : "#";
        const thumb = ep.imageUrl || fallbackImage || "/assets/brand/icon.png";
        const epLabel = ep.episodeNumber ? `<span class="episode-num">Ep ${ep.episodeNumber}</span>` : "";
        const duration = ep.duration
          ? `<span class="episode-duration">${escapeHtml(ep.duration)}</span>`
          : "";
        const listen =
          listenHref !== "#"
            ? `<a class="text-link" href="${escapeHtml(listenHref)}" target="_blank" rel="noopener">Listen on Spotify &rarr;</a>`
            : "";
        return `<article class="episode-card reveal">
          <a class="episode-thumb-link" href="${escapeHtml(listenHref)}" target="_blank" rel="noopener" aria-label="Listen: ${escapeHtml(ep.title)}">
            <img class="episode-thumb" src="${escapeHtml(thumb)}" alt="" width="128" height="128" loading="lazy" />
          </a>
          <div class="episode-card-body">
            <div class="episode-card-meta">${epLabel}${duration}</div>
            <h2><a href="${escapeHtml(listenHref)}" target="_blank" rel="noopener">${escapeHtml(ep.title)}</a></h2>
            <p class="episode-date">${formatEpisodeDate(ep.published)}</p>
            <p class="episode-desc">${truncate(ep.description)}</p>
            ${listen}
          </div>
        </article>`;
      })
      .join("")}
  </div>`;
}

function initEpisodesPage() {
  const mount = document.getElementById("episode-list-mount");
  if (!mount) return;

  fetch("/assets/data/episodes.json")
    .then((res) => {
      if (!res.ok) throw new Error("Failed to load episodes");
      return res.json();
    })
    .then((data) => {
      const all = sortEpisodes(data.episodes || []);
      const totalPages = Math.max(1, Math.ceil(all.length / EPISODES_PER_PAGE));
      const requestedPage = getEpisodePageParam();
      const currentPage = Math.min(requestedPage, totalPages);

      if (requestedPage !== currentPage && requestedPage > 1) {
        window.location.replace(episodePageHref(currentPage));
        return;
      }

      const start = (currentPage - 1) * EPISODES_PER_PAGE;
      const pageEpisodes = all.slice(start, start + EPISODES_PER_PAGE);
      const fallback =
        data.spotifyThumbnailUrl || data.channelImageUrl || "/assets/brand/icon.png";
      const rangeStart = all.length ? start + 1 : 0;
      const rangeEnd = start + pageEpisodes.length;

      if (currentPage > 1) {
        document.title = `Episodes (Page ${currentPage}) | ${window.SITE_CONFIG?.name || "Chittin' and Chattin"}`;
      }

      mount.innerHTML = `
        <p class="episode-page-summary reveal">Showing ${rangeStart}-${rangeEnd} of ${all.length} episodes</p>
        ${renderEpisodeCards(pageEpisodes, fallback)}
        <div class="ad-slot ad-mid">${renderAdSlot("inContent", "ad-unit")}</div>
        ${renderEpisodePagination(currentPage, totalPages)}
      `;
      pushAds();
      bindReveal();
    })
    .catch(() => {
      mount.innerHTML = `<p class="episode-error">Could not load episodes. Try again later or listen on <a href="/listen/">Spotify</a>.</p>`;
    });
}

function initPage({ title, description, activePath, content, hero = false, adSlots = true }) {
  const cfg = window.SITE_CONFIG || {};
  document.title = title ? `${title} | ${cfg.name}` : cfg.name;
  const meta = document.querySelector('meta[name="description"]');
  if (meta && description) meta.content = description;

  const root = document.getElementById("app");
  if (!root) return;

  root.innerHTML = `
    ${renderHeader(activePath)}
    ${hero ? renderHero() : ""}
    <main class="${hero ? "page-main" : "container page-main page-inner"}">
      ${!hero && adSlots ? `<div class="ad-slot ad-top">${renderAdSlot("header", "ad-unit")}</div>` : ""}
      ${content}
      ${adSlots ? `<div class="ad-slot ad-bottom">${renderAdSlot("footer", "ad-unit")}</div>` : ""}
    </main>
    ${renderFooter()}
  `;

  if (adSlots) pushAds();
  bindNav();
  bindReveal();
}

function bindNav() {
  const toggle = document.querySelector(".nav-toggle");
  const nav = document.getElementById("site-nav");
  if (!toggle || !nav) return;
  toggle.addEventListener("click", () => {
    const open = nav.classList.toggle("open");
    toggle.setAttribute("aria-expanded", open ? "true" : "false");
  });
}

function bindReveal() {
  const nodes = document.querySelectorAll(".reveal");
  if (!nodes.length || !("IntersectionObserver" in window)) {
    nodes.forEach((n) => n.classList.add("is-visible"));
    return;
  }
  const io = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add("is-visible");
          io.unobserve(entry.target);
        }
      });
    },
    { threshold: 0.08, rootMargin: "0px 0px -4% 0px" }
  );
  nodes.forEach((n) => io.observe(n));
}
