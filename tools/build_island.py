#!/usr/bin/env python3
"""由 tools/pages.py ＋ tools/island_meta.py 產生 island/index.html（3D 統計學習知識群島）。冪等。

頁面是「DOM 優先」：四座島的章節列表由這裡直接輸出成語意 HTML，沒有 JS、CDN 失效
或 WebGL 不可用時就是一張可點的 2D 地圖；WebGL 可用時，同一份列表變成 3D 場景旁的快速列表。
Three.js 以 importmap 釘版載入，integrity 涵蓋每一個會被抓的模組；three.module.min.js 內部 import 的
未壓縮 three.core.js 以 importmap 重新對應到 three.core.min.js，四個模組都在 <head> modulepreload。
"""
import html
import json
import re
import struct
import urllib.parse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import island_meta as M  # noqa: E402
import pages as P  # noqa: E402
from paths import ROOT, TEMPLATE  # noqa: E402

OUT = ROOT / "island" / "index.html"
FIG_DIR = ROOT / "island" / "figs"

THREE_VER = "0.186.1"
_CDN = f"https://cdn.jsdelivr.net/npm/three@{THREE_VER}"
THREE_MAIN = f"{_CDN}/build/three.module.min.js"
THREE_ADDONS = f"{_CDN}/examples/jsm/"
# 每一個實際會被瀏覽器抓的檔案都要有雜湊；three.module.min.js 會再 import ./three.core.js，
# 那個是未壓縮版（解析 1.4 MB），所以 CORE_REMAP 把它對應到 three.core.min.js。
# 升版時：下載這四個檔，以 `openssl dgst -sha384 -binary f | openssl base64 -A` 重算。
THREE_SRI = {
    THREE_MAIN: "sha384-EU5UWigB3OuXjAXooUegndJSqYber3YSJHDoMZs6rV96yY/ol/B4W8logw4CKWkA",
    f"{_CDN}/build/three.core.min.js": "sha384-ktZslgpl0L71WZcQ5wKV96Z04i9QSjtmiU/kYpjDQSfJ5NJ8B79qDF63oNTbQySl",
    f"{THREE_ADDONS}controls/OrbitControls.js": "sha384-LSqANrugPGTgf0eYsQTloqKWy926dOOXo2iZ9y6wLMIDEQoU9AaCLJF1Vcc7oJXr",
    f"{THREE_ADDONS}geometries/RoundedBoxGeometry.js": "sha384-gHmgcgYfabbVCqiNiLLSop7dMvxAqZsQsjokoDYKyrHmCD5jCPvDvFaXaAkHtTfM",
}

CORE_REMAP = {f"{_CDN}/build/three.core.js": f"{_CDN}/build/three.core.min.js"}

# 網頁字型只保留頂列標題：用 text= 只下載這幾個字（約 3 KB）；其餘一律用系統中文字型。
# 原本整套 Noto Sans／Serif TC＋JetBrains Mono 約 2.6 MB、40 個請求，是網路載入的主要負擔。
TITLE = "統計學習知識群島"
FONTS = ("https://fonts.googleapis.com/css2?family=Noto+Serif+TC:wght@900&display=swap&text="
         + urllib.parse.quote(TITLE))


# 面板上維導的頭像：黏土色的臉、深藍小帽、琥珀色的燈（與 island-scene.js 的 3D 嚮導同色）
GUIDE_FACE = ('<circle cx="24" cy="24" r="23" fill="#e7f0ea"/>'
              '<circle cx="22" cy="27" r="11" fill="#f1c9a5"/>'
              '<path d="M10 22 Q22 8 34 22 Z" fill="#2c3e7a"/><rect x="8" y="20.5" width="28" height="3.2" rx="1.6" fill="#22306a"/>'
              '<circle cx="18.5" cy="27.5" r="1.4" fill="#2b2420"/><circle cx="25.5" cy="27.5" r="1.4" fill="#2b2420"/>'
              '<path d="M19 32 Q22 34.5 25 32" stroke="#a5553d" stroke-width="1.4" fill="none" stroke-linecap="round"/>'
              '<path d="M38 22 V27" stroke="#5a4636" stroke-width="1.4"/><rect x="34.5" y="27" width="7" height="9" rx="2" fill="#f2b84b"/>'
              '<rect x="34" y="26" width="8" height="2" rx="1" fill="#5a4636"/>')


def esc(s: str) -> str:
    return html.escape(s, quote=True)


def check_meta():
    """island_meta 與 PAGES 必須一一對應；refs 只能指向先備頁。"""
    stems = [p.stem for p in P.PAGES]
    missing = [s for s in stems if s not in M.META]
    extra = [s for s in M.META if s not in P.BY_STEM]
    errs = []
    if missing:
        errs.append(f"island_meta 缺頁：{', '.join(missing)}")
    if extra:
        errs.append(f"island_meta 多出不存在的頁：{', '.join(extra)}")
    for stem, m in M.META.items():
        for k in ("landmark", "blurb"):
            if not m.get(k):
                errs.append(f"{stem} 缺 {k}")
        for r in m.get("refs", []):
            q = P.BY_STEM.get(r)
            if q is None:
                errs.append(f"{stem} 的 refs 指向不存在的 {r}")
            elif q.grp not in ("statistics", "appendix"):
                errs.append(f"{stem} 的 refs 只能指向先備頁，{r} 屬於 {q.grp}")
    for stem in stems:
        if not M.GUIDE.get(stem):
            errs.append(f"{stem} 缺維導的導覽詞（GUIDE）")
    for stem in set(M.GUIDE) - set(stems):
        errs.append(f"GUIDE 多出不存在的頁：{stem}")
    for p in P.PAGES:
        f = M.FIGS.get(p.stem)
        if p.grp == "core" and not f:
            errs.append(f"正課 {p.stem} 缺代表圖（FIGS）")
        if not f:
            continue
        if p.grp != "core":
            errs.append(f"FIGS 只放正課章節，{p.stem} 屬於 {p.grp}")
        elif not re.search(rf'id="{re.escape(f["fig"])}"', (ROOT / p.file).read_text(encoding="utf-8")):
            errs.append(f"{p.file} 裡沒有 id=\"{f['fig']}\"（FIGS 的深連結會失效）")
        elif not (FIG_DIR / f"{p.stem}.webp").exists():
            errs.append(f"缺縮圖 island/figs/{p.stem}.webp：跑 node tools/build_island_figs.js {p.stem}")
    for r in M.TOUR["routes"]:
        for s in r["stems"]:
            if s not in P.BY_STEM:
                errs.append(f"導覽路線 {r['key']} 指向不存在的 {s}")
    grps = {p.grp for p in P.PAGES}
    if grps != set(M.ISLES):
        errs.append(f"ISLES 的鍵 {sorted(M.ISLES)} ≠ PAGES 的分區 {sorted(grps)}")
    if errs:
        raise SystemExit("island_meta 與 pages.py 不一致：\n  " + "\n  ".join(errs))


CODE = {"core": lambda i: f"{i:02d}", "pre": lambda i: chr(64 + i),
        "statistics": lambda i: f"S{i}", "appendix": lambda i: f"P{i}"}


def webp_size(path: Path) -> tuple:
    """讀 WebP 檔頭的寬高（VP8／VP8L／VP8X），給 <img> 的 width/height 屬性，避免載入時版面跳動。"""
    b = path.read_bytes()[:30]
    kind = b[12:16]
    if kind == b"VP8 ":
        w, h = struct.unpack("<HH", b[26:30])
        return w & 0x3FFF, h & 0x3FFF
    if kind == b"VP8L":
        v = int.from_bytes(b[21:25], "little")
        return (v & 0x3FFF) + 1, ((v >> 14) & 0x3FFF) + 1
    if kind == b"VP8X":
        return int.from_bytes(b[24:27], "little") + 1, int.from_bytes(b[27:30], "little") + 1
    raise SystemExit(f"{path} 不是可辨識的 WebP")


def fig_record(p) -> dict | None:
    f = M.FIGS.get(p.stem)
    if not f:
        return None
    w, h = webp_size(FIG_DIR / f"{p.stem}.webp")
    return dict(src=f"figs/{p.stem}.webp", w=w, h=h, caption=f["caption"], href=f"../{p.file}#{f['fig']}")


def records():
    """依 PAGES 字面值順序；seq 是區內序號（不用 Page.n，它與顯示順序脫鉤）。"""
    out, seen = [], {}
    for p in P.PAGES:
        seen[p.grp] = seen.get(p.grp, 0) + 1
        m = M.META[p.stem]
        out.append(dict(stem=p.stem, grp=p.grp, seq=seen[p.grp], code=CODE[p.grp](seen[p.grp]),
                        title=p.plain,
                        label=p.islp_label, landmark=m["landmark"], blurb=m["blurb"],
                        refs=list(m.get("refs", [])), href=f"../{p.file}",
                        guide=M.GUIDE[p.stem], fig=fig_record(p)))
    return out


# 沒有 hero_svg 的頁（統計附錄）用一條常態曲線當 2D 卡片圖示
BELL = ('<path d="M20 230 C90 230 110 50 160 50 C210 50 230 230 300 230" fill="none" stroke="#fff" '
        'stroke-width="10" opacity=".9"/><path d="M20 244 H300" stroke="#fff" stroke-width="6" opacity=".55"/>')


def item(r: dict, p: P.Page) -> str:
    refs = ""
    if r["refs"]:
        names = "、".join(esc(P.BY_STEM[s].plain) for s in r["refs"])
        refs = f'            <span class="isl-refs">需要時可查閱：{names}</span>\n'
    return (f'        <li class="isl-item" data-stem="{r["stem"]}" data-grp="{r["grp"]}">\n'
            f'          <a class="isl-link" href="{esc(r["href"])}" data-stem="{r["stem"]}">\n'
            f'            <svg class="isl-icon" viewBox="0 0 320 280" aria-hidden="true">{p.hero_svg or BELL}</svg>\n'
            f'            <span class="isl-num">{r["code"]}</span>\n'
            f'            <span class="isl-title">{esc(r["title"])}</span>\n'
            f'            <span class="isl-landmark">{esc(r["landmark"])}</span>\n'
            f'            <span class="isl-blurb">{esc(r["blurb"])}</span>\n'
            f'{refs}'
            f'            <span class="isl-state" aria-hidden="true"></span>\n'
            f'          </a>\n'
            f'        </li>')


def isle_section(grp: str, recs: list) -> str:
    isle = M.ISLES[grp]
    rows = "\n".join(item(r, P.BY_STEM[r["stem"]]) for r in recs if r["grp"] == grp)
    return (f'    <section class="isle isle-{grp}" id="isle-{grp}" data-grp="{grp}" aria-labelledby="isle-{grp}-h">\n'
            f'      <h2 id="isle-{grp}-h"><span class="isle-name">{esc(isle["name"])}</span>'
            f'<span class="isle-sub">{esc(isle["sub"])}</span></h2>\n'
            f'      <p class="isle-note">{esc(isle["note"])}</p>\n'
            f'      <ol class="isl-items">\n{rows}\n      </ol>\n'
            f'    </section>')


def build() -> str:
    check_meta()
    recs = records()
    css = (TEMPLATE / "island.css").read_text(encoding="utf-8").rstrip()
    # UI 層與場景層 inline 進同一個 module（共用頂層名稱）
    js = "\n\n".join((TEMPLATE / f).read_text(encoding="utf-8").rstrip() for f in ("island.js", "island-scene.js"))
    data = dict(isles=[dict(grp=g, **v) for g, v in M.ISLES.items()], pages=recs, tour=M.TOUR)
    data_json = json.dumps(data, ensure_ascii=False, indent=1).replace("</", "<\\/")
    importmap = json.dumps({"imports": {"three": THREE_MAIN, "three/addons/": THREE_ADDONS, **CORE_REMAP},
                            "integrity": THREE_SRI}, indent=1)
    preload = "\n".join(f'<link rel="modulepreload" href="{u}" integrity="{h}" crossorigin="anonymous">'
                         for u, h in THREE_SRI.items())
    sections = "\n".join(isle_section(g, recs) for g in M.ISLES)
    jumps = "\n".join(f'      <button type="button" class="isl-jump-btn" data-grp="{g}">{esc(v["name"])}</button>'
                      for g, v in M.ISLES.items())
    n_core = sum(1 for r in recs if r["grp"] == "core")
    return f"""<!DOCTYPE html>
<!-- 產物：由 tools/build_island.py 產生，不要手改。文案在 tools/island_meta.py，樣式與程式在 tools/template/island.*、island-scene.js -->
<html lang="zh-Hant">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="description" content="統計學習知識群島：以 3D 群島導覽 NSYSU MATH524 統計學習自學網站的 {len(recs)} 個單元，點選建築即可前往原教材。">
<title>統計學習知識群島 — Statistical Learning Archipelago</title>
<script>
/* 有 WebGL 的瀏覽器先排 3D 版面並顯示載入中，避免 2D 卡片閃一下再切換；失敗時 island.js 會移除 */
if (window.WebGLRenderingContext) document.documentElement.classList.add('gl-pending');
</script>
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="{FONTS}" rel="stylesheet">
<style>
{css}
</style>
<script type="importmap">
{importmap}
</script>
{preload}
</head>
<body>
<header class="isl-bar">
  <a class="isl-home" href="../index.html">← 回到章節總覽</a>
  <div class="isl-brand">
    <h1>{TITLE}</h1>
    <span class="isl-brand-en">Statistical Learning Archipelago · NSYSU MATH524</span>
  </div>
  <div class="isl-actions">
    <button type="button" class="isl-btn" id="islReset" hidden>重設視角</button>
    <button type="button" class="isl-btn" id="islClear">清除足跡</button>
  </div>
</header>
<main class="isl-main">
  <div class="isl-stage" id="islStage" hidden>
    <p class="isl-loading" aria-hidden="true">群島載入中…</p>
    <canvas id="islCanvas" tabindex="0" aria-label="3D 群島：拖曳旋轉、滾輪縮放、點選建築；也可用右側列表操作"></canvas>
    <div class="isl-jumps" role="group" aria-label="跳到島嶼">
{jumps}
    </div>
    <div class="isl-labels" id="islLabels"></div>
    <button type="button" class="isl-bubble" id="islBubble" hidden>{esc(M.TOUR["hello"])}</button>
    <button type="button" class="isl-night" id="islNight" aria-pressed="false">入夜</button>
    <p class="isl-hint" aria-hidden="true">拖曳旋轉 · 滾輪或雙指縮放 · 點島或標籤</p>
  </div>
  <nav class="isl-list" id="islList" aria-label="群島章節列表">
    <p class="isl-intro">四座島、{len(recs)} 個單元，全部可以自由進入。主島的 {n_core} 章依授課順序排列；
      其他三座島是選讀，需要時再查閱。<span class="isl-trail-note">「足跡」只存在這台裝置的瀏覽器裡。</span></p>
{sections}
  </nav>
  <aside class="isl-panel" id="islPanel" hidden aria-labelledby="islPanelTitle">
    <button type="button" class="isl-panel-close" id="islPanelClose" aria-label="關閉">×</button>
    <div class="isl-guide" id="islGuide" hidden>
      <svg class="isl-guide-face" viewBox="0 0 48 48" aria-hidden="true">{GUIDE_FACE}</svg>
      <div class="isl-guide-body">
        <div class="isl-guide-who"><b>{esc(M.TOUR["name"])}</b><span id="islGuideStep"></span></div>
        <p class="isl-guide-text" id="islGuideText" aria-live="polite"></p>
        <div class="isl-guide-choices" id="islGuideChoices"></div>
      </div>
    </div>
    <div class="isl-panel-page" id="islPanelPage">
    <div class="isl-panel-kicker" id="islPanelKicker"></div>
    <h2 id="islPanelTitle"></h2>
    <div class="isl-panel-landmark" id="islPanelLandmark"></div>
    <p class="isl-panel-blurb" id="islPanelBlurb"></p>
    <figure class="isl-fig" id="islFig" hidden>
      <a class="isl-fig-img" id="islFigLink" href="#"><img id="islFigImg" alt="" loading="lazy" decoding="async"></a>
      <figcaption><span class="isl-fig-h">代表互動圖</span><span id="islFigCap"></span></figcaption>
      <a class="isl-fig-go" id="islFigGo" href="#">去操作這張圖 →</a>
    </figure>
    <div class="isl-panel-refs" id="islPanelRefs" hidden>
      <div class="isl-panel-refs-h">需要時可查閱</div>
      <ul id="islPanelRefList"></ul>
    </div>
    <div class="isl-panel-actions">
      <a class="isl-go" id="islPanelGo" href="#">前往教材 →</a>
      <button type="button" class="isl-done" id="islPanelDone" aria-pressed="false">標記完成</button>
    </div>
    </div>
    <div class="isl-guide-nav" id="islGuideNav" hidden>
      <button type="button" class="isl-btn2" id="islGuidePrev">← 上一站</button>
      <button type="button" class="isl-btn2 is-primary" id="islGuideNext">下一站 →</button>
      <button type="button" class="isl-btn2 is-quiet" id="islGuideEnd">結束導覽</button>
    </div>
  </aside>
</main>
<script type="application/json" id="island-data">
{data_json}
</script>
<script type="module">
{js}
</script>
</body>
</html>
"""


def main():
    out = build()
    OUT.parent.mkdir(exist_ok=True)
    old = OUT.read_text(encoding="utf-8") if OUT.exists() else None
    if old != out:
        OUT.write_text(out, encoding="utf-8")
        print(f"寫入 {OUT.relative_to(ROOT)}（{len(out.encode()) // 1024} KB）")
    else:
        print(f"{OUT.relative_to(ROOT)} 已是最新")


if __name__ == "__main__":
    main()
