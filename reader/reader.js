(() => {
  "use strict";
  const KEY = "velune-reader-settings-v2";
  const LAST = "velune-reader-last-v2";
  const defaults = {font: "meiryo", fontSize: 17, lineHeight: 1.8, readerWidth: 680, theme: "paper", customColor: "#f4edde"};
  const fonts = {
    serif: '"Noto Serif CJK JP","Hiragino Mincho ProN","Yu Mincho","MS PMincho",serif',
    "yu-mincho": '"Yu Mincho","YuMincho","Hiragino Mincho ProN","Noto Serif CJK JP",serif',
    "hiragino-mincho": '"Hiragino Mincho ProN","Yu Mincho","Noto Serif CJK JP",serif',
    sans: '"Noto Sans CJK JP","Hiragino Kaku Gothic ProN","Yu Gothic","Meiryo",sans-serif',
    meiryo: '"Meiryo UI","Meiryo","Hiragino Kaku Gothic ProN","Yu Gothic","Noto Sans CJK JP",sans-serif',
    "yu-gothic": '"Yu Gothic UI","Yu Gothic","Hiragino Kaku Gothic ProN","Noto Sans CJK JP",sans-serif',
    rounded: '"Hiragino Maru Gothic ProN","Zen Maru Gothic","Arial Rounded MT Bold","Meiryo",sans-serif',
    mono: '"BIZ UDゴシック","BIZ UDGothic","Noto Sans Mono CJK JP","MS Gothic",monospace'
  };
  const palettes = {
    paper: "#f4edde", light: "#ffffff", ivory: "#fff8e7", sand: "#eddfc7",
    rose: "#f9e6eb", peach: "#fae1d5", lavender: "#eae4f5", sky: "#dceef5",
    mint: "#e0f4e9", sage: "#e7edda", slate: "#dce3ea", dark: "#2c3036",
    night: "#171b22", sepia: "#423a31"
  };
  const el = id => document.getElementById(id);
  function read(key, fallback) {
    try { const v = localStorage.getItem(key); return v === null ? fallback : JSON.parse(v); }
    catch { return fallback; }
  }
  function save(key, value) {
    try { localStorage.setItem(key, JSON.stringify(value)); }
    catch {}
  }
  const stored = read(KEY, null);
  const legacy = stored === null ? read("velune-reader-settings-v1", null) : null;
  const earlier = stored || legacy;
  const settings = {...defaults, ...(earlier && typeof earlier === "object" ? earlier : {})};
  // Only migrate the old untouched 18/1.9/720 defaults, never override custom sizes.
  if (stored === null && legacy && Number(legacy.fontSize) === 18 &&
      Number(legacy.lineHeight) === 1.9 && Number(legacy.readerWidth) === 720) {
    settings.fontSize = defaults.fontSize;
    settings.lineHeight = defaults.lineHeight;
    settings.readerWidth = defaults.readerWidth;
  }

  const readingPresets = {
    compact: {fontSize: 15, lineHeight: 1.6, readerWidth: 720},
    standard: {fontSize: 17, lineHeight: 1.8, readerWidth: 680},
    relaxed: {fontSize: 19, lineHeight: 2.0, readerWidth: 640}
  };
  function luminance(hex) {
    const rgb = [1, 3, 5].map(index => parseInt(hex.slice(index, index + 2), 16) / 255);
    return rgb.map(channel => channel <= 0.04045 ? channel / 12.92 : Math.pow((channel + 0.055) / 1.055, 2.4))
      .reduce((sum, channel, index) => sum + channel * [0.2126, 0.7152, 0.0722][index], 0);
  }
  function apply() {
    if (!(settings.font in fonts)) settings.font = defaults.font;
    if (!(settings.theme in palettes) && settings.theme !== "custom") settings.theme = defaults.theme;
    if (!/^#[0-9a-f]{6}$/i.test(settings.customColor)) settings.customColor = defaults.customColor;
    settings.fontSize = Math.max(14, Math.min(28, Number(settings.fontSize) || defaults.fontSize));
    settings.lineHeight = Math.max(1.4, Math.min(2.6, Number(settings.lineHeight) || defaults.lineHeight));
    settings.readerWidth = Math.max(480, Math.min(960, Number(settings.readerWidth) || defaults.readerWidth));
    const root = document.documentElement;
    const bg = settings.theme === "custom" ? settings.customColor : palettes[settings.theme];
    const isDark = luminance(bg) < 0.24;
    root.dataset.theme = settings.theme;
    root.style.colorScheme = isDark ? "dark" : "light";
    root.style.setProperty("--bg", bg);
    root.style.setProperty("--fg", isDark ? "#f3f0eb" : "#242a2d");
    root.style.setProperty("--muted", isDark ? "#c6c9cd" : "#566069");
    root.style.setProperty("--line", isDark ? "#66696d" : "#c4c7c7");
    root.style.setProperty("--accent", isDark ? "#f1ca92" : "#5a5245");
    root.style.setProperty("--reader-font", fonts[settings.font]);
    root.style.setProperty("--font-size", settings.fontSize + "px");
    root.style.setProperty("--line-height", settings.lineHeight.toFixed(1));
    root.style.setProperty("--reader-width", settings.readerWidth + "px");
    const nums = {"font-size": settings.fontSize, "line-height": settings.lineHeight, "reader-width": settings.readerWidth};
    Object.entries(nums).forEach(([id, value]) => { if (el(id)) el(id).value = value; });
    if (el("font-value")) el("font-value").textContent = settings.fontSize + "px";
    if (el("line-value")) el("line-value").textContent = settings.lineHeight.toFixed(1);
    if (el("width-value")) el("width-value").textContent = settings.readerWidth + "px";
    document.querySelectorAll('input[name="theme"]').forEach(input => { input.checked = input.value === settings.theme; });
    document.querySelectorAll('input[name="font"]').forEach(input => { input.checked = input.value === settings.font; });
    if (el("custom-color")) el("custom-color").value = settings.customColor;
    document.querySelectorAll("[data-reading-preset]").forEach(button => {
      const preset = readingPresets[button.dataset.readingPreset];
      const active = preset && preset.fontSize === settings.fontSize &&
        preset.lineHeight === settings.lineHeight && preset.readerWidth === settings.readerWidth;
      button.setAttribute("aria-pressed", active ? "true" : "false");
    });
  }
  apply();
  const dialog = el("settings");
  el("open-settings")?.addEventListener("click", () => dialog?.showModal());
  dialog?.addEventListener("click", event => { if (event.target === dialog) dialog.close(); });
  document.querySelectorAll('input[name="font"]').forEach(input =>
    input.addEventListener("change", event => { settings.font = event.currentTarget.value; apply(); save(KEY, settings); })
  );
  document.querySelectorAll('input[name="theme"]').forEach(input =>
    input.addEventListener("change", event => { settings.theme = event.currentTarget.value; apply(); save(KEY, settings); })
  );
  el("custom-color")?.addEventListener("input", event => {
    settings.customColor = event.currentTarget.value;
    settings.theme = "custom";
    apply();
    save(KEY, settings);
  });
  [
    ["font-size", "fontSize"],
    ["line-height", "lineHeight"],
    ["reader-width", "readerWidth"]
  ].forEach(([id, prop]) =>
    el(id)?.addEventListener("input", event => {
      settings[prop] = Number(event.currentTarget.value);
      apply();
      save(KEY, settings);
    })
  );
  document.querySelectorAll("[data-reading-preset]").forEach(button =>
    button.addEventListener("click", () => {
      const preset = readingPresets[button.dataset.readingPreset];
      if (!preset) return;
      Object.assign(settings, preset);
      apply();
      save(KEY, settings);
    })
  );
  el("reset-settings")?.addEventListener("click", () => {
    Object.assign(settings, defaults);
    apply();
    save(KEY, settings);
  });

  const tocDialog = el("chapter-list");
  el("open-toc")?.addEventListener("click", () => {
    tocDialog?.showModal();
    const active = tocDialog?.querySelector('[aria-current="page"]');
    if (active) requestAnimationFrame(() => active.scrollIntoView({block: "center"}));
  });
  el("close-toc")?.addEventListener("click", () => tocDialog?.close());
  tocDialog?.addEventListener("click", event => {
    if (event.target === tocDialog) tocDialog.close();
  });
  el("chapter-filter")?.addEventListener("input", event => {
    const needle = event.currentTarget.value.trim().normalize("NFKC").toLowerCase();
    tocDialog.querySelectorAll(".drawer-toc li").forEach(item => {
      item.hidden = !item.textContent.normalize("NFKC").toLowerCase().includes(needle);
    });
  });

  if (document.body.dataset.episode === "true") {
    const title = document.querySelector(".prose h1")?.textContent || document.title;
    const positionKey = "velune-reader-scroll:" + location.pathname;
    const previous = Number(read(positionKey, 0));
    if (Number.isFinite(previous) && previous > 0) {
      requestAnimationFrame(() => scrollTo({top: previous, behavior: "instant"}));
    }
    let pending = false;
    const updateProgress = () => {
      const denominator = document.documentElement.scrollHeight - innerHeight;
      const progress = denominator > 0 ? Math.min(1, Math.max(0, scrollY / denominator)) : 1;
      const progressTrack = el("progress-track");
      if (progressTrack) progressTrack.style.width = (progress * 100).toFixed(2) + "%";
      save(positionKey, Math.round(scrollY));
      // Visiting the first page is not reading progress. Resume appears only
      // after an actual scroll into the chapter (including a restored position).
      if (scrollY >= 140) save(LAST, {path: location.pathname, title});
      pending = false;
    };
    window.addEventListener("scroll", () => {
      if (!pending) { pending = true; requestAnimationFrame(updateProgress); }
    }, {passive: true});
    window.addEventListener("resize", updateProgress, {passive: true});
    updateProgress();
  } else {
    const last = read(LAST, null);
    const continuation = el("continue-reading");
    const episodeRoot = new URL("episodes/", location.href).pathname;
    if (last && typeof last.path === "string" && last.path.startsWith(episodeRoot) && /^\/[^?#]*\.html$/.test(last.path) && continuation) {
      const match = Array.from(document.querySelectorAll(".toc a")).find(a => new URL(a.href).pathname === last.path);
      if (match) {
        continuation.href = last.path;
        continuation.textContent = "続きを読む：" + match.textContent.trim() + " →";
        continuation.hidden = false;
      }
    }
    el("toc-filter")?.addEventListener("input", event => {
      const needle = event.currentTarget.value.trim().normalize("NFKC").toLowerCase();
      let visible = 0;
      document.querySelectorAll(".toc li").forEach(li => {
        const show = li.textContent.normalize("NFKC").toLowerCase().includes(needle);
        li.hidden = !show;
        if (show) visible++;
      });
      if (el("toc-count")) el("toc-count").textContent = visible + "話";
    });
  }

  const state = el("offline-state");
  const EPISODE_CACHE = "velune-episodes-v1";
  const inEpisode = document.body.dataset.episode === "true";
  let offlineReady = false;
  let currentSaved = false;
  const showNetwork = () => {
    if (!state) return;
    const offline = !navigator.onLine;
    if (inEpisode && currentSaved) state.textContent = offline ? "オフライン · 保存済み" : "この話を保存済み";
    else state.textContent = offline ? "オフライン" : offlineReady ? "オフライン対応" : "";
  };
  window.addEventListener("online", showNetwork);
  window.addEventListener("offline", showNetwork);
  showNetwork();

  async function saveCurrentEpisode() {
    if (!inEpisode || !("caches" in window)) return;
    const cache = await caches.open(EPISODE_CACHE);
    const url = location.origin + location.pathname;
    const existing = await cache.match(url);
    if (existing) { currentSaved = true; showNetwork(); return; }
    if (!navigator.onLine) return;
    try {
      // Initial navigation can precede SW activation. Save the HTML explicitly.
      const response = await fetch(url, {cache: "reload"});
      if (response.ok) {
        await cache.put(url, response.clone());
        currentSaved = true;
        showNetwork();
      }
    } catch {
      if (!existing && state) state.textContent = "オフライン保存に失敗";
    }
  }

  async function savedEpisodeCount(links, cache) {
    let total = 0;
    for (const url of links) if (await cache.match(url)) total++;
    return total;
  }

  async function setupFullDownload() {
    const button = el("save-all");
    const progress = el("offline-progress");
    if (!button || !progress || !("caches" in window)) return;
    const links = [...document.querySelectorAll(".toc a")].map(a => a.href);
    const cache = await caches.open(EPISODE_CACHE);
    const report = async message => {
      const count = await savedEpisodeCount(links, cache);
      progress.textContent = (message || "保存済み") + "：" + count + " / " + links.length + "話";
      return count;
    };
    await report("保存済み");
    button.addEventListener("click", async () => {
      button.disabled = true;
      button.textContent = "保存中…";
      let failed = 0;
      // Limit parallel requests, avoiding unnecessary mobile network pressure.
      for (let start = 0; start < links.length; start += 3) {
        const batch = links.slice(start, start + 3);
        await Promise.all(batch.map(async url => {
          try {
            if (await cache.match(url)) return;
            const response = await fetch(url, {cache: "reload"});
            if (!response.ok) throw new Error("HTTP " + response.status);
            await cache.put(url, response.clone());
          } catch { failed++; }
        }));
        await report("保存中");
      }
      await report(failed ? "一部保存できませんでした（再試行できます）" : "オフライン保存完了");
      button.textContent = failed ? "残りを保存" : "保存済み";
      button.disabled = failed === 0;
    });
  }

  if ("serviceWorker" in navigator && location.protocol === "https:") {
    const root = document.querySelector('meta[name="app-root"]').content;
    navigator.serviceWorker.register(new URL(root + "sw.js", location.href))
      .then(() => navigator.serviceWorker.ready)
      .then(async () => {
        offlineReady = true;
        showNetwork();
        await saveCurrentEpisode();
        await setupFullDownload();
      })
      .catch(() => { if (state) state.textContent = navigator.onLine ? "オフライン設定に失敗" : "オフライン"; });
  }
})();
