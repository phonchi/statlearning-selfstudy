#!/usr/bin/env python3
"""由 tools/pages.py ＋ tools/island_meta.py 產生 island/index.html（3D 統計學習知識群島）。冪等。

頁面是「DOM 優先」：四座島的章節列表由這裡直接輸出成語意 HTML，沒有 JS、CDN 失效
或 WebGL 不可用時就是一張可點的 2D 地圖；WebGL 可用時，同一份列表變成 3D 場景旁的快速列表。
Three.js 以 importmap 釘版載入，integrity 涵蓋每一個會被抓的模組（含 three.core.js）。
"""
import html
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import island_meta as M  # noqa: E402
import pages as P  # noqa: E402
from paths import ROOT, TEMPLATE  # noqa: E402

OUT = ROOT / "island" / "index.html"

THREE_VER = "0.186.1"
_CDN = f"https://cdn.jsdelivr.net/npm/three@{THREE_VER}"
THREE_MAIN = f"{_CDN}/build/three.module.min.js"
THREE_ADDONS = f"{_CDN}/examples/jsm/"
# 每一個實際會被瀏覽器抓的檔案都要有雜湊；three.module.min.js 會再 import ./three.core.js。
# 升版時：下載這三個檔，以 `openssl dgst -sha384 -binary f | openssl base64 -A` 重算。
THREE_SRI = {
    THREE_MAIN: "sha384-EU5UWigB3OuXjAXooUegndJSqYber3YSJHDoMZs6rV96yY/ol/B4W8logw4CKWkA",
    f"{_CDN}/build/three.core.js": "sha384-mdKeCwPEcbDvzaxwhm+MVuLoMou+E7jQqrs4tmu/n8HBYPGI1kZt0MkJxlMR4zFM",
    f"{THREE_ADDONS}controls/OrbitControls.js": "sha384-LSqANrugPGTgf0eYsQTloqKWy926dOOXo2iZ9y6wLMIDEQoU9AaCLJF1Vcc7oJXr",
}

FONTS = ("https://fonts.googleapis.com/css2?family=Noto+Serif+TC:wght@400;700;900"
         "&family=Noto+Sans+TC:wght@300;400;500;700&family=JetBrains+Mono:wght@400;600&display=swap")


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
    grps = {p.grp for p in P.PAGES}
    if grps != set(M.ISLES):
        errs.append(f"ISLES 的鍵 {sorted(M.ISLES)} ≠ PAGES 的分區 {sorted(grps)}")
    if errs:
        raise SystemExit("island_meta 與 pages.py 不一致：\n  " + "\n  ".join(errs))


CODE = {"core": lambda i: f"{i:02d}", "pre": lambda i: chr(64 + i),
        "statistics": lambda i: f"S{i}", "appendix": lambda i: f"P{i}"}


def records():
    """依 PAGES 字面值順序；seq 是區內序號（不用 Page.n，它與顯示順序脫鉤）。"""
    out, seen = [], {}
    for p in P.PAGES:
        seen[p.grp] = seen.get(p.grp, 0) + 1
        m = M.META[p.stem]
        out.append(dict(stem=p.stem, grp=p.grp, seq=seen[p.grp], code=CODE[p.grp](seen[p.grp]),
                        title=p.plain,
                        label=p.islp_label, landmark=m["landmark"], blurb=m["blurb"],
                        refs=list(m.get("refs", [])), href=f"../{p.file}"))
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
    js = (TEMPLATE / "island.js").read_text(encoding="utf-8").rstrip()
    data = dict(isles=[dict(grp=g, **v) for g, v in M.ISLES.items()], pages=recs)
    data_json = json.dumps(data, ensure_ascii=False, indent=1).replace("</", "<\\/")
    importmap = json.dumps({"imports": {"three": THREE_MAIN, "three/addons/": THREE_ADDONS},
                            "integrity": THREE_SRI}, indent=1)
    sections = "\n".join(isle_section(g, recs) for g in M.ISLES)
    jumps = "\n".join(f'      <button type="button" class="isl-jump-btn" data-grp="{g}">{esc(v["name"])}</button>'
                      for g, v in M.ISLES.items())
    n_core = sum(1 for r in recs if r["grp"] == "core")
    return f"""<!DOCTYPE html>
<!-- 產物：由 tools/build_island.py 產生，不要手改。文案在 tools/island_meta.py，樣式與程式在 tools/template/island.* -->
<html lang="zh-Hant">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="description" content="統計學習知識群島：以 3D 群島導覽 NSYSU MATH524 統計學習自學網站的 {len(recs)} 個單元，點選建築即可前往原教材。">
<title>統計學習知識群島 — Statistical Learning Archipelago</title>
<link href="{FONTS}" rel="stylesheet">
<style>
{css}
</style>
<script type="importmap">
{importmap}
</script>
</head>
<body>
<header class="isl-bar">
  <a class="isl-home" href="../index.html">← 回到章節總覽</a>
  <div class="isl-brand">
    <h1>統計學習知識群島</h1>
    <span class="isl-brand-en">Statistical Learning Archipelago · NSYSU MATH524</span>
  </div>
  <div class="isl-actions">
    <button type="button" class="isl-btn" id="islReset" hidden>重設視角</button>
    <button type="button" class="isl-btn" id="islClear">清除足跡</button>
  </div>
</header>
<main class="isl-main">
  <div class="isl-stage" id="islStage" hidden>
    <canvas id="islCanvas" tabindex="0" aria-label="3D 群島：拖曳旋轉、滾輪縮放、點選建築；也可用右側列表操作"></canvas>
    <div class="isl-jumps" role="group" aria-label="跳到島嶼">
{jumps}
    </div>
    <div class="isl-tip" id="islTip" aria-hidden="true"></div>
    <p class="isl-hint" aria-hidden="true">拖曳旋轉 · 滾輪或雙指縮放 · 點選建築</p>
  </div>
  <nav class="isl-list" id="islList" aria-label="群島章節列表">
    <p class="isl-intro">四座島、{len(recs)} 個單元，全部可以自由進入。主島的 {n_core} 章依授課順序排列；
      其他三座島是選讀，需要時再查閱。<span class="isl-trail-note">「足跡」只存在這台裝置的瀏覽器裡。</span></p>
{sections}
  </nav>
  <aside class="isl-panel" id="islPanel" hidden aria-labelledby="islPanelTitle">
    <button type="button" class="isl-panel-close" id="islPanelClose" aria-label="關閉">×</button>
    <div class="isl-panel-kicker" id="islPanelKicker"></div>
    <h2 id="islPanelTitle"></h2>
    <div class="isl-panel-landmark" id="islPanelLandmark"></div>
    <p class="isl-panel-blurb" id="islPanelBlurb"></p>
    <div class="isl-panel-refs" id="islPanelRefs" hidden>
      <div class="isl-panel-refs-h">需要時可查閱</div>
      <ul id="islPanelRefList"></ul>
    </div>
    <div class="isl-panel-actions">
      <a class="isl-go" id="islPanelGo" href="#">前往教材 →</a>
      <button type="button" class="isl-done" id="islPanelDone" aria-pressed="false">標記完成</button>
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
