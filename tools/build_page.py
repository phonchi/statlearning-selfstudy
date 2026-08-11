#!/usr/bin/env python3
"""產生／更新十章頁面的骨架。冪等。

只重繪 <!-- GEN:BEGIN k --> … <!-- GEN:END k --> 之間的內容：
head、float-nav、hero、study-guide、TOC、每一節的標題列、chapter-nav、footer、共用 JS。
手寫的 section 內文與本頁元件 JS 完全不動。

所以三處顯示編號（.fn-num / .toc-num / .section-number）與 prev/next 鏈
不可能不同步——它們都是 tools/pages.py 那張表的純函數。

用法：
  python3 tools/build_page.py                # 全部（新檔建骨架，舊檔只重繪 GEN 區段）
  python3 tools/build_page.py linear_regression
  python3 tools/build_page.py --force        # 砍掉重建（會失去手寫內容，請先 commit）
"""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import pages as P  # noqa: E402
from paths import ROOT, TEMPLATE  # noqa: E402

BEGIN = "<!-- GEN:BEGIN {k} -->"
END = "<!-- GEN:END {k} -->"


def gen(k, body):
    return f"{BEGIN.format(k=k)}\n{body}\n{END.format(k=k)}"


def read_tpl(name):
    return (TEMPLATE / name).read_text(encoding="utf-8").rstrip("\n")


# ── 各 GEN 區段 ─────────────────────────────────────────────────────────
def head(p: P.Page) -> str:
    css = read_tpl("base.css") + "\n\n" + read_tpl("stats.css")
    return f"""<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="description" content="{p.plain} — {p.title_en} 互動自學頁。{p.subtitle}。NSYSU MATH524 統計學習與資料探勘。">
<title>{p.plain} — {p.title_en} Interactive（Python）</title>
<script>
  MathJax = {{ tex: {{ inlineMath: [['$','$']], displayMath: [['$$','$$']] }},
             options: {{ skipHtmlTags: ['script','noscript','style','textarea','pre','code'] }} }};
</script>
<script id="MathJax-script" async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
<link href="https://fonts.googleapis.com/css2?family=Noto+Serif+TC:wght@400;700;900&family=Noto+Sans+TC:wght@300;400;500;700&family=JetBrains+Mono:wght@400;600&display=swap" rel="stylesheet">
<script src="https://cdn.jsdelivr.net/npm/chart.js@{P.CHARTJS_VER}/dist/chart.umd.min.js"
        integrity="{P.CHARTJS_SRI}" crossorigin="anonymous"></script>
<style>
{css}
</style>
</head>"""


def floatnav(p: P.Page) -> str:
    rows = []
    for s, tok, _ in P.tokens(p):
        rows.append(f'  <a href="#{s.id}" data-target="{s.id}">'
                    f'<span class="fn-num">{tok}</span><span class="fn-name">{s.short}</span></a>')
    body = "\n".join(rows)
    return (f'<nav class="float-nav" id="floatNav" aria-label="章節導覽">\n'
            f'  <div class="fn-title">章節導覽</div>\n{body}\n'
            f'  <a href="#top" class="fn-top" title="回到頂端"><span class="fn-num">↑ TOP</span></a>\n'
            f'</nav>')


def hero(p: P.Page) -> str:
    return f"""<div class="hero" id="top">
  <div class="hero-grid"></div>
  <svg class="hero-graph" width="320" height="280" viewBox="0 0 320 280" aria-hidden="true">
{p.hero_svg}
  </svg>
  <div class="hero-content">
    <h1>{p.h1}</h1>
    <div class="subtitle">{p.subtitle}</div>
    <div class="big-formula">{p.formula}</div>
    <div class="scroll-hint">向下捲動開始互動<span>↓</span></div>
  </div>
</div>"""


def studyguide(p: P.Page) -> str:
    pills = [
        (f"📑 講義 {p.deck_no} PDF", p.blob + p.deck.replace(" ", "%20")),
        (f"📓 Ch{p.islp:02d} 中文 Lab", p.blob + p.lab.replace(" ", "%20")),
    ]
    for i, pl in enumerate(p.playlist.split(",")):
        label = "▶ 課程錄影" if i == 0 else f"▶ 課程錄影 {i + 1}"
        pills.append((label, f"https://www.youtube.com/playlist?list={pl}"))
    pills.append(("📖 ISLP 原書", P.BOOK_ISLP))
    if p.esl_label:
        pills.append(("📗 ESL 原書", P.BOOK_ESL))
    links = "".join(f'<a href="{u}" target="_blank" rel="noopener">{t}</a>' for t, u in pills)
    links += '<a href="index.html">🏠 章節總覽</a>'
    esl_hint = ("標「ESL 進階」的節是課堂沒細講的延伸，第一輪可略過。"
                if any(s.eslx for s in p.secs) else "")
    return f"""<div class="study-guide">
  <div class="sg-title">📌 本頁使用方式（{p.islp_label}｜講義 {p.deck_no}）</div>
  <p>① <strong>照節次讀</strong>：每節先讀說明，動手玩互動元件——<em>先預測結果，再按按鈕驗證</em>。
  ② <strong>對照講義</strong>：每個 §徽章都標了 ISLP 節號與講義頁碼，細節與完整推導請回講義與課本。
  ③ <strong>每節做 quiz</strong>：答錯就回到該節重讀，不要往下跳；錯的選項也寫了「錯在哪」。
  ④ 最後翻<a href="#cards">關鍵詞彙卡</a>自測術語，並用 <a href="#reference">REF 總覽</a>當速查表。{esl_hint}</p>
  <div class="sg-links">{links}</div>
</div>"""


def toc(p: P.Page) -> str:
    rows = [f'    <a href="#{s.id}"><span class="toc-num">{tok}</span>{s.short}</a>'
            for s, tok, _ in P.tokens(p)]
    return ('<div class="toc">\n  <div class="toc-title">CONTENTS · 內容目錄</div>\n'
            '  <div class="toc-grid">\n' + "\n".join(rows) + "\n  </div>\n</div>")


def sec_head(p: P.Page, s: P.Sec, number: str) -> str:
    badges = "".join(f'<span class="sec-badge">{b.strip()}</span>'
                     for b in s.badge.split("|") if b.strip())
    eslx = '<span class="eslx">ESL 進階</span>' if s.eslx else ""
    h2 = f'  <h2>{s.h2} {badges}{eslx}</h2>' if s.h2 else ""
    out = f'  <div class="section-number">{number}</div>'
    if h2:
        out += "\n" + h2
    return out


def stub_body(p: P.Page, s: P.Sec) -> str:
    """新建頁面時放的佔位內容。撰寫時整段換掉。"""
    return f'  <p class="skip-note">TODO 待撰寫：{s.short}（{s.badge}）</p>'


def ex_head(p: P.Page) -> str:
    links = P.sol_links(p.islp)
    pills = "".join(f'<a href="{u}" target="_blank" rel="noopener">{t}</a>' for t, u in links)
    # ISLP 第 1 章沒有課後習題，所以這一頁的練習改成概念自測
    if p.islp == 1:
        return f"""  <div class="section-number">EXERCISES · 練習</div>
  <h2>動手驗證：概念自測 <span class="sec-badge">ISLP Ch.1</span></h2>
  <p>ISLP 第 1 章沒有課後習題，所以這幾題是照本章觀念設計的。先自己想過再點選項；
  每個選項——<strong>包含錯的</strong>——都寫了為什麼。第 2 章開始就有課本習題可以對答案了。</p>
  <div class="sol-links">{pills}</div>"""
    n_site = len(links)
    return f"""  <div class="section-number">EXERCISES · 練習</div>
  <h2>動手驗證：ISLP 第 {p.islp} 章精選題 <span class="sec-badge">ISLP §{P.EX_SEC[p.islp]} 習題</span></h2>
  <p>下面幾題取自 ISLP §{P.EX_SEC[p.islp]} 的課後習題，題號都對得回課本。先自己想過再點選項；
  每個選項——<strong>包含錯的</strong>——都寫了為什麼。想看完整解答再對照下面{n_site}個站。</p>
  <div class="sol-links">{pills}</div>"""


def data_count(kind: str, p: P.Page) -> int:
    """data/<kind>_zh/ch<ISLP 章號>.json 的張數／題數；還沒寫就回 0。"""
    f = ROOT / "data" / f"{kind}_zh" / f"ch{p.islp}.json"
    if not f.exists():
        return 0
    try:
        return len(json.loads(f.read_text(encoding="utf-8")))
    except json.JSONDecodeError:
        return 0


def cards_block(p: P.Page) -> str:
    n = data_count("flashcards", p)
    badge = f"課程題庫 · {n} 張" if n else "課程題庫 · 待注入"
    return f"""  <div class="section-number">CARDS · 關鍵詞彙卡</div>
  <h2>關鍵詞彙卡：點卡片翻面 <span class="sec-badge">{badge}</span></h2>
  <p>詞彙卡取自本章講義與 ISLP 第 {p.islp} 章，正面是中文術語（附英文原名）。
  先看正面、心裡默想定義，再翻面對答案；洗牌後再過一輪，直到每張都能不看答案講出來。</p>
  <div class="fc-controls">
    <button id="fcShuffle">🔀 洗牌</button>
    <button id="fcFlipAll">全部翻面</button>
    <button id="fcUnflip">全部翻回</button>
  </div>
  <div class="fc-grid" id="fcGrid"></div>"""


def bankquiz_head(p: P.Page) -> str:
    n = data_count("questions", p)
    badge = f"課程題庫 ch{p.islp} · {n} 題" if n else "課程題庫 · 待注入"
    return (f'  <div class="section-number">QUIZ · 自我檢測</div>\n'
            f'  <h2>本章自我檢測 <span class="sec-badge">{badge}</span></h2>\n'
            f'  <p>這些題目取自課程題庫，只給對錯與說明，不計分。答錯就回到對應章節重讀。</p>')


def chapternav(p: P.Page) -> str:
    prev, nxt = P.neighbours(p)
    a = (f'<a class="prev" href="{prev.file}"><div class="nav-dir">◂ 上一章</div>'
         f'<div class="nav-title">{prev.plain}</div></a>') if prev else "<span></span>"
    b = ('<a class="home" href="index.html"><div class="nav-dir">INDEX</div>'
         '<div class="nav-title">章節總覽</div></a>')
    c = (f'<a class="next" href="{nxt.file}"><div class="nav-dir">下一章 ▸</div>'
         f'<div class="nav-title">{nxt.plain}</div></a>') if nxt else "<span></span>"
    return f'<div class="chapter-nav">{a}{b}{c}</div>'


def footer(p: P.Page) -> str:
    book = "An Introduction to Statistical Learning with Applications in Python (ISLP)"
    return f"""<footer>
  互動式{p.plain}教學 · 基於 {book} 第 {p.islp} 章與 NSYSU MATH524 課程講義<br>
  <span style="font-family:'JetBrains Mono',monospace;font-size:.78rem;color:var(--accent3);">Designed for NSYSU · Interactive Python self-study</span>
</footer>"""


def sharedjs(p: P.Page) -> str:
    return "<script>\n" + read_tpl("shared.js") + "\n</script>"


# ── 組裝 ────────────────────────────────────────────────────────────────
def render_new(p: P.Page) -> str:
    parts = ["<!DOCTYPE html>", '<html lang="zh-Hant">', gen("head", head(p)), "<body>",
             gen("floatnav", floatnav(p)), gen("hero", hero(p)), '<div class="container">',
             gen("studyguide", studyguide(p)), gen("toc", toc(p))]
    for s, tok, number in P.tokens(p):
        if s.id == "exercises":
            inner = gen(f"sec:{s.id}", ex_head(p)) + "\n  <!-- 練習題 quiz-box 寫在這裡 -->"
        elif s.id == "cards":
            inner = gen(f"sec:{s.id}", cards_block(p))
        elif s.id == "reference":
            inner = (gen(f"sec:{s.id}",
                         '  <div class="section-number">REFERENCE · 總覽</div>\n'
                         f'  <h2>{p.plain}速查表 <span class="sec-badge">{p.islp_label}</span></h2>')
                     + "\n  <!-- 比較表、重點回顧、.ver-note 寫在這裡 -->")
        elif s.id == "bankquiz":
            inner = gen(f"sec:{s.id}", bankquiz_head(p)) + '\n  <div id="bqBox"></div>'
        else:
            inner = gen(f"sec:{s.id}", sec_head(p, s, number)) + "\n" + stub_body(p, s)
        parts.append(f'<section id="{s.id}">\n{inner}\n</section>')
    parts += [gen("chapternav", chapternav(p)), "</div>", gen("footer", footer(p)),
              gen("sharedjs", sharedjs(p)),
              "<!-- PAGEJS:BEGIN -->", "<script>",
              f"/* ===== {p.stem} 本頁元件（id 與全域一律用 w{p.n:02d} 前綴） ===== */",
              f"HC.ready(() => {{ /* TODO w{p.n:02d} 元件 */ }});",
              "HC.initFlashcards();", "</script>", "<!-- PAGEJS:END -->",
              "<!-- DATA:BEGIN -->", "<!-- DATA:END -->",
              "</body></html>"]
    return "\n".join(parts) + "\n"


def refresh(p: P.Page, src: str):
    """只重繪 GEN 區段；回報哪些區段變了、哪些 section 還沒有。"""
    changed, missing = [], []
    regions = {"head": head(p), "floatnav": floatnav(p), "hero": hero(p),
               "studyguide": studyguide(p), "toc": toc(p),
               "chapternav": chapternav(p), "footer": footer(p), "sharedjs": sharedjs(p)}
    for s, tok, number in P.tokens(p):
        if s.id == "exercises":
            regions[f"sec:{s.id}"] = ex_head(p)
        elif s.id == "cards":
            regions[f"sec:{s.id}"] = cards_block(p)
        elif s.id == "reference":
            regions[f"sec:{s.id}"] = ('  <div class="section-number">REFERENCE · 總覽</div>\n'
                                      f'  <h2>{p.plain}速查表 '
                                      f'<span class="sec-badge">{p.islp_label}</span></h2>')
        elif s.id == "bankquiz":
            regions[f"sec:{s.id}"] = bankquiz_head(p)
        else:
            regions[f"sec:{s.id}"] = sec_head(p, s, number)

    for k, body in regions.items():
        pat = re.compile(re.escape(BEGIN.format(k=k)) + r".*?" + re.escape(END.format(k=k)), re.S)
        if not pat.search(src):
            missing.append(k)
            continue
        new = gen(k, body)
        src2 = pat.sub(lambda _m: new, src, count=1)
        if src2 != src:
            changed.append(k)
        src = src2

    order = [m.group(1) for m in re.finditer(r'<section id="([^"]+)"', src)]
    want = [s.id for s, _, _ in P.tokens(p)]
    if order != want:
        missing.append(f"section 順序不符：檔案 {order} ≠ 表 {want}")
    return src, changed, missing


def build(p: P.Page, force=False):
    dest = ROOT / p.file
    if force or not dest.exists():
        dest.write_text(render_new(p), encoding="utf-8")
        print(f"  {p.file:34s} 新建骨架（{len(P.tokens(p))} 節）")
        return
    src = dest.read_text(encoding="utf-8")
    out, changed, missing = refresh(p, src)
    if out != src:
        dest.write_text(out, encoding="utf-8")
    note = f"重繪 {len(changed)} 區段" if changed else "無變化"
    print(f"  {p.file:34s} {note}" + (f"  ⚠ {missing}" if missing else ""))


def main(argv):
    force = "--force" in argv
    names = [a for a in argv if not a.startswith("--")]
    targets = [P.BY_STEM[n] for n in names] if names else P.PAGES
    for p in targets:
        build(p, force=force)


if __name__ == "__main__":
    main(sys.argv[1:])
