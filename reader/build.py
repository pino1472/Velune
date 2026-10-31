#!/usr/bin/env python3
"""Build a public, prose-only GitHub Pages PWA; no INDEX or other sources are copied."""
from __future__ import annotations
import hashlib
import html
import json
import re
import shutil
from pathlib import Path
from markdown_it import MarkdownIt

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "_source" / "story" / "prose"
DEST = ROOT / "dist"
EPISODE_FILE = re.compile(r"^第([0-9]+)話\.md$")
HEADLINE = re.compile(r"^# +([^\n]+)\s*$", flags=re.MULTILINE)
TITLE = "リヴェルナ・オンライン"
MARKDOWN = MarkdownIt("commonmark", {"html": False, "linkify": False}).enable("table").enable("strikethrough")


def episode_data(path: Path) -> dict:
    number = int(EPISODE_FILE.fullmatch(path.name).group(1))
    source = path.read_text(encoding="utf-8-sig")
    # Ignore metadata even if its fields change. Publish only from first H1 downward.
    if source.startswith("---\n"):
        end = re.search(r"^---\s*$", source[4:], flags=re.MULTILINE)
        if end is None:
            raise ValueError(f"Unclosed YAML frontmatter: {path}")
        source = source[4 + end.end():]
    heading = HEADLINE.search(source)
    if heading is None:
        raise ValueError(f"No level-1 story title: {path}")
    body = source[heading.start():].strip()
    heading_text = heading.group(1).strip()
    return {"number": number, "name": heading_text,
            "html": MARKDOWN.render(body), "slug": str(number).zfill(3)}


def document(title: str, body: str, *, asset_prefix: str, is_episode: bool, previous: str = "", following: str = "") -> str:
    settings = '''<dialog id="settings" aria-label="表示設定">
      <form method="dialog" class="settings-panel">
        <div class="settings-head"><div><p class="settings-eyebrow">READING PREFERENCES</p><h2>表示設定</h2></div><button class="icon-btn" aria-label="閉じる" value="close">×</button></div>
        <fieldset><legend>フォント</legend><div class="font-choice">
          <label class="font-card" data-font="serif"><input name="font" type="radio" value="serif"><span class="font-name">標準の明朝</span><span class="font-sample demo-serif">あいうえお 漢字</span></label>
          <label class="font-card" data-font="yu-mincho"><input name="font" type="radio" value="yu-mincho"><span class="font-name">游明朝</span><span class="font-sample demo-yumincho">あいうえお 漢字</span></label>
          <label class="font-card" data-font="hiragino-mincho"><input name="font" type="radio" value="hiragino-mincho"><span class="font-name">ヒラギノ明朝</span><span class="font-sample demo-hiraginomincho">あいうえお 漢字</span></label>
          <label class="font-card" data-font="sans"><input name="font" type="radio" value="sans"><span class="font-name">標準のゴシック</span><span class="font-sample demo-sans">あいうえお 漢字</span></label>
          <label class="font-card" data-font="meiryo"><input name="font" type="radio" value="meiryo"><span class="font-name">Meiryo UI</span><span class="font-sample demo-meiryo">あいうえお 漢字</span></label>
          <label class="font-card" data-font="yu-gothic"><input name="font" type="radio" value="yu-gothic"><span class="font-name">游ゴシック</span><span class="font-sample demo-yugothic">あいうえお 漢字</span></label>
          <label class="font-card" data-font="rounded"><input name="font" type="radio" value="rounded"><span class="font-name">丸ゴシック</span><span class="font-sample demo-rounded">あいうえお 漢字</span></label>
          <label class="font-card" data-font="mono"><input name="font" type="radio" value="mono"><span class="font-name">等幅</span><span class="font-sample demo-mono">あいうえお 漢字</span></label>
        </div><p class="settings-hint">端末にないフォントは近い書体で表示されます。</p></fieldset>
        <fieldset><legend>背景カラーパレット</legend><div class="color-choice">
          <label><input name="theme" type="radio" value="paper"><span class="color-swatch" style="--swatch:#f4edde"></span><span>生成り</span></label>
          <label><input name="theme" type="radio" value="light"><span class="color-swatch" style="--swatch:#ffffff"></span><span>白</span></label>
          <label><input name="theme" type="radio" value="ivory"><span class="color-swatch" style="--swatch:#fff8e7"></span><span>象牙</span></label>
          <label><input name="theme" type="radio" value="sand"><span class="color-swatch" style="--swatch:#eddfc7"></span><span>砂色</span></label>
          <label><input name="theme" type="radio" value="rose"><span class="color-swatch" style="--swatch:#f9e6eb"></span><span>薄桜</span></label>
          <label><input name="theme" type="radio" value="peach"><span class="color-swatch" style="--swatch:#fae1d5"></span><span>桃色</span></label>
          <label><input name="theme" type="radio" value="lavender"><span class="color-swatch" style="--swatch:#eae4f5"></span><span>藤色</span></label>
          <label><input name="theme" type="radio" value="sky"><span class="color-swatch" style="--swatch:#dceef5"></span><span>空色</span></label>
          <label><input name="theme" type="radio" value="mint"><span class="color-swatch" style="--swatch:#e0f4e9"></span><span>薄荷</span></label>
          <label><input name="theme" type="radio" value="sage"><span class="color-swatch" style="--swatch:#e7edda"></span><span>若草</span></label>
          <label><input name="theme" type="radio" value="slate"><span class="color-swatch" style="--swatch:#dce3ea"></span><span>灰青</span></label>
          <label><input name="theme" type="radio" value="dark"><span class="color-swatch" style="--swatch:#2c3036"></span><span>墨色</span></label>
          <label><input name="theme" type="radio" value="night"><span class="color-swatch" style="--swatch:#171b22"></span><span>夜</span></label>
          <label><input name="theme" type="radio" value="sepia"><span class="color-swatch" style="--swatch:#423a31"></span><span>焦茶</span></label>
          <label class="custom-theme"><input name="theme" type="radio" value="custom"><span class="custom-picker"><input type="color" id="custom-color" value="#f4edde" aria-label="好きな背景色を選択"></span><span>自由色</span></label>
        </div></fieldset>
        <div class="settings-preview" aria-label="本文プレビュー"><span>プレビュー</span><p>　物語は、ここから始まる。</p><p>　お気に入りの文字と色で、続きを読もう。</p></div>
        <label class="setting-range">文字サイズ <output id="font-value">18px</output><input id="font-size" type="range" min="14" max="28" value="18" step="1"></label>
        <label class="setting-range">行間 <output id="line-value">1.9</output><input id="line-height" type="range" min="1.4" max="2.6" value="1.9" step="0.1"></label>
        <label class="setting-range">本文の幅 <output id="width-value">720px</output><input id="reader-width" type="range" min="480" max="960" value="720" step="40"></label>
        <button id="reset-settings" class="reset-btn" type="button">表示設定を初期化</button>
      </form></dialog>'''
    nav = '<nav class="chapter-nav" aria-label="話数移動">'
    nav += (f'<a rel="prev" href="{previous}">← 前の話</a>' if previous else '<span></span>')
    nav += f'<a href="{asset_prefix}index.html">目次</a>'
    nav += (f'<a rel="next" href="{following}">次の話 →</a>' if following else '<span></span>')
    nav += '</nav>'
    return f'''<!doctype html>
<html lang="ja" data-theme="paper"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="theme-color" content="#f4edde"><meta name="app-root" content="{asset_prefix}"><meta name="description" content="リヴェルナ・オンライン 小説リーダー">
<link rel="manifest" href="{asset_prefix}manifest.webmanifest"><link rel="icon" href="{asset_prefix}icon.svg" type="image/svg+xml">
<link rel="stylesheet" href="{asset_prefix}assets/reader.css"><title>{html.escape(title)} - {TITLE}</title></head>
<body data-episode="{'true' if is_episode else 'false'}">
<header class="topbar"><a class="brand" href="{asset_prefix}index.html">リヴェルナ・オンライン</a><div class="topbar-controls"><span class="offline-state" id="offline-state" aria-live="polite"></span><button id="open-settings" type="button" class="icon-btn" aria-label="表示設定">Aa</button></div></header>
<main class="reading-area">{body}</main>
{nav if is_episode else ''}
{settings}<div class="progress-track" id="progress-track" aria-hidden="true"></div>
<script defer src="{asset_prefix}assets/reader.js"></script></body></html>'''


def build() -> None:
    if not SOURCE.is_dir():
        raise SystemExit(f"Missing prose directory: {SOURCE}")
    episodes = [episode_data(path) for path in SOURCE.iterdir()
                if path.is_file() and EPISODE_FILE.fullmatch(path.name)]
    episodes.sort(key=lambda episode: episode["number"])
    if not episodes:
        raise SystemExit("No matching 第NNN話.md prose files found")
    numbers = [x["number"] for x in episodes]
    if len(numbers) != len(set(numbers)):
        raise SystemExit("Duplicate numeric episode filenames")
    if DEST.exists():
        shutil.rmtree(DEST)
    (DEST / "episodes").mkdir(parents=True)
    (DEST / "assets").mkdir()
    for name in ("reader.css", "reader.js"):
        shutil.copyfile(ROOT / "reader" / name, DEST / "assets" / name)
    (DEST / "icon.svg").write_text('''<svg xmlns="http://www.w3.org/2000/svg" width="192" height="192" viewBox="0 0 192 192"><rect width="192" height="192" rx="40" fill="#4d483d"/><path d="M38 50c25-11 44-4 58 7 14-11 33-18 58-7v94c-25-11-44-4-58 7-14-11-33-18-58-7z" stroke="#f5eddc" stroke-width="9" fill="none"/><path d="M96 57v95" stroke="#f5eddc" stroke-width="8"/></svg>''', encoding="utf8")
    manifest = {"name": TITLE, "short_name": "リヴェルナ", "lang": "ja",
                "start_url": "./index.html", "scope": "./", "display": "standalone", "background_color": "#f4edde", "theme_color": "#4d483d",
                "icons": [{"src": "./icon.svg", "sizes": "any", "type": "image/svg+xml", "purpose": "any maskable"}]}
    (DEST / "manifest.webmanifest").write_text(json.dumps(manifest, ensure_ascii=False), encoding="utf8")
    (DEST / ".nojekyll").write_text("", encoding="utf8")
    for position, ep in enumerate(episodes):
        previous = f'{episodes[position-1]["slug"]}.html' if position else ""
        following = f'{episodes[position+1]["slug"]}.html' if position + 1 < len(episodes) else ""
        body = f'<article class="prose" data-title="{html.escape(ep["name"], quote=True)}">{ep["html"]}</article>'
        page = document(ep["name"], body, asset_prefix="../", is_episode=True,
                        previous=previous, following=following)
        (DEST / "episodes" / f'{ep["slug"]}.html').write_text(page, encoding="utf8")
    links = "\n".join(f'<li><a href="./episodes/{ep["slug"]}.html">{html.escape(ep["name"])}</a></li>' for ep in episodes)
    home = f'''<section class="home"><p class="eyebrow">NOVEL READER</p><h1>{TITLE}</h1><p class="subheading">物語を読む</p><a class="continue" id="continue-reading" hidden>続きを読む →</a><section class="offline-library" aria-label="オフライン保存"><div><strong>オフライン読書</strong><p>開いた話は自動保存。電波がない場所でも読めます。</p></div><button type="button" id="save-all">全話を保存</button><p class="offline-progress" id="offline-progress" aria-live="polite">保存済みの話を確認しています</p></section><div class="toc-heading"><h2>目次</h2><span id="toc-count">{len(episodes)}話</span></div><label class="search-wrapper"><span aria-hidden="true">⌕</span><input id="toc-filter" type="search" placeholder="話数・タイトルで探す" aria-label="話数やタイトルで探す"></label><ol class="toc">{links}</ol></section>'''
    (DEST / "index.html").write_text(document(TITLE, home, asset_prefix="./", is_episode=False), encoding="utf8")
    # Keep app shell immediately usable offline; each opened episode is cached on demand.
    shell_urls = ["./", "./index.html", "./assets/reader.css",
                  "./assets/reader.js", "./manifest.webmanifest", "./icon.svg"]
    episode_urls = ["./episodes/" + ep["slug"] + ".html" for ep in episodes]
    digest = hashlib.sha256(
        "".join(p.read_text(encoding="utf8") for p in sorted(DEST.rglob("*")) if p.is_file()).encode()
    ).hexdigest()[:16]
    sw = r'''const SHELL = "revalna-shell-__BUILD__";
const EPISODES = "revalna-episodes-v1";
const SHELL_FILES = __SHELL_FILES__;
const EPISODE_FILES = __EPISODE_FILES__;
const scope = self.registration.scope;
const allowed = new Set(EPISODE_FILES.map(path => new URL(path, scope).pathname));
const offlinePage = '<!doctype html><html lang="ja"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>未保存の話</title><body style="font:18px/1.8 system-ui;padding:24px"><h1>この話は保存されていません</h1><p>オンラインで一度開くか、目次の「全話を保存」を利用してください。</p><p><a href="../index.html">目次に戻る</a></p></body></html>';

self.addEventListener("install", event => {
  event.waitUntil(caches.open(SHELL)
    .then(cache => cache.addAll(SHELL_FILES.map(path => new URL(path, scope))))
    .then(() => self.skipWaiting()));
});
self.addEventListener("activate", event => {
  event.waitUntil((async () => {
    const names = await caches.keys();
    await Promise.all(names.filter(name =>
      (name.startsWith("revalna-shell-") && name !== SHELL) ||
      name.startsWith("revalna-reader-")).map(name => caches.delete(name)));
    const chapters = await caches.open(EPISODES);
    for (const request of await chapters.keys()) {
      if (!allowed.has(new URL(request.url).pathname)) await chapters.delete(request);
    }
    await self.clients.claim();
  })());
});
self.addEventListener("fetch", event => {
  const req = event.request;
  const url = new URL(req.url);
  if (req.method !== "GET" || url.origin !== self.location.origin || !url.href.startsWith(scope)) return;
  if (allowed.has(url.pathname)) {
    event.respondWith((async () => {
      const cache = await caches.open(EPISODES);
      const cached = await cache.match(req, {ignoreSearch: true});
      const update = fetch(req).then(async response => {
        if (response.ok) await cache.put(req, response.clone()).catch(() => {});
        else if (response.status === 404 || response.status === 410) await cache.delete(req);
        return response;
      });
      if (cached && req.cache !== "reload") {
        event.waitUntil(update.catch(() => {}));
        return cached;
      }
      try { return await update; }
      catch {
        return cached || new Response(offlinePage, {status: 503, headers: {"Content-Type": "text/html; charset=utf-8"}});
      }
    })());
    return;
  }
  event.respondWith((async () => {
    const cache = await caches.open(SHELL);
    const cached = await cache.match(req, {ignoreSearch: true});
    const root = new URL(scope);
    if (cached) return cached;
    if (url.pathname === root.pathname && req.mode === "navigate") {
      const index = await cache.match(new URL("./index.html", scope));
      if (index) return index;
    }
    return fetch(req);
  })());
});
'''
    sw = (sw.replace("__BUILD__", digest)
          .replace("__SHELL_FILES__", json.dumps(shell_urls, ensure_ascii=False))
          .replace("__EPISODE_FILES__", json.dumps(episode_urls, ensure_ascii=False)))
    (DEST / "sw.js").write_text(sw, encoding="utf8")
    print(f"Built {len(episodes)} episodes from {SOURCE}. Published files: {len(shell_urls) + len(episode_urls) + 1}")
    assert not any(p.name.casefold() == "index.md" for p in DEST.rglob("*"))


if __name__ == "__main__":
    build()
