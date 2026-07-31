const NAV = [
  { href: "/listen/", label: "Listen" },
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
    { label: "YouTube", href: links.youtube, note: "Clips, episodes & more" },
    { label: "Instagram", href: links.instagram, note: "DMs, Spill it & Healing inbox" },
    { label: "TikTok", href: links.tiktok, note: "Show account" },
    { label: "Amazon Music", href: links.amazon, note: "Search Chittin' and Chattin" },
  ];
  return `<div class="listen-grid reveal">
    ${items
      .map(
        (item) => `<a class="listen-card" href="${item.href}" target="_blank" rel="noopener">
        <span class="listen-label">${item.label}</span>
        <span class="listen-note">${item.note}</span>
      </a>`
      )
      .join("")}
  </div>`;
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
        <p class="cross-link">Need the other inbox? <a href="${other.href}">${other.label}</a> — ${other.desc}.</p>
      </div>
    </div>`;
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
